import CancelIcon from '@mui/icons-material/Cancel'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import Accordion from '@mui/material/Accordion'
import AccordionDetails from '@mui/material/AccordionDetails'
import AccordionSummary from '@mui/material/AccordionSummary'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CircularProgress from '@mui/material/CircularProgress'
import MenuItem from '@mui/material/MenuItem'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { BarChart } from '@mui/x-charts/BarChart'
import { useEffect, useState, type ReactNode } from 'react'

import { obtenerEstadisticas, type FiltrosEstadisticas } from '../../api/admin'
import { listarModelosCnn } from '../../api/catalogo'
import { useAuth } from '../../auth/AuthContext'
import { NIVELES_CONFIANZA } from '../../components/EscalaConfianza'
import type { Estadisticas, ModeloCNN } from '../../types'

// Colores de las gráficas (validados para daltonismo y contraste).
// Una sola serie usa el primario de la app; en las comparaciones
// "sin el sistema" va en naranja y "con el sistema" en el primario.
const COLOR_PRINCIPAL = '#6366F1'
const COLOR_SIN_SISTEMA = '#eb6834'

function pct(v: number | null): string {
  return v == null ? '—' : `${Math.round(v)} %`
}

function num(v: number | null, decimales = 1): string {
  return v == null ? '—' : v.toFixed(decimales)
}

function Kpi({ titulo, valor, detalle }: { titulo: string; valor: string; detalle: string }) {
  return (
    <Card variant="outlined" sx={{ p: 2.5 }}>
      <Typography variant="body2" color="text.secondary">
        {titulo}
      </Typography>
      <Typography variant="h4" sx={{ fontWeight: 700, my: 0.5 }}>
        {valor}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {detalle}
      </Typography>
    </Card>
  )
}

// Tarjeta de una pregunta de investigación: la pregunta, la respuesta en una
// frase y la evidencia (gráficas). Siempre muestra en cuántos casos se basa.
function Seccion({
  objetivo,
  pregunta,
  respuesta,
  n,
  vacio,
  children,
}: {
  objetivo: string
  pregunta: string
  respuesta: ReactNode
  n: number
  vacio: string
  children: ReactNode
}) {
  return (
    <Card variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant="overline" color="primary">
        {objetivo}
      </Typography>
      <Typography variant="h6">{pregunta}</Typography>
      {n === 0 ? (
        <Alert severity="info" sx={{ mt: 2 }}>
          {vacio}
        </Alert>
      ) : (
        <>
          <Typography sx={{ mt: 1, mb: 2 }}>{respuesta}</Typography>
          {children}
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            Basado en {n} {n === 1 ? 'caso' : 'casos'}.
          </Typography>
        </>
      )}
    </Card>
  )
}

// Barra de proporción con dos partes (p. ej. coincidió / no coincidió).
function BarraProporcion({ a, b }: { a: number; b: number }) {
  const total = a + b || 1
  return (
    <Box>
      <Box sx={{ display: 'flex', gap: '2px', height: 28, borderRadius: 1, overflow: 'hidden' }}>
        {a > 0 && <Box sx={{ flex: a / total, bgcolor: 'success.main' }} title={`Coincidió: ${a}`} />}
        {b > 0 && <Box sx={{ flex: b / total, bgcolor: 'error.light' }} title={`No coincidió: ${b}`} />}
      </Box>
      <Stack direction="row" spacing={3} sx={{ mt: 1 }}>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
          <CheckCircleIcon fontSize="small" sx={{ color: 'success.main' }} />
          <Typography variant="body2">Coincidió: {a}</Typography>
        </Stack>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
          <CancelIcon fontSize="small" sx={{ color: 'error.light' }} />
          <Typography variant="body2">No coincidió: {b}</Typography>
        </Stack>
      </Stack>
    </Box>
  )
}

