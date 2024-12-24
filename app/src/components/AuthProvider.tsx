import styled from '@emotion/styled';
import { CircularProgress } from '@mui/material';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import { User } from '../types/users';
import { userCheckLogin, userLogout, userRegister } from 'services/user';

interface AuthContextType {
  currentUser: User | null;
  register: (displayName: string, deviceCode: string) => void;
  logout: () => void;
  initialized: boolean;
}

const SpinnerContainer = styled('div')({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  height: 'calc(100vh - 64px)',
});

export const AuthContext = createContext<AuthContextType | null>(null);

// TODO fix this, better ways to do it in react 18
interface Props {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    const checkLogin = async () => {
      const loggedIn = await userCheckLogin();

      if (loggedIn.status === 401) {
        setLoading(false);
      } else {
        const user = await loggedIn.json();
        setCurrentUser(user);
      }

      setLoading(false);
      setInitialized(true);
    };
    checkLogin();
  }, []);

  const register = async (email: string, password: string) => {
    const response = await userRegister(email, password);
    if (response.status === 200) {
      const user = await response.json();
      setCurrentUser(user);
    } else {
      throw new Error('Error logging in');
    }
  };

  // Function to log out the user
  const logout = async () => {
    const response = await userLogout();
    if (response.status === 200) {
      setCurrentUser(null);
    }

    // TODO handle response if there is an error logging out
  };

  // Render loading state while checking for authentication
  // TODO maybe do something while loading? Idk I think I prefer to only do something
  // if logging in fails and otherwise have it happen in the background
  if (loading) {
    return (
      <SpinnerContainer>
        <CircularProgress />
      </SpinnerContainer>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        register,
        logout,
        initialized,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext easily in functional components
export const useAuth = (): AuthContextType => {
  const authContext = useContext(AuthContext);
  if (!authContext) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return authContext;
};

export const RequireAuth: React.FC<Props> = ({ children }) => {
  const { currentUser, initialized } = useAuth();

  if (!initialized) {
    return <CircularProgress />;
  }

  if (initialized && !currentUser) {
    return <Navigate to="/register" replace />;
  }

  return <>{children}</>;
};
