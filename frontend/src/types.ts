export interface Usuario {
  id_usuario: number
  proveedor_oauth: 'google' | 'github'
  id_externo_proveedor: string
  email: string
  nombre: string | null
  fecha_registro: string
  ultimo_acceso: string | null
}
