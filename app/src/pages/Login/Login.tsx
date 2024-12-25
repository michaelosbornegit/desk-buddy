import styled from '@emotion/styled';
import { Alert, Button, Container, Typography } from '@mui/material';
import { FormApi, SubmissionErrors } from 'final-form';
import { Checkboxes, TextField } from 'mui-rff';
import React, { useEffect, useState } from 'react';
import { Form } from 'react-final-form';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../components/AuthProvider';
import { UserLogin } from '../../types/users';

const PageContainer = styled(Container)({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: 'inherit',
  width: '100%',
});

const Login = (): JSX.Element => {
  const navigate = useNavigate();
  const { register, currentUser } = useAuth();

  useEffect(() => {
    if (currentUser) {
      navigate('/home');
    }
  }, [currentUser, navigate]);

  const onSubmit = async (values: UserLogin) => {
    await register(values.pairingCode);
  };

  return (
    <PageContainer maxWidth="sm">
      <Typography fontSize={'48px'}>🤖</Typography>
      <Typography variant="h4" textAlign={'center'} sx={{ marginBottom: '16px' }}>
        Login
      </Typography>
      <Typography variant="body1" textAlign={'center'} sx={{ marginBottom: '8px' }}>
        First time here?
      </Typography>
      <Button
        variant="contained"
        onClick={() => {
          navigate('/register');
        }}
        fullWidth
        sx={{ marginBottom: '32px' }}
        color="secondary"
      >
        Register My Buddy
      </Button>
      <Typography variant="body1" textAlign={'center'} sx={{ marginBottom: '16px' }}>
        Otherwise, to login enter your pairing code
      </Typography>
      <Form
        onSubmit={onSubmit}
        render={({ handleSubmit, values }) => {
          return (
            <form
              onSubmit={handleSubmit}
              style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}
            >
              <TextField
                label="Pairing Code (case sensitive)"
                name="pairingCode"
                required
                variant="outlined"
              />
              <Alert severity="warning" sx={{ marginBottom: '16px' }}>
                Can&apos;t find your pairing code? It&apos;s in the Desk Buddy menu under Pair Code:{' '}
                <b>hold button -{'>'} Pair Code</b>
              </Alert>
              <Button type="submit" variant="contained" fullWidth>
                Login
              </Button>
            </form>
          );
        }}
      />
    </PageContainer>
  );
};

export default Login;
