import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import { X, GraduationCap, User, Sparkles, CheckCircle2, ChevronRight, Loader2 } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { switchRole, updateUser, loginWithGoogle } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [selectedRole, setSelectedRole] = useState<'student' | 'teacher'>('student');
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('3° de Secundaria');
  const [school, setSchool] = useState('Secundaria Técnica #26 · Veracruz');
  const [submitted, setSubmitted] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showGoogleAccounts, setShowGoogleAccounts] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [googleSuccessName, setGoogleSuccessName] = useState('');

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

  const handleGoogleAccountSelect = async (account: {
    name: string;
    email: string;
    picture?: string;
    role: 'student' | 'teacher';
    grade?: string;
    school?: string;
  }) => {
    setGoogleLoading(true);
    setGoogleSuccessName(account.name);

    try {
      // Llamada al endpoint backend de Google Auth
      await apiService.loginWithGoogle({
        email: account.email,
        name: account.name,
        picture: account.picture,
        role: account.role,
        grade: account.grade,
        school: account.school,
      });

      // Actualizar contexto de aplicación
      loginWithGoogle({
        name: account.name,
        email: account.email,
        role: account.role,
        grade: account.grade,
        school: account.school,
        avatarUrl: account.picture,
      });

      setGoogleLoading(false);
      setSubmitted(true);

      setTimeout(() => {
        setSubmitted(false);
        setShowGoogleAccounts(false);
        onClose();
      }, 1200);
    } catch {
      setGoogleLoading(false);
    }
  };

  const handleCustomGoogleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customGoogleEmail.trim() || !customGoogleEmail.includes('@')) return;

    const inferredName = customGoogleEmail.split('@')[0].replace(/[._-]/g, ' ');
    const capitalized = inferredName.charAt(0).toUpperCase() + inferredName.slice(1);

    handleGoogleAccountSelect({
      name: capitalized,
      email: customGoogleEmail.trim(),
      role: selectedRole,
      grade: selectedRole === 'student' ? grade : undefined,
      school: school,
      picture: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
    });
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
            className="w-7 h-7 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:bg-[#E8E5DC]/50 cursor-pointer transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Selector de Rol */}
        <div className="flex gap-2 p-1 bg-white rounded-xl border border-[#E8E5DC]">
          <button
            type="button"
            onClick={() => setSelectedRole('student')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
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
            className={`flex-1 py-1.5 rounded-lg text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
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
          <div className="py-6 flex flex-col items-center justify-center gap-2 text-center animate-fadeIn">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-bounce" />
            <span className="font-display font-bold text-sm text-[#0A1D2C]">
              ¡Bienvenido{googleSuccessName ? `, ${googleSuccessName}` : ''}! 🦀
            </span>
            <span className="text-xs text-[#596B72]">
              Sesión iniciada con éxito. Configurando tu espacio pedagógico...
            </span>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {/* BOTÓN OFICIAL DE GOOGLE */}
            {!showGoogleAccounts ? (
              <button
                type="button"
                onClick={() => setShowGoogleAccounts(true)}
                disabled={googleLoading}
                className="w-full py-2.5 px-3.5 rounded-xl bg-white border border-[#D5D2C7] hover:border-[#126B73] hover:shadow-md font-display font-bold text-xs text-[#0A1D2C] transition-all flex items-center justify-center gap-3 cursor-pointer group active:scale-[0.99]"
              >
                {googleLoading ? (
                  <Loader2 className="w-4 h-4 text-[#126B73] animate-spin" />
                ) : (
                  <svg className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                    <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.27 21.41 7.34 24 12 24z"/>
                    <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.17 0 9.97 0 12s.45 3.83 1.25 5.42l4.03-3.15z"/>
                    <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.27 2.59 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                  </svg>
                )}
                <span>Continuar con Google</span>
              </button>
            ) : (
              /* PANEL DE SELECCIÓN DE CUENTA GOOGLE */
              <div className="p-3 bg-white rounded-xl border border-[#D5D2C7] flex flex-col gap-2.5 animate-fadeIn">
                <div className="flex items-center justify-between pb-1 border-b border-[#E8E5DC]">
                  <span className="text-[11px] font-display font-bold text-[#0A1D2C] flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                      <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.27 21.41 7.34 24 12 24z"/>
                      <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.17 0 9.97 0 12s.45 3.83 1.25 5.42l4.03-3.15z"/>
                      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.27 2.59 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                    </svg>
                    Elige tu cuenta de Google
                  </span>
                  <button
                    type="button"
                    onClick={() => setShowGoogleAccounts(false)}
                    className="text-[10px] text-[#596B72] hover:text-[#0A1D2C] underline cursor-pointer"
                  >
                    Volver
                  </button>
                </div>

                {/* Cuenta de Alumno SEV */}
                <button
                  type="button"
                  onClick={() =>
                    handleGoogleAccountSelect({
                      name: 'Emiliano Valdés',
                      email: 'emiliano.valdes@estudiantes.sev.gob.mx',
                      role: 'student',
                      grade: '3° de Secundaria',
                      school: 'Secundaria Técnica #26 · Boca del Río',
                      picture: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
                    })
                  }
                  className="p-2 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors border border-transparent hover:border-[#E8E5DC] cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <img
                      src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80"
                      alt="Emiliano"
                      className="w-7 h-7 rounded-full object-cover"
                    />
                    <div>
                      <div className="text-[11px] font-display font-bold text-[#0A1D2C] flex items-center gap-1">
                        Emiliano Valdés
                        <span className="text-[9px] bg-[#126B73]/10 text-[#126B73] px-1 py-0.2 rounded font-mono">SEV Alumno</span>
                      </div>
                      <div className="text-[10px] text-[#596B72]">emiliano.valdes@estudiantes.sev.gob.mx</div>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-[#596B72]" />
                </button>

                {/* Cuenta de Docente SEV */}
                <button
                  type="button"
                  onClick={() =>
                    handleGoogleAccountSelect({
                      name: 'Prof. Laura Mendoza',
                      email: 'laura.mendoza@docentes.sev.gob.mx',
                      role: 'teacher',
                      school: 'Secundaria Técnica #26 · Boca del Río',
                      picture: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
                    })
                  }
                  className="p-2 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors border border-transparent hover:border-[#E8E5DC] cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <img
                      src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
                      alt="Laura"
                      className="w-7 h-7 rounded-full object-cover"
                    />
                    <div>
                      <div className="text-[11px] font-display font-bold text-[#0A1D2C] flex items-center gap-1">
                        Prof. Laura Mendoza
                        <span className="text-[9px] bg-[#E76D55]/15 text-[#E76D55] px-1 py-0.2 rounded font-mono">Docente</span>
                      </div>
                      <div className="text-[10px] text-[#596B72]">laura.mendoza@docentes.sev.gob.mx</div>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-[#596B72]" />
                </button>

                {/* Ingresar cualquier otra cuenta Google */}
                <form onSubmit={handleCustomGoogleSubmit} className="pt-2 border-t border-[#E8E5DC] flex gap-1.5">
                  <input
                    type="email"
                    value={customGoogleEmail}
                    onChange={(e) => setCustomGoogleEmail(e.target.value)}
                    placeholder="o escribe tu @gmail.com"
                    className="flex-1 text-[11px] px-2.5 py-1.5 rounded-lg bg-[#F7F5EF] border border-[#E8E5DC] focus:outline-none focus:border-[#126B73]"
                  />
                  <button
                    type="submit"
                    className="px-2.5 py-1.5 bg-[#126B73] text-white rounded-lg text-[11px] font-display font-bold hover:bg-[#005158] cursor-pointer"
                  >
                    Entrar
                  </button>
                </form>
              </div>
            )}

            {/* SEPARADOR */}
            <div className="relative flex items-center justify-center my-0.5">
              <div className="border-t border-[#E8E5DC] w-full"></div>
              <span className="bg-[#F7F5EF] px-2 text-[10px] text-[#596B72] font-semibold uppercase tracking-wider shrink-0">
                o con usuario y contraseña
              </span>
            </div>

            {/* FORMULARIO MANUAL */}
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
                className={`w-full py-2.5 mt-1 rounded-full font-display font-bold text-xs text-white shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  selectedRole === 'student' ? 'bg-[#126B73]' : 'bg-[#E76D55] shadow-[0_3px_0_#711707]'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{mode === 'login' ? 'Entrar a la Plataforma' : 'Completar Registro'}</span>
              </button>

              <div className="text-center mt-0.5">
                <button
                  type="button"
                  onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                  className="text-[11px] text-[#126B73] font-semibold hover:underline cursor-pointer"
                >
                  {mode === 'login' ? '¿No tienes cuenta? Regístrate aquí' : '¿Ya tienes cuenta? Inicia sesión'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
