import CancelIcon from '@mui/icons-material/Cancel'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import Chip from '@mui/material/Chip'
import CircularProgress from '@mui/material/CircularProgress'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'

import { listarDiagnosticosAdmin, registrarVeredicto } from '../../api/admin'
import { useAuth } from '../../auth/AuthContext'
import type { DiagnosticoAdmin, Veredicto } from '../../types'

type Filtro = 'pendientes' | 'validados' | ''

// El sistema acierta si coincide con el mecánico: sano <-> normal, leve/grave <-> anomalía.
function coincide(d: DiagnosticoAdmin): boolean | null {
  if (!d.veredicto_mecanico) return null
  const real = d.veredicto_mecanico === 'sano' ? 'normal' : 'anomalia'
  return d.resultado === real
}

export function AdminValidacionPage() {
  const { token } = useAuth()
  const [filtro, setFiltro] = useState<Filtro>('pendientes')
  const [filas, setFilas] = useState<DiagnosticoAdmin[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let activo = true
    listarDiagnosticosAdmin(filtro, token)
      .then((d) => activo && setFilas(d))
      .catch((e: Error) => activo && setError(e.message))
    return () => {
      activo = false
    }
  }, [filtro, token])

  async function guardar(d: DiagnosticoAdmin, veredicto: Veredicto | null) {
    setError(null)
    try {
      await registrarVeredicto(d.id_diagnostico, veredicto, token)
      // Se actualiza en el lugar (no se quita de la lista) para poder corregir un clic equivocado.
      setFilas((prev) =>
        prev?.map((f) =>
          f.id_diagnostico === d.id_diagnostico
            ? { ...f, veredicto_mecanico: veredicto, fecha_validacion: veredicto ? new Date().toISOString() : null }
            : f,
        ) ?? null,
      )
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <Stack spacing={2}>
      <Card variant="outlined" sx={{ p: 2 }}>
        <Typography variant="body2">
          Para cada diagnóstico, registra lo que dijo el mecánico al revisar la moto:{' '}
          <b>Sano</b>, <b>Leve</b> (problema inicial) o <b>Grave</b>. Con esto se calculan la
          exactitud y la detección temprana del panel de resultados.
        </Typography>
      </Card>

      <ToggleButtonGroup
        exclusive
        size="small"
        color="primary"
        value={filtro}
        onChange={(_, v: Filtro | null) => {
          if (v == null) return
          setFiltro(v)
          setFilas(null) // muestra el spinner mientras carga la nueva vista
        }}
      >
        <ToggleButton value="pendientes" sx={{ textTransform: 'none' }}>Pendientes</ToggleButton>
        <ToggleButton value="validados" sx={{ textTransform: 'none' }}>Validados</ToggleButton>
        <ToggleButton value="" sx={{ textTransform: 'none' }}>Todos</ToggleButton>
      </ToggleButtonGroup>

      {error && <Alert severity="error">{error}</Alert>}

      {!filas ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      ) : filas.length === 0 ? (
        <Alert severity="info">No hay diagnósticos en esta vista.</Alert>
      ) : (
        <TableContainer component={Card} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell>Moto</TableCell>
                <TableCell>Usuario</TableCell>
                <TableCell>¿Notaba algo?</TableCell>
                <TableCell>Sistema dijo</TableCell>
                <TableCell>Mecánico dijo</TableCell>
                <TableCell align="center">Coincide</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filas.map((d) => {
                const ok = coincide(d)
                return (
                  <TableRow key={d.id_diagnostico} hover>
                    <TableCell>{d.id_diagnostico}</TableCell>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                      {new Date(d.fecha_diagnostico).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {d.marca} {d.modelo}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {d.cilindraje} cc · {d.anio}
                        {d.kilometraje != null ? ` · ${d.kilometraje.toLocaleString()} km` : ''}
                      </Typography>
                      {d.notas && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          «{d.notas}»
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">{d.email_usuario}</Typography>
                    </TableCell>
                    <TableCell>
                      {d.notaba_sintomas === 'si' ? 'Sí' : d.notaba_sintomas === 'no' ? 'No' : '—'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={d.resultado === 'anomalia' ? 'warning' : 'success'}
                        label={`${d.resultado === 'anomalia' ? 'Anomalía' : 'Normal'} · ${d.confianza.toFixed(0)} %`}
                      />
                    </TableCell>
                    <TableCell>
                      <ToggleButtonGroup
                        exclusive
                        size="small"
                        value={d.veredicto_mecanico}
                        onChange={(_, v: Veredicto | null) => guardar(d, v)}
                      >
                        <ToggleButton value="sano" color="success" sx={{ textTransform: 'none' }}>Sano</ToggleButton>
                        <ToggleButton value="leve" color="warning" sx={{ textTransform: 'none' }}>Leve</ToggleButton>
                        <ToggleButton value="grave" color="error" sx={{ textTransform: 'none' }}>Grave</ToggleButton>
                      </ToggleButtonGroup>
                    </TableCell>
                    <TableCell align="center">
                      {ok === null ? (
                        '—'
                      ) : ok ? (
                        <CheckCircleIcon titleAccess="Coincide" sx={{ color: 'success.main' }} />
                      ) : (
                        <CancelIcon titleAccess="No coincide" sx={{ color: 'error.light' }} />
                      )}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Stack>
  )
}
