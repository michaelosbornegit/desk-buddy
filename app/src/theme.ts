import { createTheme } from '@mui/material';

const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          height: '58px',
        },
      },
    },
  },
  palette: {
    primary: {
      main: 'rgb(0, 215, 90)',
      contrastText: '#FFF',
    },
    secondary: {
      main: '#FFF',
    },
  },
});

export default theme;
