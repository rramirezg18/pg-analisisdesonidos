// Base de la API. En producción el reverse proxy sirve todo en el mismo origen,
// así que "/api" funciona. Se puede sobreescribir con VITE_API_URL en desarrollo.
export const API_URL = import.meta.env.VITE_API_URL ?? '/api'
