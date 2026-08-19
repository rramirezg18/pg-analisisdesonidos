import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

// Página a la que GitHub->backend redirige con ?token=<jwt>.
// Guarda el token y manda al usuario a la app.
export function AuthCallbackPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState(false)

  useEffect(() => {
    const token = params.get('token')
    if (!token) {
      setError(true)
      return
    }
    login(token).then(() => navigate('/', { replace: true }))
  }, [params, login, navigate])

  return (
    <Box
      sx={{
        minHeight: '100dvh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        px: 3,
        textAlign: 'center',
      }}
    >
      {error ? (
        <Typography color="error">
          No se recibió el token de acceso. Vuelve a iniciar sesión.
        </Typography>
      ) : (
        <>
          <CircularProgress />
          <Typography color="text.secondary">Iniciando sesión…</Typography>
        </>
      )}
    </Box>
  )
}
