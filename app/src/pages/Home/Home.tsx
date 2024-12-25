import styled from '@emotion/styled';
import { Mail, Message, Settings, Visibility } from '@mui/icons-material';
import { Alert, Button, Container, Typography } from '@mui/material';
import React from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../components/AuthProvider';

const PageContainer = styled.div({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  minHeight: 'inherit',
  width: '100%',
});

const Home = (): JSX.Element => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  console.log(currentUser);

  return (
    <Container maxWidth="sm">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '32px' }}>
        <Typography>
          Welcome <b>{currentUser?.displayName}</b>
        </Typography>
        <Typography textAlign={'right'}>
          Desk Buddy <b>{currentUser?.pairingCode}</b>
        </Typography>
      </div>
      <Typography sx={{ marginBottom: '32px' }}>What would you like to do?</Typography>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}></div>
      <Button
        variant="contained"
        size="large"
        onClick={() => {
          navigate('/send-message');
        }}
        fullWidth
        sx={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}
        color="secondary"
        endIcon={<Mail />}
      >
        send a message
      </Button>
      <Button
        variant="contained"
        size="large"
        onClick={() => {
          navigate('/message-history');
        }}
        fullWidth
        sx={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}
        color="secondary"
        endIcon={<Visibility />}
      >
        view read messages
      </Button>
      <Button
        variant="contained"
        size="large"
        onClick={() => {
          navigate('/configure-buddy');
        }}
        fullWidth
        sx={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}
        color="secondary"
        endIcon={<Settings />}
      >
        customize buddy
      </Button>
      <Alert severity="info" sx={{ marginBottom: '32px' }}>
        Buddy messed up?
        <br />
        <br />
        Plug it in while holding the button to factory reset it.
      </Alert>
    </Container>
  );
};

export default Home;
