import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';
import { getCookie, removeCookie } from '../utils/cookies';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const refreshToken = getCookie('refresh');
      if (refreshToken) {
        try {
          const response = await authService.reissueToken();
          if (response.success) {
            setAccessToken(response.accessToken);
            setUser(response.user);
          }
        } catch (error) {
          console.error('토큰 재발급 실패:', error);
          removeCookie('refresh');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);
      if (response.success) {
        setAccessToken(response.accessToken);
        setUser(response.user);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: '로그인 중 오류가 발생했습니다.' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      return response;
    } catch (error) {
      return { success: false, message: '회원가입 중 오류가 발생했습니다.' };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('로그아웃 오류:', error);
    } finally {
      setAccessToken(null);
      setUser(null);
      removeCookie('refresh');
    }
  };

  const value = {
    user,
    accessToken,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!accessToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};