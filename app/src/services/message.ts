import { Message } from '../types/messages';
import { enrichedFetch } from './api';

export const messageFetchRecipients = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/messages/get-recipients`);
};

export const sendMessage = (message: Message) => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/messages/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
  });
};

export const getMessages = () => {
  return enrichedFetch(`${import.meta.env.VITE_API_HOST}/messages/get-for-user`);
};
