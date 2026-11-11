import React, { createContext, useContext, useState } from 'react';
import type { User, UserRole } from '../types/auth';
import { MOCK_STUDENT, MOCK_TEACHER } from '../services/mockData';

interface AuthContextType {
  user: User;
  role: UserRole;
  switchRole: (newRole: UserRole) => void;
  addXP: (amount: number) => void;
  updateUser: (fields: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<UserRole>('student');
  const [studentUser, setStudentUser] = useState<User>(MOCK_STUDENT);
  const [teacherUser, setTeacherUser] = useState<User>(MOCK_TEACHER);

  const currentUser = role === 'student' ? studentUser : teacherUser;

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
  };

  const addXP = (amount: number) => {
    if (role === 'student') {
      setStudentUser((prev) => ({
        ...prev,
        xp: (prev.xp || 0) + amount,
      }));
    }
  };

  const updateUser = (fields: Partial<User>) => {
    if (role === 'student') {
      setStudentUser((prev) => ({ ...prev, ...fields }));
    } else {
      setTeacherUser((prev) => ({ ...prev, ...fields }));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        role,
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
