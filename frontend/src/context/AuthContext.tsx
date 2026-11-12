import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProfile, profileToUser, endSession, ProfileApiError, isBackendToken, getAuthToken } from '../services/api';
import type { User, UserRole } from '../types/auth';

export const GUEST_USER: User = {
  id: 'guest',
  name: 'Estudiante Invitado',
  email: '',
  role: 'student',
  grade: '3° de Secundaria',
  school: 'Secundaria Técnica #26 · Veracruz',
  avatarUrl: '/mascot/jarol-crab.webp',
  xp: 0,
  streakDays: 0,
};

interface AuthContextType {
  user: User;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  isGoogleUser: boolean;
  login: (user: User, token?: string) => void;
  logout: () => Promise<void>;
  addXP: (amount: number) => void;
  updateUser: (fields: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User>(GUEST_USER);
  const [role, setRole] = useState<UserRole>('student');
  const [isGoogleUser, setIsGoogleUser] = useState(false);

  const addXP = (amount: number) => {
    if (role === 'student') {
      setCurrentUser((prev) => {
        const updated = {
          ...prev,
          xp: (prev.xp || 0) + amount,
        };
        if (isAuthenticated) {
          localStorage.setItem('jarol_current_user', JSON.stringify(updated));
        }
        return updated;
      });
    }
  };

  const updateUser = (fields: Partial<User>) => {
    setCurrentUser((prev) => {
      const updated = { ...prev, ...fields };
      if (isAuthenticated) {
        localStorage.setItem('jarol_current_user', JSON.stringify(updated));
      }
      return updated;
    });
  };

  const login = (newUser: User, token?: string) => {
    if (!isBackendToken(token)) throw new Error('No se recibió una sesión válida del servidor.');
    setCurrentUser(newUser);
    setRole(newUser.role);
    setIsAuthenticated(true);
    setIsGoogleUser(Boolean(newUser.email?.endsWith('@gmail.com')));
    localStorage.setItem('jarol_current_user', JSON.stringify(newUser));
    if (token) {
      localStorage.setItem('jarol_token', token);
    }
  };

  const clearSession = () => {
    localStorage.removeItem('jarol_current_user');
    localStorage.removeItem('jarol_token');
    localStorage.removeItem('jarol_is_google');
    localStorage.removeItem('jarol_student_user');
    localStorage.removeItem('jarol_teacher_user');
    setCurrentUser(GUEST_USER);
    setRole('student');
    setIsAuthenticated(false);
    setIsGoogleUser(false);
  };

  const logout = async () => {
    try { await endSession(); }
    catch (error) { if (!(error instanceof ProfileApiError && error.status === 401)) throw error; }
    clearSession();
  };

  useEffect(() => {
    const token = getAuthToken();
    if (!token) { setIsLoading(false); return; }
    if (!isBackendToken(token)) { clearSession(); setIsLoading(false); return; }
    let active = true;
    getProfile().then(profile => {
      if (!active || getAuthToken() !== token) return;
      const realUser = profileToUser(profile);
      setCurrentUser(realUser); setRole(realUser.role); setIsAuthenticated(true);
      localStorage.setItem('jarol_current_user', JSON.stringify(realUser));
      setIsGoogleUser(localStorage.getItem('jarol_is_google') === 'true');
    }).catch(error => {
      if (active && getAuthToken() === token && error instanceof ProfileApiError && error.status === 401) clearSession();
    }).finally(() => { if (active) setIsLoading(false); });
    return () => { active = false; };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        role,
        isAuthenticated,
        isLoading,
        isGoogleUser,
        login,
        logout,
        addXP,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};
