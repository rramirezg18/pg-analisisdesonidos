import Box from '@mui/material/Box'
import type { ReactNode } from 'react'

// Contenedor tipo teléfono: en móvil ocupa todo; en PC se centra una columna
// angosta sobre un fondo gris, para que siempre se vea como app móvil.
export function MobileShell({ children }: { children: ReactNode }) {
  return (
    <Box
      sx={{
        minHeight: '100dvh',
        display: 'flex',
        justifyContent: 'center',
        bgcolor: { xs: 'background.default', sm: '#0F172A' },
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 420,
          minHeight: '100dvh',
          bgcolor: 'background.default',
          boxShadow: { sm: '0 0 40px rgba(0,0,0,0.25)' },
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {children}
      </Box>
    </Box>
  )
}
