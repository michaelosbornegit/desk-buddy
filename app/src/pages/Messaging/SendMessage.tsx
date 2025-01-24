import styled from '@emotion/styled';
import { Send } from '@mui/icons-material';
import {
  Box,
  Button,
  Container,
  Switch,
  TextField as MuiTextField,
  Typography,
} from '@mui/material';
import { Select } from 'mui-rff';
import { useSnackbar } from 'notistack';
import React, { useEffect, useState } from 'react';
import { Field, Form } from 'react-final-form';

import { messageFetchRecipients, sendMessage } from '../../services/message';
import { CreateMessage } from '../../types/messages';

const PageContainer = styled(Container)({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  width: '100vw',
});

const formatMessage = (message: string, smartTruncate: boolean): string => {
  if (!message) {
    return '';
  }

  const lines = message.split('\n');
  const formattedLines = [];

  for (let i = 0; i < lines.length; i++) {
    let currentLine = lines[i];

    // Handle line splitting for lines longer than 16 characters
    while (currentLine.length > 16) {
      if (smartTruncate && formattedLines.length < 6) {
        // Smart truncate: Split on the last space within the first 16 characters if possible
        const spaceIndex = currentLine.lastIndexOf(' ', 16);
        if (spaceIndex === -1) {
          // No space, split exactly at the 16th character
          formattedLines.push(currentLine.slice(0, 16));
          currentLine = currentLine.slice(16);
        } else {
          // Split at the last space
          formattedLines.push(currentLine.slice(0, spaceIndex));
          currentLine = currentLine.slice(spaceIndex + 1);
        }
      } else {
        // Dumb truncate or smart truncate beyond the 6th line: Always split exactly at the 16th character
        formattedLines.push(currentLine.slice(0, 16));
        currentLine = currentLine.slice(16);
      }

      // Stop further processing if the 6th line is complete
      if (formattedLines.length === 6) {
        break;
      }
    }

    // Add the remaining part of the current line
    formattedLines.push(currentLine);

    // If the 7th line is reached, enforce no further input
    if (formattedLines.length === 7) {
      const seventhLine = formattedLines[6];
      if (seventhLine.length > 16) {
        // Trim the 7th line to exactly 16 characters without truncating back to a space
        formattedLines[6] = seventhLine.slice(0, 16);
      }

      // Ignore any remaining content in `currentLine` beyond the 7th line
      break;
    }
  }

  // Ensure no additional lines beyond the 7th
  return formattedLines.slice(0, 7).join('\n');
};

type Recipient = {
  label: string;
  value: string;
};

const SendMessage = (): JSX.Element => {
  const [smartTruncate, setSmartTruncate] = useState(true);
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    const fetchRecipients = async () => {
      const fetchedRecipients = await messageFetchRecipients();
      const mappedRecipients = fetchedRecipients.map((recipient: string) => {
        return { label: recipient, value: recipient };
      });
      setRecipients(mappedRecipients);
    };
    if (recipients.length === 0) {
      fetchRecipients();
    }
  }, [recipients.length]);

  const onSubmit = async (values: CreateMessage) => {
    try {
      await sendMessage(values);
      enqueueSnackbar('Message sent', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Error sending message', { variant: 'error' });
    }
  };

  return (
    <PageContainer maxWidth="sm">
      <Form
        onSubmit={onSubmit}
        render={({ handleSubmit }) => {
          return (
            <form
              onSubmit={handleSubmit}
              style={{
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '16px',
              }}
            >
              <Select
                name="to"
                label="Select Recipient(s)"
                // formControlProps={{ margin: 'normal' }}
                data={recipients}
                required
                multiple
              />
              <Box display="flex" alignItems="center">
                <Switch
                  checked={smartTruncate}
                  onChange={(e) => setSmartTruncate(e.target.checked)}
                />
                <Typography sx={{ width: '100% ' }}>
                  Split lines on spaces (better for typing sentences)
                </Typography>
              </Box>
              {/* Hack for mui rff to allow us to have a controlled field to split lines */}
              <Field name="message">
                {({ input, meta }) => (
                  <MuiTextField
                    {...input}
                    label="Message"
                    name="message"
                    required
                    variant="outlined"
                    multiline
                    rows={7}
                    sx={{
                      marginBottom: '32px',
                    }}
                    slotProps={{
                      input: {
                        style: {
                          fontFamily: 'monospace',
                          fontSize: '20px',
                          width: '250px',
                          lineHeight: 1,
                        },
                      },
                    }}
                    onChange={(e) => {
                      const modifiedValue = formatMessage(e.target.value, smartTruncate); // Custom logic to modify value
                      input.onChange(modifiedValue); // Update form state
                    }}
                    helperText={meta.touched && meta.error}
                  />
                )}
              </Field>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                sx={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}
                endIcon={<Send />}
              >
                Send
              </Button>
            </form>
          );
        }}
      />
    </PageContainer>
  );
};

export default SendMessage;
