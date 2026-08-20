import GitHubIcon from '@mui/icons-material/GitHub'
import LogoutIcon from '@mui/icons-material/Logout'
import Avatar from '@mui/material/Avatar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import Chip from '@mui/material/Chip'
import Divider from '@mui/material/Divider'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import { useAuth } from '../auth/AuthContext'

export function PerfilPage() {
  const { usuario, logout } = useAuth()

  const iniciales = (usuario?.nombre ?? usuario?.email ?? '?')
    .charAt(0)
    .toUpperCase()

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Perfil
      </Typography>

      <Card variant="outlined" sx={{ p: 3, bgcolor: 'background.paper' }}>
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
          <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main' }}>
            {iniciales}
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h6" noWrap>
              {usuario?.nombre ?? 'Usuario'}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {usuario?.email}
            </Typography>
          </Box>
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Stack
          direction="row"
          sx={{ justifyContent: 'space-between', alignItems: 'center' }}
        >
          <Typography variant="body2" color="text.secondary">
            Sesión iniciada con
          </Typography>
          <Chip
            size="small"
            icon={<GitHubIcon />}
            label={usuario?.proveedor_oauth ?? 'oauth'}
            sx={{ textTransform: 'capitalize' }}
          />
        </Stack>
      </Card>

      <Button
        fullWidth
        variant="outlined"
        color="error"
        startIcon={<LogoutIcon />}
        onClick={logout}
        sx={{ mt: 3 }}
      >
        Cerrar sesión
      </Button>
    </Box>
  )
}
