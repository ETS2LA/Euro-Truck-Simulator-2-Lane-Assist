"use client";

import { createContext, useContext, useState, ReactNode } from 'react';
import { login_token, username as initial_username } from '@/apis/account';

interface AuthState {
  token: string;
  username: string;
  setToken: (token: string) => void;
  setUsername: (username: string) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(login_token);
  const [username, setUsername] = useState(initial_username);

  const value = {
    token,
    username,
    setToken,
    setUsername,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}