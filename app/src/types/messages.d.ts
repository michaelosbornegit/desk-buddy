export type CreateMessage = {
  to: string[];
  message: string;
};

export type Message = SendMessage & {
  from: string;
  message: string;
  createdAt: string;
};
