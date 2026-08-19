import { createTheme } from '@mui/material/styles'

// Paleta y tokens tomados del diseño (motorscan_login.svg).
export const theme = createTheme({
  palette: {
    primary: { main: '#6366F1', dark: '#4338CA', light: '#EEF2FF' },
    secondary: { main: '#1E293B' },
    background: { default: '#FFFFFF', paper: '#F9FAFB' },
    text: { primary: '#111827', secondary: '#6B7280' },
    divider: '#E5E7EB',
    success: { main: '#10B981' },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: 'Inter, -apple-system, system-ui, sans-serif',
    h4: { fontWeight: 700 },
    h6: { fontWeight: 600 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { paddingBlock: 12 } },
    },
  },
})

// Gradiente del espectrograma (Mel). Se expone como token reutilizable.
export const spectrogramGradient =
  'linear-gradient(180deg, #6B21A8 0%, #7C3AED 35%, #3B82F6 55%, #0891B2 75%, #10B981 100%)'
