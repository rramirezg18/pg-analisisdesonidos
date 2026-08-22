import EditIcon from '@mui/icons-material/Edit'
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord'
import GraphicEqIcon from '@mui/icons-material/GraphicEq'
import StopIcon from '@mui/icons-material/Stop'
import TwoWheelerIcon from '@mui/icons-material/TwoWheeler'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import Alert from '@mui/material/Alert'
import Avatar from '@mui/material/Avatar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CircularProgress from '@mui/material/CircularProgress'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useEffect, useRef, useState } from 'react'

import { analizarAudio } from '../../api/diagnostico'
import { useAuth } from '../../auth/AuthContext'
import type { DatosMoto, Diagnostico, MotoResumen } from '../../types'

interface Props {
  resumen: MotoResumen | null
  datos: DatosMoto
  onEditar: () => void
  onAnalizado: (diagnostico: Diagnostico) => void
}

// Extensión de archivo a partir del MIME del blob (ej. "audio/webm;codecs=opus" -> "webm").
function extensionDe(tipo: string): string {
  const sub = tipo.split('/')[1]?.split(';')[0] ?? 'webm'
  return sub === 'mpeg' ? 'mp3' : sub === 'x-m4a' ? 'm4a' : sub
}

const RECOMENDACIONES = [
  'Duración mínima: 4 segundos',
  'Motor en ralentí, sin acelerar',
  'Ambiente silencioso',
  'Celular a 20-30 cm del motor',
]

export function PasoAudio({ resumen, datos, onEditar, onAnalizado }: Props) {
  const { token } = useAuth()
  const [grabando, setGrabando] = useState(false)
  const [segundos, setSegundos] = useState(0)
  const [audio, setAudio] = useState<{ blob: Blob; url: string; nombre: string } | null>(
    null,
  )
  const [analizando, setAnalizando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      recorderRef.current?.stream.getTracks().forEach((t) => t.stop())
    }
  }, [])

  function fijarAudio(blob: Blob, nombre: string) {
    setAudio((prev) => {
      if (prev) URL.revokeObjectURL(prev.url)
      return { blob, url: URL.createObjectURL(blob), nombre }
    })
  }

  async function iniciarGrabacion() {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      chunksRef.current = []
      rec.ondataavailable = (e) => e.data.size > 0 && chunksRef.current.push(e.data)
      rec.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: rec.mimeType })
        fijarAudio(blob, `grabacion.${extensionDe(rec.mimeType)}`)
        stream.getTracks().forEach((t) => t.stop())
      }
      rec.start()
      recorderRef.current = rec
      setGrabando(true)
      setSegundos(0)
      timerRef.current = window.setInterval(() => setSegundos((s) => s + 1), 1000)
    } catch {
      setError('No se pudo acceder al micrófono. Revisa los permisos del navegador.')
    }
  }

  function detenerGrabacion() {
    recorderRef.current?.stop()
    setGrabando(false)
    if (timerRef.current) clearInterval(timerRef.current)
  }

  function subirArchivo(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      setError(null)
      fijarAudio(file, file.name)
    }
    e.target.value = ''
  }

  async function analizar() {
    if (!audio || datos.id_modelo === '' || datos.anio === '') return
    setAnalizando(true)
    setError(null)
    try {
      // El backend regenera el espectrograma con librosa, corre el CNN y
      // persiste la imagen. Devuelve el diagnóstico ya guardado.
      const diagnostico = await analizarAudio(audio.blob, audio.nombre, datos, token)
      onAnalizado(diagnostico)
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : 'No se pudo analizar el audio. Intenta de nuevo.',
      )
    } finally {
      setAnalizando(false)
    }
  }

  const mmss = `${String(Math.floor(segundos / 60)).padStart(2, '0')}:${String(segundos % 60).padStart(2, '0')}`

  return (
    <Box sx={{ px: 3, pb: 3 }}>
      <Typography variant="h5" sx={{ fontWeight: 700 }}>
        Graba el motor
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>
        Enciende la moto y déjala en ralentí unos segundos antes de grabar.
      </Typography>

      {/* Moto seleccionada */}
      <Card variant="outlined" sx={{ p: 1.5, mb: 2, bgcolor: 'background.paper' }}>
        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
          <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.dark' }}>
            <TwoWheelerIcon />
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" sx={{ fontWeight: 600 }} noWrap>
              {resumen
                ? `${resumen.marca} ${resumen.modelo} · ${resumen.cilindraje} cc`
                : 'Moto sin definir'}
            </Typography>
          </Box>
          <Button size="small" startIcon={<EditIcon />} onClick={onEditar}>
            Editar
          </Button>
        </Stack>
      </Card>

      {/* Zona de grabación */}
      <Card
        variant="outlined"
        sx={{
          p: 3,
          textAlign: 'center',
          borderStyle: 'dashed',
          bgcolor: 'background.paper',
        }}
      >
        <Avatar
          sx={{
            width: 64,
            height: 64,
            mx: 'auto',
            mb: 1.5,
            bgcolor: grabando ? 'error.light' : 'primary.light',
            color: grabando ? 'error.main' : 'primary.dark',
          }}
        >
          <GraphicEqIcon fontSize="large" />
        </Avatar>

        {grabando ? (
          <>
            <Typography variant="h6" sx={{ fontVariantNumeric: 'tabular-nums' }}>
              {mmss}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Grabando…
            </Typography>
            <Button
              fullWidth
              variant="contained"
              color="error"
              startIcon={<StopIcon />}
              onClick={detenerGrabacion}
            >
              Detener
            </Button>
          </>
        ) : (
          <>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {audio ? 'Audio listo' : 'Grabar ahora'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              o sube un archivo existente
            </Typography>

            {audio && (
              <Box
                component="audio"
                controls
                src={audio.url}
                sx={{ width: '100%', mb: 2 }}
              />
            )}

            <Stack spacing={1.5}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<FiberManualRecordIcon />}
                onClick={iniciarGrabacion}
              >
                {audio ? 'Grabar de nuevo' : 'Grabar audio'}
              </Button>
              <Button
                fullWidth
                variant="outlined"
                component="label"
                startIcon={<UploadFileIcon />}
              >
                Subir archivo
                <input hidden type="file" accept="audio/*" onChange={subirArchivo} />
              </Button>
            </Stack>
          </>
        )}
      </Card>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Recomendaciones */}
      <Card variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
          Recomendaciones
        </Typography>
        <Stack spacing={0.75}>
          {RECOMENDACIONES.map((r) => (
            <Typography key={r} variant="body2" color="text.secondary">
              • {r}
            </Typography>
          ))}
        </Stack>
      </Card>

      <Button
        fullWidth
        variant="contained"
        size="large"
        disabled={!audio || analizando}
        onClick={analizar}
        startIcon={analizando ? <CircularProgress size={18} color="inherit" /> : null}
        sx={{ mt: 3 }}
      >
        {analizando ? 'Analizando…' : 'Analizar audio'}
      </Button>
    </Box>
  )
}
