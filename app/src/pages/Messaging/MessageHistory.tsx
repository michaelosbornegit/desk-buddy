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
          width: '75%',
        }}
      >
        <Box display="flex" flexDirection="column">
          <Typography>From: {isSentByCurrentUser ? 'You' : message.from}</Typography>
          <Box display="flex">
            <Typography>To:</Typography>
            <Box display={'flex'} flexWrap={'wrap'} alignItems={'flex-end'}>
              {message.to.map((recipient: { to: string; read: boolean }) => {
                if (recipient.to === currentUser?.displayName) {
                  recipient.to = 'You';
                }
                return (
                  <Chip
                    key={recipient.to}
                    size="small"
                    label={recipient.to}
                    sx={{ marginLeft: '5px', marginBottom: '5px' }}
                    icon={
                      recipient.read ? <Visibility sx={{ height: '15px', width: '15px' }} /> : <></>
                    }
                  />
                );
              })}
            </Box>
          </Box>
        </Box>
        <div
          style={{
            whiteSpace: 'pre',
            fontFamily: 'monospace',
            fontSize: '18px',
            width: 'calc(16ch + 2px)',
            height: 'calc(1em * 7)',
            backgroundColor: 'black',
            color: 'white',
            resize: 'none',
            outline: 'none',
            padding: '5px',
            lineHeight: '1',
            textAlign: message.centerLines ? 'center' : 'left',
          }}
        >
          {message.message}
        </div>
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
      <Typography variant="h4" marginBottom={'30px'}>
        Message History
      </Typography>
      <Box display="flex" flexDirection="column" width="100%">
        {messages.map((message: Message) => {
          return buildMessageCard(message);
        })}
      </Box>
    </PageContainer>
  );
};

export default MessageHistory;
