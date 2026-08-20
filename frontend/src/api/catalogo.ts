import type { Marca, Modelo, ModeloCNN } from '../types'
import { apiFetch } from './client'

export function listarMarcas() {
  return apiFetch<Marca[]>('/marcas')
}

export function listarModelosPorMarca(idMarca: number) {
  return apiFetch<Modelo[]>(`/modelos?id_marca=${idMarca}`)
}

export function obtenerCnnActivo() {
  return apiFetch<ModeloCNN>('/modelos-cnn/activo')
}
