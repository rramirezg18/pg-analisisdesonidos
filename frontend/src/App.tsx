import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthCallbackPage } from './pages/AuthCallbackPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
