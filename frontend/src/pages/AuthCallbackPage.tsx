import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

// Página a la que GitHub->backend redirige con #token=<jwt>.
// El token va en el fragmento para que no llegue a ningún servidor ni log.
// Guarda el token y manda al usuario a la app.
export function AuthCallbackPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  // Se lee una sola vez al montar, antes de que el efecto limpie la URL.
  const [token] = useState(() =>
    new URLSearchParams(window.location.hash.slice(1)).get('token'),
  )
  const error = !token

  useEffect(() => {
    // Quita el token de la barra de direcciones y del historial.
    window.history.replaceState(null, '', window.location.pathname)
    if (token) login(token).then(() => navigate('/', { replace: true }))
  }, [token, login, navigate])

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
