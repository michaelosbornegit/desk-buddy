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
import { Select, Switches } from 'mui-rff';
import { useSnackbar } from 'notistack';
import React, { useEffect, useState } from 'react';
import { Field, Form } from 'react-final-form';

import { messageFetchRecipients, sendMessage } from '../../services/message';
import { CreateMessage } from '../../types/messages';

const PageContainer = styled(Container)({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
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
  const [postProcessedMessage, setPostProcessedMessage] = useState('');
  const [centerLines, setCenterLines] = useState(false);
  const [showMessageTooLongWarning, setShowMessageTooLongWarning] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  const postProcessMessage = (message: string) => {
    let processedMessage = '';
    const maxLineLength = 16;

    // Split message by user-entered newlines, preserving empty lines
    const lines = message.split(/(\n)/);

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line === '\n') {
        processedMessage += '\n';
        continue;
      }
      let lineStart = 0;
      while (lineStart < line.length) {
        const end = lineStart + maxLineLength;

        if (end >= line.length) {
          processedMessage += line.slice(lineStart);
          break;
        }

        // Look for the last space within the max line length
        const lastSpace = line.lastIndexOf(' ', end);
        if (lastSpace > lineStart) {
          processedMessage += line.slice(lineStart, lastSpace) + '\n';
          lineStart = lastSpace + 1; // Move to the character after the space
        } else {
          processedMessage += line.slice(lineStart, end) + '\n';
          lineStart = end;
        }
      }
    }

    const splitMessage = processedMessage.split('\n');

    if (splitMessage.length > 7) {
      setShowMessageTooLongWarning(true);
    } else {
      setShowMessageTooLongWarning(false);
    }

    processedMessage = splitMessage.slice(0, 7).join('\n');

    console.log(processedMessage);
    setPostProcessedMessage(processedMessage);
  };

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
    // we want the post processed version
    values.message = postProcessedMessage;

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
        render={({ handleSubmit, values }) => {
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
              <Select name="to" label="Select Recipient(s)" data={recipients} required multiple />
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography style={{ marginBottom: '0', textAlign: 'center' }}>Message</Typography>
                <Field name="message">
                  {({ input }) => (
                    <textarea
                      {...input}
                      style={{
                        fontSize: '24px',
                        fontFamily: 'monospace',
                        width: 'calc(16ch + 2px)',
                        minHeight: 'calc(1em * 7)',
                        height: '178px',
                        resize: 'none',
                        padding: '5px',
                        lineHeight: '1',
                        border: '1px solid #ccc',
                        outline: 'none',
                        overflow: 'hidden',
                        textAlign: values.centerLines ? 'center' : 'left',
                      }}
                      onInput={(e) => {
                        const castedTarget = e.target as HTMLTextAreaElement;
                        castedTarget.style.height = 'auto';
                        castedTarget.style.height = `${castedTarget.scrollHeight}px`;
                        postProcessMessage(castedTarget.value);
                      }}
                      cols={16}
                    />
                  )}
                </Field>
                {showMessageTooLongWarning && (
                  <Typography variant="caption" color="error">
                    Desk Buddy&apos;s display only has 7 rows, see preview for what will be
                    displayed
                  </Typography>
                )}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ marginBottom: '16px' }}>
                  <Switches name="centerLines" data={{ label: 'Center Lines', value: false }} />
                </div>
                <Typography style={{ marginBottom: '0', textAlign: 'center' }}>Preview</Typography>
                <div
                  style={{
                    whiteSpace: 'pre',
                    fontFamily: 'monospace',
                    fontSize: '24px',
                    width: 'calc(16ch + 2px)',
                    height: 'calc(1em * 7)',
                    backgroundColor: 'black',
                    color: 'white',
                    resize: 'none',
                    outline: 'none',
                    padding: '5px',
                    lineHeight: '1',
                    marginBottom: '32px',
                    textAlign: values.centerLines ? 'center' : 'left',
                  }}
                >
                  {postProcessedMessage}
                </div>
              </div>
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
