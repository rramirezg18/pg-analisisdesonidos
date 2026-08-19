import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

import { apiFetch } from '../api/client'
import { API_URL } from '../config'
import type { Usuario } from '../types'

const TOKEN_KEY = 'motorscan_token'

interface AuthContextValue {
  usuario: Usuario | null
  token: string | null
  cargando: boolean
  login: (token: string) => Promise<void>
  logout: () => void
  loginConGithub: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY),
  )
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [cargando, setCargando] = useState(true)

  // Al montar (o al cambiar el token) validamos la sesión contra el backend.
  useEffect(() => {
    if (!token) {
      setUsuario(null)
      setCargando(false)
      return
    }
    let activo = true
    setCargando(true)
    apiFetch<Usuario>('/usuarios/me', {}, token)
      .then((u) => {
        if (activo) setUsuario(u)
      })
      .catch(() => {
        if (activo) {
          localStorage.removeItem(TOKEN_KEY)
          setToken(null)
          setUsuario(null)
        }
      })
      .finally(() => {
        if (activo) setCargando(false)
      })
    return () => {
      activo = false
    }
  }, [token])

  async function login(nuevoToken: string) {
    localStorage.setItem(TOKEN_KEY, nuevoToken)
    setToken(nuevoToken)
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUsuario(null)
  }

  function loginConGithub() {
    window.location.href = `${API_URL}/auth/github/login`
  }

  return (
    <AuthContext.Provider
      value={{ usuario, token, cargando, login, logout, loginConGithub }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return ctx
}
