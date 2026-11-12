import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import { X, GraduationCap, User, Sparkles, CheckCircle2, ChevronRight, Loader2 } from 'lucide-react';

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (parent: HTMLElement | null, options: any) => void;
          prompt: (notification?: any) => void;
        };
      };
    };
  }
}

const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID ||
  '1057441789427-vbbijigh0lbj5dju7curv2dk3dm3qjo3.apps.googleusercontent.com';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { loginWithGoogle, login } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [selectedRole, setSelectedRole] = useState<'student' | 'teacher'>('student');
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('3° de Secundaria');
  const [school, setSchool] = useState('Secundaria Técnica #26 · Veracruz');
  const [submitted, setSubmitted] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showDemoAccounts, setShowDemoAccounts] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [googleSuccessName, setGoogleSuccessName] = useState('');
  const googleBtnRef = useRef<HTMLDivElement>(null);

  // Inicializar Google Identity Services (GIS)
  useEffect(() => {
    if (!isOpen) return;

    const initGoogle = () => {
      if (window.google?.accounts?.id && googleBtnRef.current) {
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          // Renderizar el botón oficial nativo de Google con estilo Veracruz
          googleBtnRef.current.innerHTML = '';
          window.google.accounts.id.renderButton(googleBtnRef.current, {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            text: 'continue_with',
            shape: 'rectangular',
            logo_alignment: 'left',
            width: googleBtnRef.current.offsetWidth || 300,
          });
        } catch (err) {
          console.warn('Google Identity Services no pudo renderizar botón automático:', err);
        }
      }
    };

    const timer = setTimeout(initGoogle, 150);
    return () => clearTimeout(timer);
  }, [isOpen, selectedRole]);

  if (!isOpen) return null;

  const parseGoogleJwt = (token: string) => {
    try {
      const base64Url = token.split('.')[1];
      if (!base64Url) return null;
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch {
      return null;
    }
  };

  // Manejador del JWT oficial de Google Identity Services
  const handleGoogleCredentialResponse = async (response: any) => {
    if (!response?.credential) return;
    setGoogleLoading(true);

    try {
      const decoded = parseGoogleJwt(response.credential);
      const googleEmail = decoded?.email || '';
      const googleName = decoded?.name || decoded?.given_name || 'Usuario Google';
      const googlePicture = decoded?.picture || '';

      const result = await apiService.loginWithGoogle({
        credential: response.credential,
        email: googleEmail,
        name: googleName,
        picture: googlePicture,
        role: selectedRole,
        grade: selectedRole === 'student' ? grade : undefined,
        school: school,
      });

      if (result.success && result.user) {
        setGoogleSuccessName(result.user.name || googleName);
        loginWithGoogle({
          ...result.user,
          name: result.user.name || googleName,
          email: result.user.email || googleEmail,
          avatarUrl: result.user.avatarUrl || googlePicture,
        });
        setGoogleLoading(false);
        setSubmitted(true);

        setTimeout(() => {
          setSubmitted(false);
          onClose();
        }, 1200);
      }
    } catch {
      setGoogleLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);

    const userName = name.trim() || (selectedRole === 'student' ? 'Estudiante Veracruzano' : 'Docente Veracruzano');
    const userEmail = `${userName.toLowerCase().replace(/[^a-z0-9]/g, '.')}@${selectedRole === 'student' ? 'estudiantes' : 'docentes'}.sev.gob.mx`;

    const newUser = {
      id: `usr_${Date.now()}`,
      name: userName,
      email: userEmail,
      role: selectedRole,
      grade: selectedRole === 'student' ? grade : undefined,
      school: school.trim() || 'Secundaria Técnica #26 · Veracruz',
      avatarUrl:
        selectedRole === 'teacher'
          ? 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=150&auto=format&fit=crop&q=80'
          : 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
      xp: selectedRole === 'student' ? 120 : 0,
      streakDays: selectedRole === 'student' ? 1 : 0,
    };

    login(newUser, `jarol_local_${Date.now()}`);

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
      await apiService.loginWithGoogle({
        email: account.email,
        name: account.name,
        picture: account.picture,
        role: account.role,
        grade: account.grade,
        school: account.school,
      });

      const demoUser = {
        id: `demo_${Date.now()}`,
        name: account.name,
        email: account.email,
        role: account.role,
        grade: account.grade,
        school: account.school,
        avatarUrl: account.picture,
        xp: account.role === 'student' ? 320 : 0,
        streakDays: account.role === 'student' ? 4 : 0,
      };

      login(demoUser, `jarol_demo_${Date.now()}`);

      setGoogleLoading(false);
      setSubmitted(true);

      setTimeout(() => {
        setSubmitted(false);
        setShowDemoAccounts(false);
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

  const triggerGooglePrompt = () => {
    if (window.google?.accounts?.id) {
      try {
        window.google.accounts.id.prompt();
      } catch (err) {
        console.warn('Error al activar Google Prompt:', err);
      }
    }
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
            {/* BOTÓN OFICIAL NATIVO DE GOOGLE IDENTITY SERVICES */}
            <div className="flex flex-col gap-1.5">
              {googleLoading && (
                <div className="p-3 bg-white rounded-xl border border-[#126B73] flex items-center justify-center gap-2 text-xs font-display font-bold text-[#126B73] animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validando con Google...</span>
                </div>
              )}

              {/* Contenedor oficial renderizado por Google SDK */}
              <div
                id="google-official-btn"
                ref={googleBtnRef}
                className="w-full flex justify-center min-h-[44px] overflow-hidden rounded-xl"
              />

              {/* Botón de respaldo/One Tap */}
              <button
                type="button"
                onClick={triggerGooglePrompt}
                className="text-[11px] text-[#126B73] font-semibold text-center hover:underline cursor-pointer"
              >
                ¿No abrió el selector? Toca aquí para reintentar
              </button>
            </div>

            {/* SELECCIÓN RÁPIDA DE CUENTAS DEMO SEV */}
            <div className="pt-1 border-t border-[#E8E5DC]">
              <button
                type="button"
                onClick={() => setShowDemoAccounts(!showDemoAccounts)}
                className="w-full py-1.5 px-2.5 rounded-lg bg-white border border-[#E8E5DC] text-[11px] font-display font-semibold text-[#596B72] hover:text-[#0A1D2C] flex items-center justify-between cursor-pointer"
              >
                <span>Cuentas de prueba institucionales (SEV)</span>
                <ChevronRight className={`w-3.5 h-3.5 transition-transform ${showDemoAccounts ? 'rotate-90' : ''}`} />
              </button>

              {showDemoAccounts && (
                <div className="p-2.5 mt-1.5 bg-white rounded-xl border border-[#D5D2C7] flex flex-col gap-2 animate-fadeIn">
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
                    className="p-1.5 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80"
                        alt="Emiliano"
                        className="w-6 h-6 rounded-full object-cover"
                      />
                      <div>
                        <div className="text-[11px] font-display font-bold text-[#0A1D2C]">Emiliano Valdés (Alumno)</div>
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
                    className="p-1.5 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
                        alt="Laura"
                        className="w-6 h-6 rounded-full object-cover"
                      />
                      <div>
                        <div className="text-[11px] font-display font-bold text-[#0A1D2C]">Prof. Laura Mendoza (Docente)</div>
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
                      className="flex-1 text-[11px] px-2 py-1 rounded-lg bg-[#F7F5EF] border border-[#E8E5DC] focus:outline-none focus:border-[#126B73]"
                    />
                    <button
                      type="submit"
                      className="px-2 py-1 bg-[#126B73] text-white rounded-lg text-[11px] font-display font-bold hover:bg-[#005158] cursor-pointer"
                    >
                      Entrar
                    </button>
                  </form>
                </div>
              )}
            </div>

            {/* SEPARADOR */}
            <div className="relative flex items-center justify-center my-0.5">
              <div className="border-t border-[#E8E5DC] w-full"></div>
              <span className="bg-[#F7F5EF] px-2 text-[10px] text-[#596B72] font-semibold uppercase tracking-wider shrink-0">
                o formulario tradicional
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
