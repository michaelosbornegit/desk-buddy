import { AppBar, Button, Toolbar, Typography } from '@mui/material';
import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

const NavBar = (): JSX.Element => {
  const navigate = useNavigate();

  return (
    <>
      <AppBar position="static" sx={{ marginBottom: '16px', width: '100vw' }} color="secondary">
        <Toolbar>
          <div onClick={() => navigate('/home')}>
            <Typography variant="h6">🤖 Desk Buddy</Typography>
          </div>
        </Toolbar>
      </AppBar>
      <Outlet />
    </>
  );
};

export default NavBar;
