export interface Usuario {
  id_usuario: number
  proveedor_oauth: 'google' | 'github'
  id_externo_proveedor: string
  email: string
  nombre: string | null
  fecha_registro: string
  ultimo_acceso: string | null
}

export interface Marca {
  id_marca: number
  nombre: string
}

export type Cilindraje = 125 | 150 | 200

export interface Modelo {
  id_modelo: number
  id_marca: number
  nombre: string
  cilindraje: Cilindraje
}

export interface ModeloCNN {
  id_modelo_cnn: number
  version: string
  fecha_entrenamiento: string
  exactitud_validacion: number
  archivo_pesos: string
  descripcion: string | null
  activo: number
}

// Datos de la moto capturados en el paso 1 del wizard.
export interface DatosMoto {
  id_marca: number | ''
  id_modelo: number | ''
  cilindraje: Cilindraje | ''
  anio: number | ''
  kilometraje: number | ''
  notas: string
}

// Nombres resueltos de la moto, para mostrar en los pasos 2 y 3.
export interface MotoResumen {
  marca: string
  modelo: string
  cilindraje: Cilindraje
}

// Diagnóstico persistido que devuelve el backend (con nombres ya resueltos).
export interface Diagnostico {
  id_diagnostico: number
  id_usuario: number
  id_modelo: number
  id_modelo_cnn: number
  anio: number
  kilometraje: number | null
  notas: string | null
  espectrograma_ref: string
  resultado: 'normal' | 'anomalia'
  confianza: number
  fecha_diagnostico: string
  marca: string
  modelo: string
  cilindraje: number
}
