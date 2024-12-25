import styled from '@emotion/styled';
import { Alert, Button, Container, Typography } from '@mui/material';
import { FormApi, SubmissionErrors } from 'final-form';
import { Checkboxes, TextField } from 'mui-rff';
import React, { useState } from 'react';
import { Form } from 'react-final-form';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../components/AuthProvider';
import { UserRegister } from '../../types/users';

const PageContainer = styled(Container)({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: 'inherit',
  width: '100%',
});

const Register = (): JSX.Element => {
  const [needsOverride, setNeedsOverride] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (values: UserRegister) => {
    await register(values.pairingCode, values.displayName, values.forceAssociate);
    navigate('/home');
  };

  return (
    <PageContainer maxWidth="sm">
      <Typography fontSize={'48px'}>🤖</Typography>
      <Typography variant="h4" textAlign={'center'} sx={{ marginBottom: '16px' }}>
        Register
      </Typography>
      <Form
        onSubmit={onSubmit}
        render={({ handleSubmit, values }) => {
          return (
            <form
              onSubmit={handleSubmit}
              style={{ width: '100%', display: 'flex', flexDirection: 'column' }}
            >
              <TextField
                label="Pairing Code (case sensitive)"
                name="pairingCode"
                required
                variant="outlined"
                sx={{ marginBottom: '16px' }}
              />
              <Alert severity="warning" sx={{ marginBottom: '16px' }}>
                Can&apos;t find your pairing code? It&apos;s in the Desk Buddy menu under Pair Code:{' '}
                <b>hold button -{'>'} Pair Code</b>
              </Alert>
              <Typography variant="body1">
                Pick a display name, this is how others will see you in the app.
              </Typography>
              <TextField
                label="Display Name"
                name="displayName"
                required
                variant="outlined"
                sx={{ marginBottom: '8px' }}
              />
              <Alert severity="info" sx={{ marginBottom: '16px' }}>
                Don&apos;t worry! You can change this by registering your desk buddy again.
              </Alert>

              {needsOverride && (
                <Checkboxes
                  name="options"
                  data={[{ label: 'Override Account?', value: 'forceAssociate' }]}
                />
              )}
              <Button type="submit" variant="contained" fullWidth>
                Register
              </Button>
            </form>
          );
        }}
      />
    </PageContainer>
  );
};

export default Register;
