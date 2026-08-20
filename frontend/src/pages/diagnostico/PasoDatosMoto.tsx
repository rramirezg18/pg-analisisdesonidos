import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'

import { listarMarcas, listarModelosPorMarca } from '../../api/catalogo'
import { useAuth } from '../../auth/AuthContext'
import type { DatosMoto, Marca, Modelo, MotoResumen } from '../../types'

interface Props {
  valor: DatosMoto
  onCambio: (v: DatosMoto) => void
  onResumen: (r: MotoResumen | null) => void
  onSiguiente: () => void
}

export function PasoDatosMoto({ valor, onCambio, onResumen, onSiguiente }: Props) {
  const { token } = useAuth()
  const [marcas, setMarcas] = useState<Marca[]>([])
  const [modelos, setModelos] = useState<Modelo[]>([])

  useEffect(() => {
    listarMarcas()
      .then(setMarcas)
      .catch(() => setMarcas([]))
  }, [token])

  useEffect(() => {
    if (valor.id_marca === '') {
      setModelos([])
      return
    }
    listarModelosPorMarca(valor.id_marca)
      .then(setModelos)
      .catch(() => setModelos([]))
  }, [valor.id_marca])

  function cambiarMarca(id_marca: number) {
    // Al cambiar la marca se resetean modelo y cilindraje dependientes.
    onCambio({ ...valor, id_marca, id_modelo: '', cilindraje: '' })
  }

  function cambiarModelo(id_modelo: number) {
    const modelo = modelos.find((m) => m.id_modelo === id_modelo)
    const marca = marcas.find((m) => m.id_marca === valor.id_marca)
    onCambio({
      ...valor,
      id_modelo,
      cilindraje: modelo?.cilindraje ?? '',
    })
    onResumen(
      modelo && marca
        ? { marca: marca.nombre, modelo: modelo.nombre, cilindraje: modelo.cilindraje }
        : null,
    )
  }

  const anioActual = new Date().getFullYear()
  const anioValido =
    valor.anio !== '' && valor.anio >= 1980 && valor.anio <= anioActual + 1
  const valido =
    valor.id_marca !== '' && valor.id_modelo !== '' && anioValido

  return (
    <Box sx={{ px: 3, pb: 3 }}>
      <Typography variant="h5" sx={{ fontWeight: 700 }}>
        Datos de la moto
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 3 }}>
        Delimitan el sistema y ayudan a que el análisis sea más preciso.
      </Typography>

      <Stack spacing={2.5}>
        <TextField
          select
          required
          label="Marca"
          value={valor.id_marca}
          onChange={(e) => cambiarMarca(Number(e.target.value))}
        >
          {marcas.map((m) => (
            <MenuItem key={m.id_marca} value={m.id_marca}>
              {m.nombre}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          required
          label="Modelo"
          value={valor.id_modelo}
          disabled={valor.id_marca === ''}
          helperText={valor.id_marca === '' ? 'Elige primero una marca' : ' '}
          onChange={(e) => cambiarModelo(Number(e.target.value))}
        >
          {modelos.map((m) => (
            <MenuItem key={m.id_modelo} value={m.id_modelo}>
              {m.nombre}
            </MenuItem>
          ))}
        </TextField>

        <Stack direction="row" spacing={2}>
          <TextField
            label="Cilindraje"
            value={valor.cilindraje === '' ? '' : `${valor.cilindraje} cc`}
            disabled
            helperText="Definido por el modelo"
            sx={{ flex: 1 }}
          />
          <TextField
            required
            type="number"
            label="Año"
            value={valor.anio}
            error={valor.anio !== '' && !anioValido}
            onChange={(e) =>
              onCambio({
                ...valor,
                anio: e.target.value === '' ? '' : Number(e.target.value),
              })
            }
            sx={{ flex: 1 }}
          />
        </Stack>

        <TextField
          type="number"
          label="Kilometraje (opcional)"
          placeholder="Ej. 24500"
          value={valor.kilometraje}
          onChange={(e) =>
            onCambio({
              ...valor,
              kilometraje: e.target.value === '' ? '' : Number(e.target.value),
            })
          }
        />

        <TextField
          label="Notas (opcional)"
          placeholder="Ej. Ruido al acelerar..."
          multiline
          minRows={2}
          value={valor.notas}
          onChange={(e) => onCambio({ ...valor, notas: e.target.value })}
        />
      </Stack>

      <Button
        fullWidth
        variant="contained"
        size="large"
        endIcon={<ArrowForwardIcon />}
        disabled={!valido}
        onClick={onSiguiente}
        sx={{ mt: 4 }}
      >
        Continuar
      </Button>
    </Box>
  )
}
