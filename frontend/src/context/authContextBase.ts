import { createContext } from 'react';

export interface AuthUser {
  id: number;
  username: string;
  role: string;
  student_id: number | null;
}

export interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);
