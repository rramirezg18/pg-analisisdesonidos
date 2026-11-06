import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

// Va dentro de <ProtectedRoute>: el usuario ya está cargado. Si no es admin,
// vuelve al inicio (el backend igual responde 403 en /admin).
export function AdminRoute() {
  const { usuario } = useAuth()
  if (!usuario?.es_admin) {
    return <Navigate to="/" replace />
  }
  return <Outlet />
}
