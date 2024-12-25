export type User = {
  pairingCode: string;
  displayName: string;
  admin: boolean;
};

export type UserRegister = {
  pairingCode: string;
  displayName: string;
  forceAssociate?: boolean;
};

export type UserLogin = Pick<User, 'pairingCode'>;
