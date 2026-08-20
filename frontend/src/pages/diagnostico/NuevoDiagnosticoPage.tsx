import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import Box from '@mui/material/Box'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import Step from '@mui/material/Step'
import StepLabel from '@mui/material/StepLabel'
import Stepper from '@mui/material/Stepper'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { obtenerCnnActivo } from '../../api/catalogo'
import type { AnalisisResultado } from '../../api/diagnostico'
import { MobileShell } from '../../components/MobileShell'
import type { DatosMoto, ModeloCNN, MotoResumen } from '../../types'
import type { EspectrogramaMel } from '../../utils/melSpectrogram'
import { PasoAudio } from './PasoAudio'
import { PasoDatosMoto } from './PasoDatosMoto'
import { PasoResultado } from './PasoResultado'

const PASOS = ['Datos', 'Audio', 'Resultado']

const MOTO_VACIA: DatosMoto = {
  id_marca: '',
  id_modelo: '',
  cilindraje: '',
  anio: '',
  kilometraje: '',
  notas: '',
}

const TITULOS = ['Nuevo diagnóstico', 'Nuevo diagnóstico', 'Resultado']

export function NuevoDiagnosticoPage() {
  const navigate = useNavigate()
  const [paso, setPaso] = useState(0)
  const [datosMoto, setDatosMoto] = useState<DatosMoto>(MOTO_VACIA)
  const [resumen, setResumen] = useState<MotoResumen | null>(null)
  const [espectrograma, setEspectrograma] = useState<EspectrogramaMel | null>(null)
  const [resultado, setResultado] = useState<AnalisisResultado | null>(null)
  const [cnn, setCnn] = useState<ModeloCNN | null>(null)

  useEffect(() => {
    obtenerCnnActivo()
      .then(setCnn)
      .catch(() => setCnn(null))
  }, [])

  function atras() {
    if (paso === 0) navigate('/')
    else setPaso((p) => p - 1)
  }

  function reiniciar() {
    setDatosMoto(MOTO_VACIA)
    setResumen(null)
    setEspectrograma(null)
    setResultado(null)
    setPaso(0)
  }

  return (
    <MobileShell>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 1,
          py: 1.5,
          position: 'relative',
        }}
      >
        <IconButton onClick={atras} aria-label="Volver">
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
          {TITULOS[paso]}
        </Typography>
      </Box>
      <Divider />

      <Box sx={{ px: 3, py: 2.5 }}>
        <Stepper activeStep={paso} alternativeLabel>
          {PASOS.map((p) => (
            <Step key={p}>
              <StepLabel>{p}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Box>

      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        {paso === 0 && (
          <PasoDatosMoto
            valor={datosMoto}
            onCambio={setDatosMoto}
            onResumen={setResumen}
            onSiguiente={() => setPaso(1)}
          />
        )}
        {paso === 1 && (
          <PasoAudio
            resumen={resumen}
            cilindraje={datosMoto.cilindraje}
            onEditar={() => setPaso(0)}
            onAnalizado={(esp, res) => {
              setEspectrograma(esp)
              setResultado(res)
              setPaso(2)
            }}
          />
        )}
        {paso === 2 && espectrograma && resultado && (
          <PasoResultado
            datosMoto={datosMoto}
            resumen={resumen}
            espectrograma={espectrograma}
            resultado={resultado}
            cnn={cnn}
            onOtro={reiniciar}
          />
        )}
      </Box>
    </MobileShell>
  )
}