function SeccionExactitud({ ex }: { ex: Estadisticas['exactitud'] }) {
  const versiones = ex.por_version.filter((v) => v.n > 0)
  const m = ex.matriz
  return (
    <Seccion
      objetivo="Objetivo específico 1 · Exactitud"
      pregunta="¿Qué tan seguido coincide el sistema con el mecánico?"
      n={ex.n}
      vacio="Aún no hay casos validados. Registra lo que dijo el mecánico en la pestaña «Validar casos»."
      respuesta={
        <>
          El sistema coincidió con el mecánico en <b>{ex.coincidencias} de {ex.n}</b> motos:
          una exactitud del <b>{pct(ex.porcentaje)}</b>.
        </>
      }
    >
      <BarraProporcion a={ex.coincidencias} b={ex.n - ex.coincidencias} />

      {versiones.length > 0 && (
        <>
          <Typography variant="subtitle2" sx={{ mt: 3 }}>
            Exactitud por versión del modelo: en el entrenamiento vs. con motos reales
          </Typography>
          <BarChart
            height={240}
            borderRadius={4}
            xAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: versiones.map((v) => v.version) }]}
            yAxis={[{ min: 0, max: 100, valueFormatter: (v: number) => `${v} %` }]}
            series={[
              {
                label: 'En el entrenamiento',
                data: versiones.map((v) => v.exactitud_entrenamiento),
                color: COLOR_SIN_SISTEMA,
                valueFormatter: (v) => pct(v),
              },
              {
                label: 'Con motos reales (vs. mecánico)',
                data: versiones.map((v) => v.porcentaje),
                color: COLOR_PRINCIPAL,
                valueFormatter: (v) => pct(v),
              },
            ]}
            grid={{ horizontal: true }}
          />
        </>
      )}

      <Accordion disableGutters variant="outlined" sx={{ mt: 2, borderRadius: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Detalle técnico (matriz de confusión y métricas)
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Table size="small" sx={{ maxWidth: 480, mb: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell />
                <TableCell align="center">Sistema: anomalía</TableCell>
                <TableCell align="center">Sistema: normal</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>Mecánico: con falla</TableCell>
                <TableCell align="center">{m.vp} (VP)</TableCell>
                <TableCell align="center">{m.fn} (FN)</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Mecánico: sano</TableCell>
                <TableCell align="center">{m.fp} (FP)</TableCell>
                <TableCell align="center">{m.vn} (VN)</TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell>Precisión</TableCell>
                <TableCell>{num(ex.precision, 3)}</TableCell>
                <TableCell>De las veces que dijo «anomalía», cuántas eran falla real.</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Sensibilidad (recall)</TableCell>
                <TableCell>{num(ex.sensibilidad, 3)}</TableCell>
                <TableCell>De las motos con falla, cuántas detectó.</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Especificidad</TableCell>
                <TableCell>{num(ex.especificidad, 3)}</TableCell>
                <TableCell>De las motos sanas, cuántas dio como normales.</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>F1</TableCell>
                <TableCell>{num(ex.f1, 3)}</TableCell>
                <TableCell>Balance entre precisión y sensibilidad.</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionDetails>
      </Accordion>
    </Seccion>
  )
}

function SeccionDeteccion({ dt }: { dt: Estadisticas['deteccion_temprana'] }) {
  const grupos = [
    { nombre: 'Problema leve', g: dt.leve },
    { nombre: 'Problema grave', g: dt.grave },
  ]
  const ss = dt.sin_sintomas
  return (
    <Seccion
      objetivo="Objetivo específico 2 · Detección temprana"
      pregunta="¿Detecta los problemas cuando todavía son leves?"
      n={dt.leve.n + dt.grave.n}
      vacio="Aún no hay motos validadas con problema leve o grave."
      respuesta={
        <>
          Detectó <b>{dt.leve.detectados} de {dt.leve.n}</b> motos con problema leve (
          {pct(dt.leve.porcentaje)}) y <b>{dt.grave.detectados} de {dt.grave.n}</b> con problema
          grave ({pct(dt.grave.porcentaje)}).
        </>
      }
    >
      <BarChart
        height={240}
        borderRadius={4}
        hideLegend
        xAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: grupos.map((x) => x.nombre) }]}
        // Tope en 110 para que la etiqueta de una barra al 100 % no se corte.
        yAxis={[{ min: 0, max: 110, tickInterval: [0, 25, 50, 75, 100], valueFormatter: (v: number) => `${v} %` }]}
        series={[
          {
            label: 'Detectadas',
            data: grupos.map((x) => x.g.porcentaje),
            color: COLOR_PRINCIPAL,
            barLabelPlacement: 'outside',
            barLabel: (item) =>
              item.value == null ? null : `${grupos[item.dataIndex].g.detectados} de ${grupos[item.dataIndex].g.n}`,
            valueFormatter: (v, { dataIndex }) =>
              `${pct(v)} (${grupos[dataIndex].g.detectados} de ${grupos[dataIndex].g.n})`,
          },
        ]}
        grid={{ horizontal: true }}
      />

      <Box
        sx={{
          mt: 2,
          p: 2,
          borderRadius: 2,
          bgcolor: 'primary.light',
        }}
      >
        <Typography variant="body2">
          {ss.n === 0 ? (
            'Todavía no hay motos con falla en las que el dueño dijera que no notaba nada raro.'
          ) : (
            <>
              En <b>{ss.detectados} de {ss.n}</b> motos con falla cuyo dueño <b>no notaba nada raro</b>,
              el sistema sí detectó el problema ({pct(ss.porcentaje)}).
            </>
          )}
        </Typography>
      </Box>
    </Seccion>
  )
}

