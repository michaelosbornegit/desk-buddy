import { enrichedFetch } from './api';

export const userCheckLogin = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/devices/login`, {}, false, false);
};

export const userRegister = (pairingCode: string, displayName?: string, forceAssociate = true) => {
  return enrichedFetch(
    `${import.meta.env.VITE_API_HOST}/devices/login`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pairingCode,
        displayName,
        forceAssociate,
      }),
    },
    false,
    false
  );
};

export const userLogout = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/devices/logout`, undefined, false, false);
};
