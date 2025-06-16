import Cookies from 'js-cookie';

export const setCookie = (name, value, options = {}) => {
  const defaultOptions = {
    expires: 30, // 30일
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    ...options
  };

  Cookies.set(name, value, defaultOptions);
};

export const getCookie = (name) => {
  return Cookies.get(name);
};

export const removeCookie = (name) => {
  Cookies.remove(name);
};