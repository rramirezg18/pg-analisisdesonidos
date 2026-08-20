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
import Typography from '@mui/material/Typography'
import { useNavigate } from 'react-router-dom'

import type { AnalisisResultado } from '../../api/diagnostico'
import type { DatosMoto, ModeloCNN, MotoResumen } from '../../types'
import type { EspectrogramaMel } from '../../utils/melSpectrogram'

interface Props {
  datosMoto: DatosMoto
  resumen: MotoResumen | null
  espectrograma: EspectrogramaMel
  resultado: AnalisisResultado
  cnn: ModeloCNN | null
  onOtro: () => void
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

export function PasoResultado({
  datosMoto,
  resumen,
  espectrograma,
  resultado,
  cnn,
  onOtro,
}: Props) {
  const navigate = useNavigate()
  const esAnomalia = resultado.clase === 'anomalia'
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
            {resultado.confianza.toFixed(0)} %
          </Typography>
        </Stack>
        <LinearProgress
          variant="determinate"
          color={color}
          value={Math.min(resultado.confianza, 100)}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Card>

      {/* Espectrograma de Mel: la entrada del modelo CNN */}
      <Typography variant="overline" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Espectrograma de Mel
      </Typography>
      <Box
        component="img"
        src={espectrograma.dataUrl}
        alt="Espectrograma de Mel del motor"
        sx={{
          width: '100%',
          height: 160,
          objectFit: 'fill',
          borderRadius: 3,
          display: 'block',
          imageRendering: 'pixelated',
        }}
      />
      <Typography variant="caption" color="text.secondary">
        {espectrograma.height} bandas Mel × {espectrograma.width} frames (preview).
      </Typography>

      {/* Detalles */}
      <Card variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'background.paper' }}>
        <Typography variant="overline" color="text.secondary">
          Detalles del análisis
        </Typography>
        <Divider sx={{ mt: 0.5 }} />
        <Fila
          etiqueta="Motocicleta"
          valor={resumen ? `${resumen.marca} ${resumen.modelo}` : '—'}
        />
        <Divider />
        <Fila
          etiqueta="Cilindraje"
          valor={datosMoto.cilindraje ? `${datosMoto.cilindraje} cc` : '—'}
        />
        <Divider />
        <Fila etiqueta="Año" valor={String(datosMoto.anio || '—')} />
        <Divider />
        <Fila
          etiqueta="Duración audio"
          valor={`${espectrograma.duracionSeg.toFixed(1)} s`}
        />
        <Divider />
        <Fila etiqueta="Modelo CNN" valor={cnn?.version ?? '—'} />
      </Card>

      <Alert severity="warning" sx={{ mt: 2, borderRadius: 3 }}>
        <strong>Aviso:</strong> diagnóstico preliminar. No sustituye la revisión de
        un mecánico certificado.
      </Alert>

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