function SeccionConfianza({ cu }: { cu: Estadisticas['confianza_usuario'] }) {
  const ayudo = [
    { nombre: 'Sí', n: cu.ayudo_si },
    { nombre: 'Más o menos', n: cu.ayudo_parcial },
    { nombre: 'No', n: cu.ayudo_no },
  ]
  return (
    <Seccion
      objetivo="Objetivo específico 3 · Confianza del usuario"
      pregunta="¿El sistema le da más confianza al usuario para autorizar reparaciones?"
      n={cu.n}
      vacio="Aún no hay encuestas. Se responden al terminar cada diagnóstico."
      respuesta={
        <>
          Con bastante o mucha confianza: <b>{pct(cu.pct_alta_antes)}</b> solo con el mecánico, y{' '}
          <b>{pct(cu.pct_alta_despues)}</b> con el respaldo del sistema.
        </>
      }
    >
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
        <Kpi
          titulo="Confianza promedio sin el sistema"
          valor={num(cu.promedio_antes)}
          detalle="Escala de 1 (nada) a 5 (mucha)"
        />
        <Kpi
          titulo="Confianza promedio con el sistema"
          valor={num(cu.promedio_despues)}
          detalle="Escala de 1 (nada) a 5 (mucha)"
        />
      </Box>

      <Typography variant="subtitle2" sx={{ mt: 3 }}>
        ¿Cuánta confianza tiene para autorizar una reparación?
      </Typography>
      <BarChart
        height={260}
        borderRadius={4}
        xAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: NIVELES_CONFIANZA }]}
        yAxis={[{ tickMinStep: 1, label: 'Usuarios' }]}
        series={[
          { label: 'Solo con el mecánico', data: cu.distribucion_antes, color: COLOR_SIN_SISTEMA },
          { label: 'Con el respaldo del sistema', data: cu.distribucion_despues, color: COLOR_PRINCIPAL },
        ]}
        grid={{ horizontal: true }}
      />

      <Typography variant="subtitle2" sx={{ mt: 3 }}>
        ¿El resultado le ayudó a decidir?
      </Typography>
      <BarChart
        height={170}
        borderRadius={4}
        layout="horizontal"
        hideLegend
        yAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: ayudo.map((a) => a.nombre), width: 90 }]}
        xAxis={[{ tickMinStep: 1, tickNumber: 6 }]}
        series={[
          {
            label: 'Usuarios',
            data: ayudo.map((a) => a.n),
            color: COLOR_PRINCIPAL,
            barLabel: 'value',
            barLabelPlacement: 'outside',
          },
        ]}
      />

      {(cu.promedio_despues_acierto != null || cu.promedio_despues_fallo != null) && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Confianza promedio cuando el sistema acertó: <b>{num(cu.promedio_despues_acierto)}</b> ·
          cuando se equivocó: <b>{num(cu.promedio_despues_fallo)}</b>.
        </Typography>
      )}
    </Seccion>
  )
}

