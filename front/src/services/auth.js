import { api } from './api';

export const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/login', {
        username,
        password
      }, {
        withCredentials: true
      });

      const accessToken = response.headers.access;
      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
        return {
          success: true,
          accessToken,
          user: { username }
        };
      }

      return { success: false, message: '로그인에 실패했습니다.' };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || '로그인 중 오류가 발생했습니다.' 
      };
    }
  },

  async register(userData) {
    try {
      await api.post('/join', userData, {
      headers: {
        access: undefined // 헤더 제거
      }
    });
      return { success: true, message: '회원가입이 완료되었습니다.' };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || '회원가입 중 오류가 발생했습니다.' 
      };
    }
  },

  async logout() {
    try {
      await api.post('/logout', {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('로그아웃 오류:', error);
    } finally {
      localStorage.removeItem('accessToken');
    }
  },

  async reissueToken() {
    try {
      const response = await api.post('/reissue', {}, {
        withCredentials: true
      });

      const accessToken = response.headers.access;
      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
        return {
          success: true,
          accessToken,
          user: { username: 'user' } // 실제로는 토큰에서 추출
        };
      }

      return { success: false };
    } catch (error) {
      return { success: false };
    }
  }
};