import { API_URL } from '../config'
import type { DatosMoto, Diagnostico } from '../types'
import { ApiError, apiFetch } from './client'

// URL pública de la imagen del espectrograma (servida estáticamente por el backend).
export function urlEspectrograma(ref: string): string {
  return `${API_URL}/media/${ref}`
}

// Envía el AUDIO crudo + los datos de la moto. El backend regenera el
// espectrograma con librosa, corre el CNN, guarda la IMAGEN (no el audio) y
// devuelve el diagnóstico persistido.
export async function analizarAudio(
  audio: Blob,
  nombreArchivo: string,
  datos: DatosMoto,
  token: string | null,
): Promise<Diagnostico> {
  const form = new FormData()
  form.append('audio', audio, nombreArchivo)
  form.append('id_modelo', String(datos.id_modelo))
  form.append('anio', String(datos.anio))
  if (datos.kilometraje !== '') form.append('kilometraje', String(datos.kilometraje))
  if (datos.notas.trim()) form.append('notas', datos.notas.trim())

  // Nota: NO fijamos Content-Type; el navegador pone el boundary de multipart.
  const headers = new Headers()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const res = await fetch(`${API_URL}/diagnosticos/analizar`, {
    method: 'POST',
    body: form,
    headers,
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      detail = (await res.json()).detail ?? detail
    } catch {
      // sin cuerpo JSON
    }
    throw new ApiError(res.status, detail)
  }
  return res.json()
}

export function listarMisDiagnosticos(token: string | null) {
  return apiFetch<Diagnostico[]>('/diagnosticos/mis', {}, token)
}

export function obtenerDiagnostico(id: number, token: string | null) {
  return apiFetch<Diagnostico>(`/diagnosticos/${id}`, {}, token)
}
