import HistoryIcon from '@mui/icons-material/History'
import HomeIcon from '@mui/icons-material/Home'
import PersonIcon from '@mui/icons-material/Person'
import Box from '@mui/material/Box'
import BottomNavigation from '@mui/material/BottomNavigation'
import BottomNavigationAction from '@mui/material/BottomNavigationAction'
import Paper from '@mui/material/Paper'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { MobileShell } from './MobileShell'

// Secciones del menú inferior. Cada una es una ruta protegida.
const secciones = [
  { label: 'Inicio', icon: <HomeIcon />, ruta: '/' },
  { label: 'Historial', icon: <HistoryIcon />, ruta: '/historial' },
  { label: 'Perfil', icon: <PersonIcon />, ruta: '/perfil' },
]

// Layout compartido de las pantallas autenticadas: contenido scrolleable
// arriba + barra de navegación fija abajo (patrón móvil estándar).
export function AppLayout() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const indiceActivo = secciones.findIndex((s) => s.ruta === pathname)

  return (
    <MobileShell>
      <Box sx={{ flex: 1, overflowY: 'auto', pb: 9 }}>
        <Outlet />
      </Box>

      <Paper
        elevation={0}
        sx={{
          position: 'sticky',
          bottom: 0,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <BottomNavigation
          showLabels
          value={indiceActivo === -1 ? false : indiceActivo}
          onChange={(_, nuevo) => navigate(secciones[nuevo].ruta)}
        >
          {secciones.map((s) => (
            <BottomNavigationAction
              key={s.ruta}
              label={s.label}
              icon={s.icon}
            />
          ))}
        </BottomNavigation>
      </Paper>
    </MobileShell>
  )
}
