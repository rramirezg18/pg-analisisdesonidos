import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HistoryIcon from '@mui/icons-material/History'
import RefreshIcon from '@mui/icons-material/Refresh'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import Divider from '@mui/material/Divider'
import LinearProgress from '@mui/material/LinearProgress'
import Stack from '@mui/material/Stack'
import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import Typography from '@mui/material/Typography'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { registrarVeredictoMecanico, urlEspectrograma } from '../../api/diagnostico'
import { useAuth } from '../../auth/AuthContext'
import type { Diagnostico, ModeloCNN, Veredicto } from '../../types'

interface Props {
  diagnostico: Diagnostico
  cnn: ModeloCNN | null
  onOtro: () => void
}

// El mecánico registra lo que encontró al revisar la moto. Se guarda al
// elegir una opción y se puede cambiar; sirve para medir si el sistema acierta.
function VeredictoMecanico({ idDiagnostico }: { idDiagnostico: number }) {
  const { token } = useAuth()
  const [veredicto, setVeredicto] = useState<Veredicto | null>(null)
  const [estado, setEstado] = useState<'inicial' | 'guardando' | 'guardado' | 'error'>('inicial')

  async function guardar(v: Veredicto) {
    const anterior = veredicto
    setVeredicto(v)
    setEstado('guardando')
    try {
      await registrarVeredictoMecanico(idDiagnostico, v, token)
      setEstado('guardado')
    } catch {
      setVeredicto(anterior)
      setEstado('error')
    }
  }

  return (
    <Card variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'background.paper' }}>
      <Typography variant="overline" color="text.secondary">
        Revisión del mecánico
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.5, mb: 1 }}>
        Al revisar la moto, ¿qué encontró?
      </Typography>
      <ToggleButtonGroup
        exclusive
        fullWidth
        size="small"
        value={veredicto}
        disabled={estado === 'guardando'}
        onChange={(_, v: Veredicto | null) => v && guardar(v)}
      >
        <ToggleButton value="sano" color="success" sx={{ textTransform: 'none' }}>
          Sin falla
        </ToggleButton>
        <ToggleButton value="leve" color="warning" sx={{ textTransform: 'none' }}>
          Falla leve
        </ToggleButton>
        <ToggleButton value="grave" color="error" sx={{ textTransform: 'none' }}>
          Falla grave
        </ToggleButton>
      </ToggleButtonGroup>

      {estado === 'guardado' && (
        <Alert severity="success" sx={{ mt: 1.5 }}>
          Revisión guardada. Puede cambiarla si se equivocó.
        </Alert>
      )}
      {estado === 'error' && (
        <Alert severity="error" sx={{ mt: 1.5 }}>
          No se pudo guardar. Intente de nuevo.
        </Alert>
      )}
    </Card>
  )
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

export function PasoResultado({ diagnostico, cnn, onOtro }: Props) {
  const navigate = useNavigate()
  const esAnomalia = diagnostico.resultado === 'anomalia'
  const color = esAnomalia ? 'warning' : 'success'

  return (
    <Box sx={{ px: 3, pb: 3 }}>
      {/* Tarjeta de resultado del CNN */}
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
        <Typography variant="body2" sx={{ mt: 0.5, color: 'text.secondary' }}>
          {esAnomalia
            ? 'Se identificaron patrones anómalos. Se recomienda revisar con un mecánico.'
            : 'No se detectaron patrones anómalos en el motor.'}
        </Typography>

        <Stack
          direction="row"
          sx={{ justifyContent: 'space-between', mt: 2, mb: 0.5 }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Confianza
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 700 }}>
            {diagnostico.confianza.toFixed(0)} %
          </Typography>
        </Stack>
        <LinearProgress
          variant="determinate"
          color={color}
          value={Math.min(diagnostico.confianza, 100)}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Card>

      <VeredictoMecanico idDiagnostico={diagnostico.id_diagnostico} />

      {/* Espectrograma de Mel: la entrada del modelo CNN (imagen del servidor) */}
      <Typography variant="overline" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Espectrograma de Mel
      </Typography>
      <Box
        component="img"
        src={urlEspectrograma(diagnostico.espectrograma_ref)}
        alt="Espectrograma de Mel del motor"
        sx={{
          width: '100%',
          borderRadius: 3,
          display: 'block',
          bgcolor: 'background.paper',
        }}
      />

      {/* Detalles */}
      <Card variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'background.paper' }}>
        <Typography variant="overline" color="text.secondary">
          Detalles del análisis
        </Typography>
        <Divider sx={{ mt: 0.5 }} />
        <Fila
          etiqueta="Motocicleta"
          valor={`${diagnostico.marca} ${diagnostico.modelo}`}
        />
        <Divider />
        <Fila etiqueta="Cilindraje" valor={`${diagnostico.cilindraje} cc`} />
        <Divider />
        <Fila etiqueta="Año" valor={String(diagnostico.anio)} />
        {diagnostico.kilometraje != null && (
          <>
            <Divider />
            <Fila
              etiqueta="Kilometraje"
              valor={`${diagnostico.kilometraje.toLocaleString()} km`}
            />
          </>
        )}
        <Divider />
        <Fila etiqueta="Modelo CNN" valor={cnn?.version ?? '—'} />
      </Card>

      <Stack spacing={1.5} sx={{ mt: 3 }}>
        <Button
          fullWidth
          variant="contained"
          size="large"
          startIcon={<RefreshIcon />}
          onClick={onOtro}
        >
          Realizar otro diagnóstico
        </Button>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<HistoryIcon />}
          onClick={() => navigate('/historial')}
        >
          Ver historial
        </Button>
      </Stack>
    </Box>
  )
}
