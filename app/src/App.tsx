import { Grow } from '@mui/material';
import { SnackbarKey, SnackbarProvider } from 'notistack';
import React, { useCallback } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Home from './pages/Home/Home';

export default function App() {

  return (
    <SnackbarProvider maxSnack={3} autoHideDuration={6000} TransitionComponent={Grow}>
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </SnackbarProvider>
  );
}
