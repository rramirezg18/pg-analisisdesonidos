import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import HistoryIcon from '@mui/icons-material/History'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardActionArea from '@mui/material/CardActionArea'
import Chip from '@mui/material/Chip'
import CircularProgress from '@mui/material/CircularProgress'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listarMisDiagnosticos } from '../api/diagnostico'
import { useAuth } from '../auth/AuthContext'
import type { Diagnostico } from '../types'

function formatoFecha(iso: string): string {
  return new Date(iso).toLocaleDateString('es', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function HistorialPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [diagnosticos, setDiagnosticos] = useState<Diagnostico[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listarMisDiagnosticos(token)
      .then(setDiagnosticos)
      .catch(() => setError('No se pudo cargar el historial.'))
  }, [token])

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Historial
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      {!error && diagnosticos === null && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {diagnosticos?.length === 0 && (
        <Card
          variant="outlined"
          sx={{ p: 5, textAlign: 'center', bgcolor: 'background.paper' }}
        >
          <HistoryIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body1" sx={{ fontWeight: 600 }}>
            Sin diagnósticos todavía
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Tus análisis aparecerán aquí ordenados por fecha.
          </Typography>
        </Card>
      )}

      <Stack spacing={1.5}>
        {diagnosticos?.map((d) => {
          const esAnomalia = d.resultado === 'anomalia'
          return (
            <Card key={d.id_diagnostico} variant="outlined">
              <CardActionArea
                onClick={() => navigate(`/diagnostico/${d.id_diagnostico}`)}
                sx={{ p: 2 }}
              >
                <Stack direction="row" sx={{ alignItems: 'center' }} spacing={1.5}>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="body1" sx={{ fontWeight: 600 }} noWrap>
                      {d.marca} {d.modelo}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatoFecha(d.fecha_diagnostico)}
                    </Typography>
                  </Box>
                  <Chip
                    size="small"
                    color={esAnomalia ? 'warning' : 'success'}
                    label={esAnomalia ? 'Anomalía' : 'Normal'}
                  />
                  <ChevronRightIcon sx={{ color: 'text.secondary' }} />
                </Stack>
              </CardActionArea>
            </Card>
          )
        })}
      </Stack>
    </Box>
  )
}
