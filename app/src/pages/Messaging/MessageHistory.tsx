import styled from '@emotion/styled';
import { Visibility } from '@mui/icons-material';
import { Box, Card, Chip, Container, Typography } from '@mui/material';
import { useSnackbar } from 'notistack';
import React, { useEffect, useState } from 'react';

import { useAuth } from '../../components/AuthProvider';
import { getMessages } from '../../services/message';
import { Message } from '../../types/messages';

const PageContainer = styled(Container)({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  width: '100vw',
});

const MessageHistory = (): JSX.Element => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchMessages = async () => {
      const fetchedMessages = await getMessages();

      setMessages(fetchedMessages);
    };
    fetchMessages();
  }, []);

  const buildMessageCard = (message: Message) => {
    const isSentByCurrentUser = message.from === currentUser?.displayName;

    return (
      <Card
        key={message.createdAt}
        sx={{
          marginBottom: '10px',
          padding: '10px',
          alignSelf: isSentByCurrentUser ? 'flex-end' : 'flex-start',
          minWidth: '75%',
        }}
      >
        <Box display="flex" flexDirection="column">
          <Typography variant="h6">From: {isSentByCurrentUser ? 'You' : message.from}</Typography>
          <Box display="flex">
            <Typography variant="h6">To:</Typography>
            <Box display={'flex'} flexDirection={'row'}>
              {message.to.map((recipient: { to: string; read: boolean }) => {
                if (recipient.to === currentUser?.displayName) {
                  recipient.to = 'You';
                }
                return (
                  <Chip
                    key={recipient.to}
                    label={recipient.to}
                    sx={{ marginLeft: '5px' }}
                    icon={
                      recipient.read ? <Visibility sx={{ height: '15px', width: '15px' }} /> : <></>
                    }
                  />
                );
              })}
            </Box>
          </Box>
        </Box>
        <Typography
          variant="body1"
          whiteSpace={'pre-wrap'} // Allow multi-line wrapping
          fontFamily={'monospace'}
          lineHeight={'1'}
          my={'10px'}
        >
          {message.message}
        </Typography>
        <Typography variant="caption">
          {new Date(`${message.createdAt}Z`).toLocaleString(undefined, {
            year: 'numeric',
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
          })}
        </Typography>
      </Card>
    );
  };

  return (
    <PageContainer maxWidth="sm">
      <Typography variant="h4">Message History</Typography>
      <Box display="flex" flexDirection="column" width="100%">
        {messages.map((message: Message) => {
          return buildMessageCard(message);
        })}
      </Box>
    </PageContainer>
  );
};

export default MessageHistory;
