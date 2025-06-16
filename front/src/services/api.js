import axios from 'axios';
import { getCookie, removeCookie } from '../utils/cookies.js';

const API_BASE_URL = 'http://16.176.121.138:3000/api';

// 기본 axios 인스턴스
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10초
});

// 파일 업로드용 axios 인스턴스
const uploadApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5분
});

// 요청 인터셉터 - ACCESS 토큰 자동 추가
const addTokenInterceptor = (instance) => {
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        config.headers.access = token;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
};

// 응답 인터셉터 - 토큰 만료 시 자동 재발급
const addResponseInterceptor = (instance) => {
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = getCookie('refresh');
          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/reissue`, {}, {
              withCredentials: true
            });

            const newAccessToken = response.headers.access;
            if (newAccessToken) {
              localStorage.setItem('accessToken', newAccessToken);
              originalRequest.headers.access = newAccessToken;
              return instance(originalRequest);
            }
          }
        } catch (refreshError) {
          localStorage.removeItem('accessToken');
          removeCookie('refresh');
          window.location.href = '/login';
        }
      }

      return Promise.reject(error);
    }
  );
};

// 인터셉터 적용
addTokenInterceptor(api);
addTokenInterceptor(uploadApi);
addResponseInterceptor(api);
addResponseInterceptor(uploadApi);

export { api, uploadApi };