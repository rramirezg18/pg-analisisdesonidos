import GitHubIcon from '@mui/icons-material/GitHub'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Divider from '@mui/material/Divider'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { Navigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { MobileShell } from '../components/MobileShell'
import { spectrogramGradient } from '../theme'

const PASOS = [
  {
    emoji: '🎙️',
    fondo: '#DBEAFE',
    titulo: '1. Graba el motor',
    texto: 'Enciende la moto en ralentí y graba con tu celular.',
  },
  {
    emoji: '🧠',
    fondo: '#FCE7F3',
    titulo: '2. Analizamos con CNN',
    texto: 'Convertimos el audio en espectrograma y lo procesa la red neuronal.',
  },
  {
    emoji: '✅',
    fondo: '#D1FAE5',
    titulo: '3. Recibe el diagnóstico',
    texto: 'Sabrás si el motor suena normal o con anomalía, con su confianza.',
  },
]

export function LoginPage() {
  const { usuario, cargando, loginConGithub } = useAuth()

  if (!cargando && usuario) {
    return <Navigate to="/" replace />
  }

  return (
    <MobileShell>
      <Box sx={{ px: 3, pt: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 2,
              bgcolor: 'secondary.main',
              color: 'common.white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: 18,
            }}
          >
            M
          </Box>
          <Typography variant="h6">MotorScan</Typography>
        </Stack>

        <Divider sx={{ mt: 2 }} />

        {/* Badge */}
        <Chip
          label="Análisis con IA"
          size="small"
          sx={{
            mt: 3,
            alignSelf: 'flex-start',
            bgcolor: 'primary.light',
            color: 'primary.dark',
            fontWeight: 600,
            '& .MuiChip-icon': { color: 'primary.main' },
          }}
          icon={
            <Box
              component="span"
              sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'primary.main' }}
            />
          }
        />

        {/* Headline + subtítulo */}
        <Typography variant="h4" sx={{ mt: 2 }}>
          Detecta fallas en el motor de tu moto
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          Analizamos el sonido de tu motor en ralentí con una red neuronal para
          detectar anomalías por holgura de válvulas.
        </Typography>

        {/* Espectrograma */}
        <Box
          sx={{
            mt: 3,
            height: 120,
            borderRadius: 3,
            background: spectrogramGradient,
          }}
        />
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 1, textAlign: 'center', fontFamily: 'monospace' }}
        >
          Espectrograma de Mel · 128 bandas
        </Typography>

        {/* Cómo funciona */}
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ mt: 3, fontWeight: 700, letterSpacing: 1 }}
        >
          ¿Cómo funciona?
        </Typography>
        <Stack spacing={1.5} sx={{ mt: 1 }}>
          {PASOS.map((paso) => (
            <Paper
              key={paso.titulo}
              variant="outlined"
              sx={{ p: 1.5, display: 'flex', gap: 1.5, alignItems: 'center' }}
            >
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2.5,
                  bgcolor: paso.fondo,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 22,
                  flexShrink: 0,
                }}
              >
                {paso.emoji}
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {paso.titulo}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {paso.texto}
                </Typography>
              </Box>
            </Paper>
          ))}
        </Stack>

        {/* Botones */}
        <Stack spacing={1.5} sx={{ mt: 4, pb: 3 }}>
          <Button variant="outlined" color="inherit" disabled fullWidth>
            Continuar con Google · Próximamente
          </Button>
          <Button
            variant="contained"
            color="secondary"
            fullWidth
            startIcon={<GitHubIcon />}
            onClick={loginConGithub}
          >
            Continuar con GitHub
          </Button>
        </Stack>
      </Box>
    </MobileShell>
  )
}
