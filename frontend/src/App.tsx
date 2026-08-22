import { Navigate, Route, Routes } from 'react-router-dom'

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
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
