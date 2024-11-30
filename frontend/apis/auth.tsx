// Create new file: hooks/useAuth.ts
import { login_token, username } from '@/apis/account'
import { create } from 'zustand'

interface AuthState {
  token: string
  username: string
  setToken: (token: string) => void
  setUsername: (username: string) => void
}

export const useAuth = create<AuthState>((set) => ({
  token: login_token,
  username: username,
  setToken: (token) => set({ token }),
  setUsername: (username) => set({ username })
}))