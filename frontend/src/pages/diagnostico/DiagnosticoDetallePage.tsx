import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CircularProgress from '@mui/material/CircularProgress'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import LinearProgress from '@mui/material/LinearProgress'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { obtenerDiagnostico, urlEspectrograma } from '../../api/diagnostico'
import { useAuth } from '../../auth/AuthContext'
import { MobileShell } from '../../components/MobileShell'
import type { Diagnostico } from '../../types'

function formatoFecha(iso: string): string {
  return new Date(iso).toLocaleDateString('es', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function Fila({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <Stack direction="row" sx={{ justifyContent: 'space-between', py: 1.25 }}>
      <Typography variant="body2" color="text.secondary">
        {etiqueta}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {valor}
      </Typography>
    </Stack>
  )
}

export function DiagnosticoDetallePage() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [diag, setDiag] = useState<Diagnostico | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const idNum = Number(id)
    if (!Number.isInteger(idNum)) {
      setError('Diagnóstico inválido.')
      return
    }
    obtenerDiagnostico(idNum, token)
      .then(setDiag)
      .catch(() => setError('No se pudo cargar el diagnóstico.'))
  }, [id, token])

  const esAnomalia = diag?.resultado === 'anomalia'

  return (
    <MobileShell>
      <Box sx={{ display: 'flex', alignItems: 'center', px: 1, py: 1.5, position: 'relative' }}>
        <IconButton onClick={() => navigate('/historial')} aria-label="Volver">
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
          Diagnóstico
        </Typography>
      </Box>
      <Divider />

      <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
        {error && <Alert severity="error">{error}</Alert>}

        {!error && !diag && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {diag && (
          <>
            <Card
              sx={{
                p: 3,
                textAlign: 'center',
                bgcolor: esAnomalia ? '#FFF7ED' : '#ECFDF5',
                border: 1,
                borderColor: esAnomalia ? '#FED7AA' : '#A7F3D0',
              }}
            >
              {esAnomalia ? (
                <WarningAmberIcon sx={{ fontSize: 44, color: 'warning.main' }} />
              ) : (
                <CheckCircleIcon sx={{ fontSize: 44, color: 'success.main' }} />
              )}
              <Typography
                variant="h5"
                sx={{ fontWeight: 700, mt: 1, color: esAnomalia ? '#C2410C' : '#047857' }}
              >
                {esAnomalia ? 'Anomalía detectada' : 'Sonido normal'}
              </Typography>
              <Stack
                direction="row"
                sx={{ justifyContent: 'space-between', mt: 2, mb: 0.5 }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Confianza
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                  {diag.confianza.toFixed(0)} %
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                color={esAnomalia ? 'warning' : 'success'}
                value={Math.min(diag.confianza, 100)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Card>

            <Typography
              variant="overline"
              color="text.secondary"
              sx={{ mt: 2, display: 'block' }}
            >
              Espectrograma de Mel
            </Typography>
            <Box
              component="img"
              src={urlEspectrograma(diag.espectrograma_ref)}
              alt="Espectrograma de Mel del motor"
              sx={{ width: '100%', borderRadius: 3, display: 'block', bgcolor: 'background.paper' }}
            />

            <Card variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'background.paper' }}>
              <Typography variant="overline" color="text.secondary">
                Detalles
              </Typography>
              <Divider sx={{ mt: 0.5 }} />
              <Fila etiqueta="Motocicleta" valor={`${diag.marca} ${diag.modelo}`} />
              <Divider />
              <Fila etiqueta="Cilindraje" valor={`${diag.cilindraje} cc`} />
              <Divider />
              <Fila etiqueta="Año" valor={String(diag.anio)} />
              {diag.kilometraje != null && (
                <>
                  <Divider />
                  <Fila
                    etiqueta="Kilometraje"
                    valor={`${diag.kilometraje.toLocaleString()} km`}
                  />
                </>
              )}
              <Divider />
              <Fila etiqueta="Fecha" valor={formatoFecha(diag.fecha_diagnostico)} />
              {diag.notas && (
                <>
                  <Divider />
                  <Fila etiqueta="Notas" valor={diag.notas} />
                </>
              )}
            </Card>

            <Alert severity="warning" sx={{ mt: 2, borderRadius: 3 }}>
              <strong>Aviso:</strong> diagnóstico preliminar. No sustituye la revisión
              de un mecánico certificado.
            </Alert>
          </>
        )}
      </Box>
    </MobileShell>
  )
}
