import styled from '@emotion/styled';
import { Mail, ManageHistory, Message, Settings, Visibility } from '@mui/icons-material';
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

  return (
    <Container maxWidth="sm">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '32px' }}>
        <Typography>
          Welcome <b>{currentUser?.displayName}</b>
        </Typography>
        <Typography textAlign={'right'}>
          Pairing Code <b>{currentUser?.pairingCode}</b>
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
        view messages
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
        disabled
      >
        customize buddy (coming soon)
      </Button>
      <Button
        variant="contained"
        size="large"
        onClick={() => {
          window.open('https://github.com/michaelosbornegit/desk-buddy/releases', '_blank');
        }}
        fullWidth
        sx={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}
        color="secondary"
        endIcon={<ManageHistory />}
      >
        view change log
      </Button>
      <Alert severity="info" sx={{ marginBottom: '32px' }}>
        Buddy messed up?
        <br />
        <br />
        Plug it in while holding the button to factory reset it. Don&apos;t worry! You won&apos;t
        lose messages or data.
      </Alert>
    </Container>
  );
};

export default Home;
