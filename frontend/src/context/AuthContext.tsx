import React, { createContext, useContext, useState } from 'react';
import type { User, UserRole } from '../types/auth';
import { apiService, getAuthToken } from '../services/api';

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
  loginWithGoogle: (googleUser: Partial<User>, token?: string) => void;
  logout: () => void;
  switchRole: (newRole: UserRole) => Promise<void>;
  addXP: (amount: number) => void;
  updateUser: (fields: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    const savedUser = localStorage.getItem('jarol_current_user');
    const savedToken = localStorage.getItem('jarol_token');
    return Boolean(savedUser && (savedToken || localStorage.getItem('jarol_is_google') === 'true'));
  });

  const [currentUser, setCurrentUser] = useState<User>(() => {
    const savedUser = localStorage.getItem('jarol_current_user');
    if (savedUser) {
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

  // Si hay una sesión demo o Google vieja sin token DRF real, sincronizar automáticamente con backend
  React.useEffect(() => {
    const token = getAuthToken();
    if (!isAuthenticated) return;
    if (token && token.startsWith('jarol_demo_')) {
      const profile: 'student' | 'teacher' =
        currentUser.role === 'teacher' ? 'teacher' : 'student';
      apiService.loginDemo(profile).then((res) => {
        if (res.success && res.user) {
          setCurrentUser(res.user);
          setRole(res.user.role);
          localStorage.setItem('jarol_current_user', JSON.stringify(res.user));
        }
      });
    } else if (
      (!token || token.startsWith('jarol_gtoken_') || token.startsWith('jarol_token_')) &&
      currentUser.email
    ) {
      apiService
        .loginWithGoogle({
          email: currentUser.email,
          name: currentUser.name,
          role: currentUser.role === 'teacher' ? 'teacher' : 'student',
          grade: currentUser.grade,
          school: currentUser.school,
        })
        .then((res) => {
          if (res.success && res.user && res.token && !res.token.startsWith('jarol_')) {
            setCurrentUser(res.user);
            setRole(res.user.role);
            localStorage.setItem('jarol_current_user', JSON.stringify(res.user));
          }
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const switchRole = async (newRole: UserRole) => {
    const normalized: 'student' | 'teacher' = newRole === 'teacher' ? 'teacher' : 'student';
    setRole(normalized);
    setCurrentUser((prev) => {
      const updated = { ...prev, role: normalized };
      if (isAuthenticated) {
        localStorage.setItem('jarol_current_user', JSON.stringify(updated));
      }
      return updated;
    });
    if (isAuthenticated) {
      await apiService.switchBackendRole(normalized);
    }
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

  const loginWithGoogle = (googleUser: Partial<User>, token?: string) => {
    const updatedUser: User = {
      id: googleUser.id || `guser_${Date.now()}`,
      name: googleUser.name || 'Estudiante Google',
      email: googleUser.email || '',
      role: googleUser.role || role,
      grade: googleUser.grade || '3° de Secundaria',
      school: googleUser.school || 'Secundaria Técnica #26 · Veracruz',
      avatarUrl: googleUser.avatarUrl || '/mascot/jarol-crab.png',
      xp: googleUser.xp ?? 0,
      streakDays: googleUser.streakDays ?? 1,
    };

    setCurrentUser(updatedUser);
    setRole(updatedUser.role);
    setIsAuthenticated(true);
    setIsGoogleUser(true);
    localStorage.setItem('jarol_is_google', 'true');
    localStorage.setItem('jarol_current_user', JSON.stringify(updatedUser));
    if (token) {
      localStorage.setItem('jarol_token', token);
    }
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
