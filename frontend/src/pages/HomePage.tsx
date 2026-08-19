import LogoutIcon from '@mui/icons-material/Logout'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { useAuth } from '../auth/AuthContext'
import { MobileShell } from '../components/MobileShell'

export function HomePage() {
  const { usuario, logout } = useAuth()

  return (
    <MobileShell>
      <Box sx={{ p: 3, flex: 1 }}>
        <Stack
          direction="row"
          sx={{ justifyContent: 'space-between', alignItems: 'center' }}
        >
          <Typography variant="h6">MotorScan</Typography>
          <Button
            size="small"
            color="inherit"
            startIcon={<LogoutIcon />}
            onClick={logout}
          >
            Salir
          </Button>
        </Stack>

        <Typography variant="h4" sx={{ mt: 4 }}>
          ¡Hola, {usuario?.nombre ?? 'usuario'}!
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Sesión iniciada como {usuario?.email}.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
          Aquí irá el flujo de diagnóstico (nuevo diagnóstico, grabar audio,
          resultado e historial).
        </Typography>
      </Box>
    </MobileShell>
  )
}
