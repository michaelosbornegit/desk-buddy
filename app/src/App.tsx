import { Grow, ThemeProvider } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { AuthProvider, RequireAuth } from './components/AuthProvider';
import NavBar from './components/NavBar';
import Home from './pages/Home/Home';
import Login from './pages/Login/Login';
import Register from './pages/Login/Register';
import MessageHistory from './pages/Messaging/MessageHistory';
import SendMessage from './pages/Messaging/SendMessage';
import theme from './theme';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <SnackbarProvider maxSnack={3} autoHideDuration={6000} TransitionComponent={Grow}>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/" element={<NavBar />}>
                <Route path="/" element={<Navigate to="/home" replace />} />
                <Route
                  path="/home"
                  element={
                    <RequireAuth>
                      <Home />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/send-message"
                  element={
                    <RequireAuth>
                      <SendMessage />
                    </RequireAuth>
                  }
                />
                <Route
                  path="/message-history"
                  element={
                    <RequireAuth>
                      <MessageHistory />
                    </RequireAuth>
                  }
                />
                {/* <Route
                  path="/configure-buddy"
                  element={
                    <RequireAuth>
                      <Home />
                    </RequireAuth>
                  }
                /> */}
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              <Route path="*" element={<Navigate to="/home" replace />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  );
}
