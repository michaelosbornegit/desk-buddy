export type CreateMessage = {
  to: string[];
  message: string;
  centerLines: boolean;
};

export type Message = SendMessage & {
  from: string;
  message: string;
  createdAt: string;
};
