import { AppBar, Button, Toolbar, Typography } from '@mui/material';
import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

import { useAuth } from './AuthProvider';

const NavBar = (): JSX.Element => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  return (
    <>
      <AppBar position="static" sx={{ marginBottom: '16px', width: '100vw' }} color="secondary">
        <Toolbar style={{ display: 'flex', justifyContent: 'space-between' }}>
          <div onClick={() => navigate('/home')}>
            <Typography variant="h6">🤖 Desk Buddy</Typography>
          </div>
          <Button color="inherit" onClick={() => logout()}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Outlet />
    </>
  );
};

export default NavBar;
