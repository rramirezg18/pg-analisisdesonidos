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
import { MobileShell } from '../../components/MobileShell'
import type { Diagnostico, DatosMoto, ModeloCNN, MotoResumen } from '../../types'
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
  const [diagnostico, setDiagnostico] = useState<Diagnostico | null>(null)
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
    setDiagnostico(null)
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
            datos={datosMoto}
            onEditar={() => setPaso(0)}
            onAnalizado={(diag) => {
              setDiagnostico(diag)
              setPaso(2)
            }}
          />
        )}
        {paso === 2 && diagnostico && (
          <PasoResultado diagnostico={diagnostico} cnn={cnn} onOtro={reiniciar} />
        )}
      </Box>
    </MobileShell>
  )
}
