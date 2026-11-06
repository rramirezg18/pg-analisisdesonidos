import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminLayout } from './components/AdminLayout'
import { AdminRoute } from './components/AdminRoute'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AcercaDePage } from './pages/AcercaDePage'
import { AuthCallbackPage } from './pages/AuthCallbackPage'
import { HistorialPage } from './pages/HistorialPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { PerfilPage } from './pages/PerfilPage'
import { DiagnosticoDetallePage } from './pages/diagnostico/DiagnosticoDetallePage'
import { NuevoDiagnosticoPage } from './pages/diagnostico/NuevoDiagnosticoPage'

// El panel de admin se carga aparte: la librería de gráficas no entra en el
// bundle que descargan los usuarios normales.
const AdminEstadisticasPage = lazy(() =>
  import('./pages/admin/AdminEstadisticasPage').then((m) => ({ default: m.AdminEstadisticasPage })),
)
const AdminValidacionPage = lazy(() =>
  import('./pages/admin/AdminValidacionPage').then((m) => ({ default: m.AdminValidacionPage })),
)

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/historial" element={<HistorialPage />} />
          <Route path="/perfil" element={<PerfilPage />} />
        </Route>
        <Route path="/diagnostico/nuevo" element={<NuevoDiagnosticoPage />} />
        <Route path="/diagnostico/:id" element={<DiagnosticoDetallePage />} />
        <Route path="/acerca-de" element={<AcercaDePage />} />

        {/* Panel de investigación: solo correos en ADMIN_EMAILS */}
        <Route element={<AdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<Suspense><AdminEstadisticasPage /></Suspense>} />
            <Route path="/admin/validar" element={<Suspense><AdminValidacionPage /></Suspense>} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
