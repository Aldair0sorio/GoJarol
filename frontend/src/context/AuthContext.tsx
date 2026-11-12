import React, { createContext, useContext, useState } from 'react';
import type { User, UserRole } from '../types/auth';

export const GUEST_USER: User = {
  id: 'guest',
  name: 'Estudiante Invitado',
  email: '',
  role: 'student',
  grade: '3° de Secundaria',
  school: 'Secundaria Técnica #26 · Veracruz',
  avatarUrl: '/mascot/jarol-crab.png',
  xp: 0,
  streakDays: 0,
};

interface AuthContextType {
  user: User;
  role: UserRole;
  isAuthenticated: boolean;
  isGoogleUser: boolean;
  login: (user: User, token?: string) => void;
  loginWithGoogle: (googleUser: Partial<User>) => void;
  logout: () => void;
  switchRole: (newRole: UserRole) => void;
  addXP: (amount: number) => void;
  updateUser: (fields: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    const savedUser = localStorage.getItem('jarol_current_user');
    const savedToken = localStorage.getItem('jarol_token');
    return Boolean(savedUser && savedToken);
  });

  const [currentUser, setCurrentUser] = useState<User>(() => {
    const savedUser = localStorage.getItem('jarol_current_user');
    const savedToken = localStorage.getItem('jarol_token');
    if (savedUser && savedToken) {
      try {
        return JSON.parse(savedUser);
      } catch {
        // fallback a guest
      }
    }
    return GUEST_USER;
  });

  const [role, setRole] = useState<UserRole>(() => {
    return currentUser.role || 'student';
  });

  const [isGoogleUser, setIsGoogleUser] = useState<boolean>(() => {
    return Boolean(
      currentUser.email &&
        (currentUser.email.endsWith('@gmail.com') ||
          localStorage.getItem('jarol_is_google') === 'true')
    );
  });

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
    setCurrentUser((prev) => {
      const updated = { ...prev, role: newRole };
      if (isAuthenticated) {
        localStorage.setItem('jarol_current_user', JSON.stringify(updated));
      }
      return updated;
    });
  };

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
    setCurrentUser(newUser);
    setRole(newUser.role);
    setIsAuthenticated(true);
    setIsGoogleUser(Boolean(newUser.email?.endsWith('@gmail.com')));
    localStorage.setItem('jarol_current_user', JSON.stringify(newUser));
    if (token) {
      localStorage.setItem('jarol_token', token);
    }
  };

  const loginWithGoogle = (googleUser: Partial<User>) => {
    const updatedUser: User = {
      id: googleUser.id || `guser_${Date.now()}`,
      name: googleUser.name || 'Estudiante Google',
      email: googleUser.email || '',
      role: googleUser.role || role,
      grade: googleUser.grade || '3° de Secundaria',
      school: googleUser.school || 'Secundaria Técnica #26 · Veracruz',
      avatarUrl: googleUser.avatarUrl || '/mascot/jarol-crab.png',
      xp: googleUser.xp ?? 320,
      streakDays: googleUser.streakDays ?? 4,
    };

    setCurrentUser(updatedUser);
    setRole(updatedUser.role);
    setIsAuthenticated(true);
    setIsGoogleUser(true);
    localStorage.setItem('jarol_is_google', 'true');
    localStorage.setItem('jarol_current_user', JSON.stringify(updatedUser));
  };

  const logout = () => {
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

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        role,
        isAuthenticated,
        isGoogleUser,
        login,
        loginWithGoogle,
        logout,
        switchRole,
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