function SeccionUso({ uso, total }: { uso: Estadisticas['uso']; total: number }) {
  return (
    <Seccion
      objetivo="Contexto · Uso del sistema"
      pregunta="¿Con qué motos y cuándo se usó?"
      n={total}
      vacio="Aún no hay diagnósticos."
      respuesta={<>Diagnósticos realizados por cilindraje y por mes.</>}
    >
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
        <BarChart
          height={220}
          borderRadius={4}
          hideLegend
          xAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: uso.por_cilindraje.map((c) => c.etiqueta) }]}
          yAxis={[{ tickMinStep: 1 }]}
          series={[{ label: 'Diagnósticos', data: uso.por_cilindraje.map((c) => c.n), color: COLOR_PRINCIPAL }]}
          grid={{ horizontal: true }}
        />
        <BarChart
          height={220}
          borderRadius={4}
          hideLegend
          xAxis={[{ scaleType: 'band', categoryGapRatio: 0.45, data: uso.por_mes.map((c) => c.etiqueta) }]}
          yAxis={[{ tickMinStep: 1 }]}
          series={[{ label: 'Diagnósticos', data: uso.por_mes.map((c) => c.n), color: COLOR_PRINCIPAL }]}
          grid={{ horizontal: true }}
        />
      </Box>
    </Seccion>
  )
}

export function AdminEstadisticasPage() {
  const { token } = useAuth()
  const [filtros, setFiltros] = useState<FiltrosEstadisticas>({ id_modelo_cnn: '', desde: '', hasta: '' })
  const [cnns, setCnns] = useState<ModeloCNN[]>([])
  const [datos, setDatos] = useState<Estadisticas | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listarModelosCnn()
      .then(setCnns)
      .catch(() => setCnns([]))
  }, [])

  useEffect(() => {
    let activo = true
    obtenerEstadisticas(filtros, token)
      .then((d) => {
        if (!activo) return
        setDatos(d)
        setError(null)
      })
      .catch((e: Error) => activo && setError(e.message))
    return () => {
      activo = false
    }
  }, [filtros, token])

  return (
    <Stack spacing={3}>
      {/* Filtros en una sola fila sobre las gráficas */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <TextField
          select
          size="small"
          label="Versión del modelo"
          value={filtros.id_modelo_cnn}
          onChange={(e) =>
            setFiltros({ ...filtros, id_modelo_cnn: e.target.value === '' ? '' : Number(e.target.value) })
          }
          slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}
          sx={{ minWidth: 220 }}
        >
          <MenuItem value="">Todas</MenuItem>
          {cnns.map((c) => (
            <MenuItem key={c.id_modelo_cnn} value={c.id_modelo_cnn}>
              {c.version}
              {c.activo ? ' (activo)' : ''}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          type="date"
          size="small"
          label="Desde"
          value={filtros.desde}
          onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })}
          slotProps={{ inputLabel: { shrink: true } }}
        />
        <TextField
          type="date"
          size="small"
          label="Hasta"
          value={filtros.hasta}
          onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })}
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}
      {!datos && !error && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {datos && (
        <>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
              gap: 2,
            }}
          >
            <Kpi
              titulo="Exactitud (vs. mecánico)"
              valor={pct(datos.exactitud.porcentaje)}
              detalle={`${datos.exactitud.coincidencias} de ${datos.exactitud.n} coincidieron`}
            />
            <Kpi
              titulo="Problemas leves detectados"
              valor={pct(datos.deteccion_temprana.leve.porcentaje)}
              detalle={`${datos.deteccion_temprana.leve.detectados} de ${datos.deteccion_temprana.leve.n} motos`}
            />
            <Kpi
              titulo="Usuarios con alta confianza"
              valor={pct(datos.confianza_usuario.pct_alta_despues)}
              detalle={`Sin el sistema: ${pct(datos.confianza_usuario.pct_alta_antes)}`}
            />
            <Kpi
              titulo="Casos validados"
              valor={`${datos.resumen.validados} / ${datos.resumen.total_diagnosticos}`}
              detalle={`${datos.resumen.pendientes} pendientes · ${datos.resumen.evaluaciones} encuestas`}
            />
          </Box>

          <SeccionExactitud ex={datos.exactitud} />
          <SeccionDeteccion dt={datos.deteccion_temprana} />
          <SeccionConfianza cu={datos.confianza_usuario} />
          <SeccionUso uso={datos.uso} total={datos.resumen.total_diagnosticos} />
        </>
      )}
    </Stack>
  )
}
