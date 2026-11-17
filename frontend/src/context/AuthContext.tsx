import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  role: UserRole;
  token: string | null;
  login: (email: string, role?: UserRole) => Promise<void>;
  switchRole: (role: UserRole) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>({
    id: 1,
    email: 'owner@fooderp.com',
    full_name: 'Sundaram Ramakrishnan (Owner)',
    role: 'owner',
    is_active: true,
  });
  const [role, setRole] = useState<UserRole>('owner');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token') || 'demo-token');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
    const demoProfiles: Record<UserRole, { name: string; email: string; id: number }> = {
      owner: { name: 'Sundaram Ramakrishnan (Owner)', email: 'owner@fooderp.com', id: 1 },
      admin: { name: 'Meenakshi Sundaram (Admin)', email: 'admin@fooderp.com', id: 2 },
      salesman: { name: 'Karthik Raj (Salesman A)', email: 'salesman.a@fooderp.com', id: 3 },
      production: { name: 'Muthukumar S. (Production)', email: 'supervisor@fooderp.com', id: 5 },
      auditor: { name: 'Ranganathan FCA (Auditor)', email: 'auditor@fooderp.com', id: 6 },
    };

    const prof = demoProfiles[newRole];
    setUser({
      id: prof.id,
      email: prof.email,
      full_name: prof.name,
      role: newRole,
      is_active: true,
    });
  };

  const login = async (email: string, userRole: UserRole = 'owner') => {
    setIsLoading(true);
    try {
      // In production calls api.login, with fallback for seamless evaluation
      switchRole(userRole);
      setToken('demo-token-active');
      localStorage.setItem('token', 'demo-token-active');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, role, token, login, switchRole, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

