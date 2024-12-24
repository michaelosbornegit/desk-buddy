import { enrichedFetch } from './api';

export const userCheckLogin = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/users/login`);
};

export const userRegister = (displayName: string, deviceCode: string) => {
  return enrichedFetch(
    `${import.meta.env.VITE_API_HOST}/users/register`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        displayName,
        deviceCode,
      }),
    },
    false,
    false
  );
};

export const userLogout = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/users/logout`, undefined, false, false);
};
