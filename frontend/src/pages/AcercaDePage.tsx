import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import GitHubIcon from '@mui/icons-material/GitHub'
import GraphicEqIcon from '@mui/icons-material/GraphicEq'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import Avatar from '@mui/material/Avatar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useNavigate } from 'react-router-dom'

import { MobileShell } from '../components/MobileShell'

// ─────────────────────────────────────────────────────────────────────────
const URL_MANUAL = '' 
const URL_REPOSITORIO = '' 

const DESARROLLADORES = [
  { nombre: 'Roberto Ramírez', rol: 'Desarrollador', contacto: 'rramirezg18@miumg.edu.gt' },
]
// ─────────────────────────────────────────────────────────────────────────

export function AcercaDePage() {
  const navigate = useNavigate()

  return (
    <MobileShell>
      <Box sx={{ display: 'flex', alignItems: 'center', px: 1, py: 1.5, position: 'relative' }}>
        <IconButton onClick={() => navigate('/perfil')} aria-label="Volver">
          <ArrowBackIcon />
        </IconButton>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            position: 'absolute',
            left: 0,
            right: 0,
            textAlign: 'center',
            pointerEvents: 'none',
          }}
        >
          Acerca de
        </Typography>
      </Box>
      <Divider />

      <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
        {/* Identidad de la app */}
        <Stack sx={{ alignItems: 'center', textAlign: 'center', mb: 3 }}>
          <Avatar sx={{ width: 72, height: 72, bgcolor: 'primary.main', mb: 1.5 }}>
            <GraphicEqIcon sx={{ fontSize: 40 }} />
          </Avatar>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            MotorScan
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Detección de fallas de motor por sonido con inteligencia artificial.
          </Typography>
        </Stack>

        {/* Desarrolladores */}
        <Card variant="outlined" sx={{ p: 2, bgcolor: 'background.paper' }}>
          <Typography variant="overline" color="text.secondary">
            Desarrollado por
          </Typography>
          <Divider sx={{ mt: 0.5, mb: 1 }} />
          <Stack spacing={1.5}>
            {DESARROLLADORES.map((d) => (
              <Stack key={d.contacto} direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.dark' }}>
                  {d.nombre.charAt(0).toUpperCase()}
                </Avatar>
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }} noWrap>
                    {d.nombre}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" noWrap>
                    {d.rol} · {d.contacto}
                  </Typography>
                </Box>
              </Stack>
            ))}
          </Stack>
        </Card>

        {/* Enlaces */}
        <Stack spacing={1.5} sx={{ mt: 3 }}>
          {URL_MANUAL && (
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<MenuBookIcon />}
              component="a"
              href={URL_MANUAL}
              target="_blank"
              rel="noopener noreferrer"
            >
              Manual de usuario
            </Button>
          )}
          {URL_REPOSITORIO && (
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<GitHubIcon />}
              component="a"
              href={URL_REPOSITORIO}
              target="_blank"
              rel="noopener noreferrer"
            >
              Repositorio en GitHub
            </Button>
          )}
        </Stack>

        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: 'block', textAlign: 'center', mt: 4 }}
        >
          MotorScan · Proyecto de graduación
        </Typography>
      </Box>
    </MobileShell>
  )
}
