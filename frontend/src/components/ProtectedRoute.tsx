import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

export function ProtectedRoute() {
  const { usuario, cargando } = useAuth()

  if (cargando) {
    return (
      <Box
        sx={{
          minHeight: '100dvh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
