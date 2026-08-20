import { API_URL } from '../config'
import type { Cilindraje } from '../types'
import { ApiError } from './client'

// Lo que devuelve el endpoint de inferencia del backend.
export interface AnalisisResultado {
  clase: 'normal' | 'anomalia'
  confianza: number // 0..100
  valor_raw: number // salida cruda del sigmoid (0..1)
}

// Envía el AUDIO crudo (no el espectrograma) + cilindraje al backend, que
// regenera el espectrograma con librosa y corre el CNN. El audio no se guarda.
export async function analizarAudio(
  audio: Blob,
  nombreArchivo: string,
  cilindraje: Cilindraje,
  token: string | null,
): Promise<AnalisisResultado> {
  const form = new FormData()
  form.append('audio', audio, nombreArchivo)
  form.append('cilindraje', String(cilindraje))

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
