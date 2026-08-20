import AddIcon from '@mui/icons-material/Add'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import GraphicEqIcon from '@mui/icons-material/GraphicEq'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardActionArea from '@mui/material/CardActionArea'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { spectrogramGradient } from '../theme'

export function HomePage() {
  const { usuario } = useAuth()
  const navigate = useNavigate()

  const primerNombre = usuario?.nombre?.split(' ')[0] ?? 'motociclista'

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="body2" color="text.secondary">
        Hola,
      </Typography>
      <Typography variant="h4" sx={{ mb: 3 }}>
        {primerNombre} 👋
      </Typography>

      {/* CTA principal: iniciar el flujo de diagnóstico */}
      <Card
        sx={{
          background: spectrogramGradient,
          color: 'common.white',
          borderRadius: 4,
        }}
      >
        <CardActionArea
          onClick={() => navigate('/diagnostico/nuevo')}
          sx={{ p: 3 }}
        >
          <GraphicEqIcon sx={{ fontSize: 40, mb: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Nuevo diagnóstico
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
            Graba el motor y detecta anomalías con IA.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{
              mt: 2,
              bgcolor: 'common.white',
              color: 'text.primary',
              '&:hover': { bgcolor: 'grey.100' },
            }}
          >
            Empezar
          </Button>
        </CardActionArea>
      </Card>

      {/* Diagnósticos recientes (empty state por ahora) */}
      <Stack
        direction="row"
        sx={{ justifyContent: 'space-between', alignItems: 'center', mt: 4 }}
      >
        <Typography variant="h6">Recientes</Typography>
        <Button
          size="small"
          endIcon={<ChevronRightIcon />}
          onClick={() => navigate('/historial')}
        >
          Ver historial
        </Button>
      </Stack>

      <Card
        variant="outlined"
        sx={{
          mt: 1,
          p: 4,
          textAlign: 'center',
          bgcolor: 'background.paper',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Aún no tienes diagnósticos.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Crea el primero desde el botón de arriba.
        </Typography>
      </Card>
    </Box>
  )
}
