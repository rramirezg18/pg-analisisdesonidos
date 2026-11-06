export interface Usuario {
  id_usuario: number
  proveedor_oauth: 'google' | 'github'
  id_externo_proveedor: string
  email: string
  nombre: string | null
  fecha_registro: string
  ultimo_acceso: string | null
  es_admin: boolean
}

export interface Marca {
  id_marca: number
  nombre: string
}

export type Cilindraje = 125 | 150 | 155 | 160 | 180 | 190 | 200

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
  // Preguntas previas al resultado (datos para la tesis, OE2 y OE3).
  notaba_sintomas: 'si' | 'no' | ''
  confianza_antes: number | ''
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
  notaba_sintomas: 'si' | 'no' | null
}

export type Veredicto = 'sano' | 'leve' | 'grave'

// Diagnóstico visto por el admin, con el veredicto del mecánico.
export interface DiagnosticoAdmin extends Diagnostico {
  email_usuario: string
  veredicto_mecanico: Veredicto | null
  fecha_validacion: string | null
  tiene_evaluacion: boolean
}

// Encuesta del usuario al ver el resultado (escala 1..5).
export interface EvaluacionNueva {
  confianza_antes: number
  confianza_despues: number
  ayudo_decidir: 'si' | 'parcial' | 'no'
}

// ---- Panel de investigación (GET /admin/estadisticas) ----
// Porcentajes de 0 a 100; null cuando aún no hay casos.

export interface GrupoDeteccion {
  n: number
  detectados: number
  porcentaje: number | null
  confianza_promedio: number | null
}

export interface Conteo {
  etiqueta: string
  n: number
}

export interface Estadisticas {
  resumen: {
    total_diagnosticos: number
    validados: number
    pendientes: number
    evaluaciones: number
    usuarios: number
  }
  exactitud: {
    n: number
    coincidencias: number
    porcentaje: number | null
    matriz: { vp: number; fn: number; fp: number; vn: number }
    precision: number | null
    sensibilidad: number | null
    especificidad: number | null
    f1: number | null
    por_version: {
      version: string
      exactitud_entrenamiento: number
      n: number
      porcentaje: number | null
    }[]
  }
  deteccion_temprana: {
    leve: GrupoDeteccion
    grave: GrupoDeteccion
    sin_sintomas: GrupoDeteccion
  }
  confianza_usuario: {
    n: number
    distribucion_antes: number[]
    distribucion_despues: number[]
    promedio_antes: number | null
    promedio_despues: number | null
    pct_alta_antes: number | null
    pct_alta_despues: number | null
    ayudo_si: number
    ayudo_parcial: number
    ayudo_no: number
    promedio_despues_acierto: number | null
    promedio_despues_fallo: number | null
  }
  uso: {
    por_cilindraje: Conteo[]
    por_mes: Conteo[]
  }
}
