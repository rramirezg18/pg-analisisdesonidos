import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Stack from '@mui/material/Stack'
import Tab from '@mui/material/Tab'
import Tabs from '@mui/material/Tabs'
import Typography from '@mui/material/Typography'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

const secciones = [
  { label: 'Resultados', ruta: '/admin' },
  { label: 'Validar casos', ruta: '/admin/validar' },
]

// Layout del panel de investigación. A diferencia del resto de la app (columna
// tipo teléfono), usa todo el ancho para que las gráficas se lean bien en PC.
export function AdminLayout() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const activa = secciones.findIndex((p) => p.ruta === pathname)

  return (
    <Box sx={{ minHeight: '100dvh', bgcolor: 'background.paper' }}>
      <Box sx={{ bgcolor: 'background.default', borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="lg">
          <Stack
            direction="row"
            sx={{ alignItems: 'center', justifyContent: 'space-between', pt: 2 }}
          >
            <Box>
              <Typography variant="overline" color="text.secondary">
                MotorScan · Administración
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Panel de investigación
              </Typography>
            </Box>
            <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/perfil')}>
              Volver a la app
            </Button>
          </Stack>
          <Tabs
            value={activa === -1 ? false : activa}
            onChange={(_, i: number) => navigate(secciones[i].ruta)}
            sx={{ mt: 1 }}
          >
            {secciones.map((p) => (
              <Tab key={p.ruta} label={p.label} />
            ))}
          </Tabs>
        </Container>
      </Box>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  )
}
