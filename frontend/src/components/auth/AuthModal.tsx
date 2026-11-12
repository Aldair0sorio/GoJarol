import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { X, GraduationCap, User, Sparkles, CheckCircle2 } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { switchRole, updateUser } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [selectedRole, setSelectedRole] = useState<'student' | 'teacher'>('student');
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('3° de Secundaria');
  const [school, setSchool] = useState('Secundaria Técnica #26 · Veracruz');
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);

    if (name.trim()) {
      updateUser({
        name: name.trim(),
        grade: selectedRole === 'student' ? grade : undefined,
        school: school.trim(),
      });
    }

    switchRole(selectedRole);

    setTimeout(() => {
      setSubmitted(false);
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-sm w-full p-5 border border-[#E8E5DC] shadow-2xl flex flex-col gap-3.5 animate-scaleUp">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img
              src="/mascot/jarol-crab.png"
              alt="Jarol"
              className="w-8 h-8 rounded-full bg-[#126B73]/10 p-0.5 object-contain"
            />
            <h2 className="font-display font-extrabold text-base text-[#0A1D2C]">
              {mode === 'login' ? 'Iniciar Sesión en Go Jarol' : 'Registro de Usuario'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Selector de Rol */}
        <div className="flex gap-2 p-1 bg-white rounded-xl border border-[#E8E5DC]">
          <button
            type="button"
            onClick={() => setSelectedRole('student')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all ${
              selectedRole === 'student'
                ? 'bg-[#126B73] text-white shadow-xs'
                : 'text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Soy Alumno</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedRole('teacher')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all ${
              selectedRole === 'teacher'
                ? 'bg-[#E76D55] text-white shadow-xs'
                : 'text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Soy Maestro</span>
          </button>
        </div>

        {submitted ? (
          <div className="py-6 flex flex-col items-center justify-center gap-2 text-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-bounce" />
            <span className="font-display font-bold text-sm text-[#0A1D2C]">
              ¡Bienvenido a Go Jarol!
            </span>
            <span className="text-xs text-[#596B72]">
              Configurando tu espacio pedagógico...
            </span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-2.5">
            <div>
              <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                Nombre Completo
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={selectedRole === 'student' ? 'Ej. Emiliano Valdés' : 'Ej. Prof. Laura Mendoza'}
                className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
              />
            </div>

            {selectedRole === 'student' && (
              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Nivel Escolar
                </label>
                <select
                  value={grade}
                  onChange={(e) => setGrade(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none font-display"
                >
                  <option value="1° de Secundaria">1° de Secundaria</option>
                  <option value="2° de Secundaria">2° de Secundaria</option>
                  <option value="3° de Secundaria">3° de Secundaria</option>
                  <option value="Bachillerato · 1er Semestre">Bachillerato · 1er Semestre</option>
                  <option value="Bachillerato · 2do Semestre">Bachillerato · 2do Semestre</option>
                </select>
              </div>
            )}

            <div>
              <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                Escuela / Municipio en Veracruz
              </label>
              <input
                type="text"
                value={school}
                onChange={(e) => setSchool(e.target.value)}
                placeholder="Ej. Secundaria Técnica #26 · Boca del Río"
                className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className={`w-full py-2.5 mt-2 rounded-full font-display font-bold text-xs text-white shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                selectedRole === 'student' ? 'bg-[#126B73]' : 'bg-[#E76D55] shadow-[0_3px_0_#711707]'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{mode === 'login' ? 'Entrar a la Plataforma' : 'Completar Registro'}</span>
            </button>

            <div className="text-center mt-1">
              <button
                type="button"
                onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                className="text-[11px] text-[#126B73] font-semibold hover:underline"
              >
                {mode === 'login' ? '¿No tienes cuenta? Regístrate aquí' : '¿Ya tienes cuenta? Inicia sesión'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
