import React, { createContext, useContext, useState } from 'react';
import type { User, UserRole } from '../types/auth';
import { MOCK_STUDENT, MOCK_TEACHER } from '../services/mockData';

interface AuthContextType {
  user: User;
  role: UserRole;
  isGoogleUser: boolean;
  switchRole: (newRole: UserRole) => void;
  addXP: (amount: number) => void;
  updateUser: (fields: Partial<User>) => void;
  loginWithGoogle: (googleUser: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<UserRole>('student');
  const [isGoogleUser, setIsGoogleUser] = useState<boolean>(false);
  const [studentUser, setStudentUser] = useState<User>(() => {
    const saved = localStorage.getItem('jarol_student_user');
    return saved ? JSON.parse(saved) : MOCK_STUDENT;
  });
  const [teacherUser, setTeacherUser] = useState<User>(() => {
    const saved = localStorage.getItem('jarol_teacher_user');
    return saved ? JSON.parse(saved) : MOCK_TEACHER;
  });

  const currentUser = role === 'student' ? studentUser : teacherUser;

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
  };

  const addXP = (amount: number) => {
    if (role === 'student') {
      setStudentUser((prev) => {
        const updated = {
          ...prev,
          xp: (prev.xp || 0) + amount,
        };
        localStorage.setItem('jarol_student_user', JSON.stringify(updated));
        return updated;
      });
    }
  };

  const updateUser = (fields: Partial<User>) => {
    if (role === 'student') {
      setStudentUser((prev) => {
        const updated = { ...prev, ...fields };
        localStorage.setItem('jarol_student_user', JSON.stringify(updated));
        return updated;
      });
    } else {
      setTeacherUser((prev) => {
        const updated = { ...prev, ...fields };
        localStorage.setItem('jarol_teacher_user', JSON.stringify(updated));
        return updated;
      });
    }
  };

  const loginWithGoogle = (googleUser: Partial<User>) => {
    setIsGoogleUser(true);
    if (googleUser.role) {
      setRole(googleUser.role);
    }
    const targetRole = googleUser.role || role;
    if (targetRole === 'student') {
      setStudentUser((prev) => {
        const updated = { ...prev, ...googleUser };
        localStorage.setItem('jarol_student_user', JSON.stringify(updated));
        return updated;
      });
    } else {
      setTeacherUser((prev) => {
        const updated = { ...prev, ...googleUser };
        localStorage.setItem('jarol_teacher_user', JSON.stringify(updated));
        return updated;
      });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        role,
        isGoogleUser,
        switchRole,
        addXP,
        updateUser,
        loginWithGoogle,
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
