import styled from '@emotion/styled';
import { Box, Button, Container, TextField, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';

import { getDogDashboard } from '../../services/api';

const PageContainer = styled.div({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  minHeight: 'inherit',
  width: '100%',
});

const Home = (): JSX.Element => {
  const [displayOneMessage, setDisplayOneMessage] = useState<string>('');
  const [displayTwoMessage, setDisplayTwoMessage] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      const dashboard = await getDogDashboard();

      setDisplayOneMessage(dashboard.screen_one.text);
      setDisplayTwoMessage(dashboard.screen_two.text);
    };
    fetchData();
  });

  return (
    <Container maxWidth="lg">
      <PageContainer>
        <Box sx={{ height: '10vh' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '50px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Button variant="contained">button 1</Button>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <Typography variant="caption">Display 1</Typography>
              <TextField
                multiline
                rows={5}
                value={displayOneMessage}
                disabled
                // Make the display behave like raspberry pi OLEDs, they have 16 character width and overflow by clipping
                inputProps={{
                  style: {
                    fontFamily: 'monospace',
                    width: '17ch',
                    whiteSpace: 'pre',
                    overflowX: 'clip',
                  },
                }}
              />
            </div>
            <Button variant="contained">button 2</Button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Button variant="contained">button 3</Button>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <Typography variant="caption">Display 2</Typography>
              <TextField
                multiline
                rows={5}
                value={displayTwoMessage}
                disabled
                // Make the display behave like raspberry pi OLEDs, they have 16 character width and overflow by clipping
                inputProps={{
                  style: {
                    fontFamily: 'monospace',
                    width: '17ch',
                    whiteSpace: 'pre',
                    overflowX: 'clip',
                  },
                }}
              />
            </div>
            <Button variant="contained">button 4</Button>
          </div>
        </div>
      </PageContainer>
    </Container>
  );
};

export default Home;
