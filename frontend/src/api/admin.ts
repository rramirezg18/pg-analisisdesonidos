import type { DiagnosticoAdmin, Estadisticas, Veredicto } from '../types'
import { apiFetch } from './client'

export interface FiltrosEstadisticas {
  id_modelo_cnn: number | ''
  desde: string
  hasta: string
}

export function obtenerEstadisticas(f: FiltrosEstadisticas, token: string | null) {
  const q = new URLSearchParams()
  if (f.id_modelo_cnn !== '') q.set('id_modelo_cnn', String(f.id_modelo_cnn))
  if (f.desde) q.set('desde', f.desde)
  if (f.hasta) q.set('hasta', f.hasta)
  return apiFetch<Estadisticas>(`/admin/estadisticas?${q}`, {}, token)
}

export function listarDiagnosticosAdmin(
  estado: 'pendientes' | 'validados' | '',
  token: string | null,
) {
  const q = estado ? `?estado=${estado}&limit=500` : '?limit=500'
  return apiFetch<DiagnosticoAdmin[]>(`/admin/diagnosticos${q}`, {}, token)
}

export function registrarVeredicto(
  id: number,
  veredicto: Veredicto | null,
  token: string | null,
) {
  return apiFetch<void>(
    `/admin/diagnosticos/${id}/veredicto`,
    { method: 'PATCH', body: JSON.stringify({ veredicto_mecanico: veredicto }) },
    token,
  )
}
