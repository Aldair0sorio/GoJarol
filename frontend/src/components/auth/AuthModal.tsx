import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import {
  X,
  GraduationCap,
  User,
  Sparkles,
  CheckCircle2,
  ChevronRight,
  Loader2,
  Lock,
  Mail,
  UserPlus,
  LogIn,
  School,
  AlertCircle,
} from 'lucide-react';

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

  // Estado para LOGIN
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Estado para REGISTRO
  const [registerRole, setRegisterRole] = useState<'student' | 'teacher'>('student');
  const [registerName, setRegisterName] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerNivel, setRegisterNivel] = useState<'secundaria' | 'bachillerato'>('secundaria');
  const [registerGrado, setRegisterGrado] = useState<number>(3);
  const [registerSchool, setRegisterSchool] = useState('Secundaria Técnica #26 · Boca del Río');
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  // Estados compartidos
  const [submitted, setSubmitted] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showDemoAccounts, setShowDemoAccounts] = useState(false);
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

          googleBtnRef.current.innerHTML = '';
          window.google.accounts.id.renderButton(googleBtnRef.current, {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            text: mode === 'login' ? 'signin_with' : 'signup_with',
            shape: 'rectangular',
            logo_alignment: 'left',
            width: googleBtnRef.current.offsetWidth || 300,
          });
        } catch (err) {
          console.warn('Google Identity Services no pudo renderizar botón:', err);
        }
      }
    };

    const timer = setTimeout(initGoogle, 150);
    return () => clearTimeout(timer);
  }, [isOpen, mode, registerRole]);

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

  const handleNivelChange = (newNivel: 'secundaria' | 'bachillerato') => {
    setRegisterNivel(newNivel);
    if (newNivel === 'secundaria' && registerGrado > 3) {
      setRegisterGrado(3);
    }
  };

  // Manejo de respuesta de Google OAuth
  const handleGoogleCredentialResponse = async (response: any) => {
    if (!response?.credential) return;
    setGoogleLoading(true);

    try {
      const decoded = parseGoogleJwt(response.credential);
      const googleEmail = decoded?.email || '';
      const googleName = decoded?.name || decoded?.given_name || 'Usuario Google';
      const googlePicture = decoded?.picture || '';

      const targetRole = mode === 'register' ? registerRole : 'student';
      const gradeStr =
        targetRole === 'student'
          ? registerNivel === 'bachillerato'
            ? `${registerGrado}° Semestre de Bachillerato`
            : `${registerGrado}° de Secundaria`
          : undefined;

      const result = await apiService.loginWithGoogle({
        credential: response.credential,
        email: googleEmail,
        name: googleName,
        picture: googlePicture,
        role: targetRole,
        explicitRole: mode === 'register',
        grade: gradeStr,
        school: registerSchool,
      });

      if (result.success && result.user) {
        loginWithGoogle(
          {
            ...result.user,
            name: result.user.name || googleName,
            email: result.user.email || googleEmail,
            avatarUrl: result.user.avatarUrl || googlePicture,
          },
          result.token
        );

        setSuccessMessage(`¡Bienvenido, ${result.user.name || googleName}!`);
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

  // Manejo de LOGIN tradicional
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);

    if (!loginIdentifier.trim()) {
      setLoginError('Por favor ingresa tu usuario o correo electrónico.');
      return;
    }

    setLoginLoading(true);
    try {
      const result = await apiService.login({
        username: loginIdentifier.trim(),
        password: loginPassword,
      });

      if (result.success && result.user) {
        login(result.user, result.token);
        setSuccessMessage(`¡Qué gusto verte de nuevo, ${result.user.name}!`);
        setSubmitted(true);

        setTimeout(() => {
          setSubmitted(false);
          onClose();
        }, 1200);
      } else {
        setLoginError(result.error || 'Credenciales no válidas. Revisa tus datos.');
      }
    } catch {
      setLoginError('No se pudo conectar con el servidor. Intenta de nuevo.');
    } finally {
      setLoginLoading(false);
    }
  };

  // Manejo de REGISTRO tradicional
  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError(null);

    if (!registerName.trim()) {
      setRegisterError('Por favor ingresa tu nombre completo.');
      return;
    }

    const username = registerUsername.trim() || registerName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
    const email = registerEmail.trim() || `${username}@${registerRole === 'student' ? 'estudiantes' : 'docentes'}.sev.gob.mx`;
    const password = registerPassword.trim() || 'Jarol2026!';

    setRegisterLoading(true);
    try {
      const result = await apiService.register({
        username,
        email,
        password,
        alias: registerName.trim(),
        role: registerRole,
        nivel: registerNivel,
        grado: registerGrado,
        school: registerSchool.trim(),
      });

      if (result.success && result.user) {
        login(result.user, result.token);
        setSuccessMessage(`¡Cuenta creada con éxito! Bienvenido, ${result.user.name}.`);
        setSubmitted(true);

        setTimeout(() => {
          setSubmitted(false);
          onClose();
        }, 1200);
      } else {
        setRegisterError(result.error || 'No se pudo completar el registro. Verifica los campos.');
      }
    } catch {
      setRegisterError('Error de conexión. Intenta de nuevo.');
    } finally {
      setRegisterLoading(false);
    }
  };

  // Demo account select (autenticación real en PostgreSQL)
  const handleDemoAccountSelect = async (account: {
    name: string;
    email: string;
    role: 'student' | 'teacher';
    grade?: string;
    school?: string;
    picture?: string;
  }) => {
    const profile: 'student' | 'teacher' = account.role === 'teacher' ? 'teacher' : 'student';
    const res = await apiService.loginDemo(profile);

    if (res.success && res.user) {
      login(res.user, res.token);
      setSuccessMessage(`¡Accediste como ${res.user.name}!`);
    } else {
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
      setSuccessMessage(`¡Accediste como ${account.name}!`);
    }

    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setShowDemoAccounts(false);
      onClose();
    }, 900);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3 animate-fadeIn">
      <div className="bg-[#F7F5EF] rounded-3xl max-w-md w-full p-6 border border-[#E8E5DC] shadow-2xl flex flex-col gap-4 animate-scaleUp max-h-[92vh] overflow-y-auto">
        {/* Header con Mascota y Botón Cerrar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img
              src="/mascot/jarol-crab.png"
              alt="Jarol"
              className="w-9 h-9 rounded-full bg-[#126B73]/10 p-0.5 object-contain"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-display font-black text-base text-[#0A1D2C]">Go Jarol</span>
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded-full bg-[#E76D55] text-white uppercase">
                  Veracruz
                </span>
              </div>
              <p className="text-[11px] text-[#596B72]">Aprender a la jarocha con tutor IA</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:bg-[#E8E5DC]/50 cursor-pointer transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* TABS PRINCIPALES: INICIAR SESIÓN vs REGISTRARSE */}
        <div className="flex p-1 bg-white/90 rounded-2xl border border-[#E8E5DC] shadow-inner">
          <button
            type="button"
            onClick={() => {
              setMode('login');
              setLoginError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-display font-extrabold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
              mode === 'login'
                ? 'bg-[#126B73] text-white shadow-sm'
                : 'text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Iniciar Sesión</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setMode('register');
              setRegisterError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-display font-extrabold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
              mode === 'register'
                ? 'bg-[#126B73] text-white shadow-sm'
                : 'text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Crear Cuenta</span>
          </button>
        </div>

        {/* CONTENIDO SEGÚN ESTADO SUBMITTED */}
        {submitted ? (
          <div className="py-8 flex flex-col items-center justify-center gap-2.5 text-center animate-fadeIn">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 animate-bounce" />
            <h3 className="font-display font-extrabold text-base text-[#0A1D2C]">{successMessage}</h3>
            <p className="text-xs text-[#596B72]">Configurando tu espacio de aprendizaje en Go Jarol...</p>
          </div>
        ) : mode === 'login' ? (
          /* ======================================================== */
          /* PANTALLA: INICIAR SESIÓN                                 */
          /* ======================================================== */
          <div className="flex flex-col gap-3.5">
            <div>
              <h2 className="font-display font-extrabold text-lg text-[#0A1D2C]">¡Qué onda! Bienvenido de vuelta 🦀</h2>
              <p className="text-xs text-[#596B72] mt-0.5">
                Accede para continuar tus retos y guardar tus puntos.
              </p>
            </div>

            {/* FORMULARIO DE LOGIN TRADICIONAL ARRIBA */}
            <form onSubmit={handleLoginSubmit} className="flex flex-col gap-2.5">
              {loginError && (
                <div className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-shake">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{loginError}</span>
                </div>
              )}

              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Usuario o Correo Institucional
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#596B72] absolute left-3 top-3" />
                  <input
                    type="text"
                    value={loginIdentifier}
                    onChange={(e) => setLoginIdentifier(e.target.value)}
                    placeholder="ej. emiliano.valdes o tu@gmail.com"
                    required
                    className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Contraseña
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#596B72] absolute left-3 top-3" />
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Tu contraseña"
                    className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full py-2.5 mt-1 rounded-full bg-[#126B73] text-white font-display font-bold text-xs shadow-[0_3px_0_#005158] hover:bg-[#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {loginLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verificando...</span>
                  </>
                ) : (
                  <>
                    <LogIn className="w-3.5 h-3.5" />
                    <span>Iniciar Sesión</span>
                  </>
                )}
              </button>
            </form>

            {/* SEPARADOR: O CONTINUAR CON GOOGLE */}
            <div className="relative flex items-center justify-center my-0.5">
              <div className="border-t border-[#E8E5DC] w-full"></div>
              <span className="bg-[#F7F5EF] px-2.5 text-[10px] text-[#596B72] font-semibold uppercase tracking-wider shrink-0">
                o también puedes acceder con
              </span>
            </div>

            {/* BOTÓN OFICIAL DE GOOGLE ABAJO */}
            <div className="flex flex-col gap-1.5">
              {googleLoading && (
                <div className="p-2.5 bg-white rounded-xl border border-[#126B73] flex items-center justify-center gap-2 text-xs font-display font-bold text-[#126B73] animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Conectando con Google...</span>
                </div>
              )}
              <div
                id="google-official-btn-login"
                ref={googleBtnRef}
                className="w-full flex justify-center min-h-[44px] overflow-hidden rounded-xl"
              />
            </div>

            {/* SELECCIÓN RÁPIDA DE CUENTAS DEMO SEV */}
            <div className="pt-2 border-t border-[#E8E5DC]">
              <button
                type="button"
                onClick={() => setShowDemoAccounts(!showDemoAccounts)}
                className="w-full py-1.5 px-3 rounded-xl bg-white border border-[#E8E5DC] text-[11px] font-display font-semibold text-[#596B72] hover:text-[#0A1D2C] flex items-center justify-between cursor-pointer"
              >
                <span>Cuentas rápidas de demostración (SEV)</span>
                <ChevronRight
                  className={`w-3.5 h-3.5 transition-transform ${showDemoAccounts ? 'rotate-90' : ''}`}
                />
              </button>

              {showDemoAccounts && (
                <div className="p-2.5 mt-2 bg-white rounded-xl border border-[#D5D2C7] flex flex-col gap-2 animate-fadeIn">
                  <button
                    type="button"
                    onClick={() =>
                      handleDemoAccountSelect({
                        name: 'Emiliano Valdés',
                        email: 'emiliano.valdes@estudiantes.sev.gob.mx',
                        role: 'student',
                        grade: '3° de Secundaria',
                        school: 'Secundaria Técnica #26 · Boca del Río',
                        picture:
                          'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
                      })
                    }
                    className="p-1.5 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80"
                        alt="Emiliano"
                        className="w-7 h-7 rounded-full object-cover"
                      />
                      <div>
                        <div className="text-[11px] font-display font-bold text-[#0A1D2C]">
                          Emiliano Valdés (Estudiante 3°)
                        </div>
                        <div className="text-[10px] text-[#596B72]">
                          emiliano.valdes@estudiantes.sev.gob.mx
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-[#596B72]" />
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleDemoAccountSelect({
                        name: 'Prof. Laura Mendoza',
                        email: 'laura.mendoza@docentes.sev.gob.mx',
                        role: 'teacher',
                        school: 'Secundaria Técnica #26 · Boca del Río',
                        picture:
                          'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
                      })
                    }
                    className="p-1.5 rounded-lg hover:bg-[#F7F5EF] flex items-center justify-between text-left transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <img
                        src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
                        alt="Laura"
                        className="w-7 h-7 rounded-full object-cover"
                      />
                      <div>
                        <div className="text-[11px] font-display font-bold text-[#0A1D2C]">
                          Prof. Laura Mendoza (Docente)
                        </div>
                        <div className="text-[10px] text-[#596B72]">
                          laura.mendoza@docentes.sev.gob.mx
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-[#596B72]" />
                  </button>
                </div>
              )}
            </div>

            {/* SWITCH A REGISTRO */}
            <div className="text-center pt-1">
              <span className="text-[11px] text-[#596B72]">¿No tienes una cuenta aún? </span>
              <button
                type="button"
                onClick={() => {
                  setMode('register');
                  setRegisterError(null);
                }}
                className="text-[11px] text-[#126B73] font-display font-bold hover:underline cursor-pointer"
              >
                Regístrate gratis aquí
              </button>
            </div>
          </div>
        ) : (
          /* ======================================================== */
          /* PANTALLA: CREAR CUENTA (REGISTRO)                         */
          /* ======================================================== */
          <div className="flex flex-col gap-3.5">
            <div>
              <h2 className="font-display font-extrabold text-lg text-[#0A1D2C]">Crea tu cuenta en Go Jarol 🦀</h2>
              <p className="text-xs text-[#596B72] mt-0.5">
                Elige tu rol para personalizar tu tutor y tus temas de estudio.
              </p>
            </div>

            {/* SELECTOR DE ROL: ESTUDIANTE / DOCENTE */}
            <div className="flex gap-2 p-1 bg-white rounded-2xl border border-[#E8E5DC]">
              <button
                type="button"
                onClick={() => setRegisterRole('student')}
                className={`flex-1 py-2 rounded-xl text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                  registerRole === 'student'
                    ? 'bg-[#126B73] text-white shadow-xs'
                    : 'text-[#596B72] hover:text-[#0A1D2C]'
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>Soy Estudiante</span>
              </button>

              <button
                type="button"
                onClick={() => setRegisterRole('teacher')}
                className={`flex-1 py-2 rounded-xl text-xs font-display font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                  registerRole === 'teacher'
                    ? 'bg-[#E76D55] text-white shadow-xs'
                    : 'text-[#596B72] hover:text-[#0A1D2C]'
                }`}
              >
                <GraduationCap className="w-3.5 h-3.5" />
                <span>Soy Docente</span>
              </button>
            </div>

            {/* FORMULARIO DE REGISTRO COMPLETO ARRIBA */}
            <form onSubmit={handleRegisterSubmit} className="flex flex-col gap-2.5">
              {registerError && (
                <div className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-shake">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{registerError}</span>
                </div>
              )}

              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Nombre Completo *
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#596B72] absolute left-3 top-3" />
                  <input
                    type="text"
                    value={registerName}
                    onChange={(e) => setRegisterName(e.target.value)}
                    placeholder="Ej. Hugo García Lara"
                    required
                    className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                    Usuario
                  </label>
                  <input
                    type="text"
                    value={registerUsername}
                    onChange={(e) => setRegisterUsername(e.target.value)}
                    placeholder="ej. hugo_dev"
                    className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                    Contraseña *
                  </label>
                  <input
                    type="password"
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    placeholder="Mín. 8 caracteres"
                    required
                    className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Correo Electrónico
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#596B72] absolute left-3 top-3" />
                  <input
                    type="email"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    placeholder="ej. tu@gmail.com o @estudiantes.sev.gob.mx"
                    className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              {/* SELECTOR DE NIVEL Y GRADOS/SEMESTRES (SECUNDARIA = 3 AÑOS, BACHILLERATO = 6 SEMESTRES) */}
              {registerRole === 'student' && (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                      Nivel Escolar
                    </label>
                    <select
                      value={registerNivel}
                      onChange={(e) => handleNivelChange(e.target.value as 'secundaria' | 'bachillerato')}
                      className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none font-display font-medium"
                    >
                      <option value="secundaria">Secundaria (3 años)</option>
                      <option value="bachillerato">Bachillerato (6 semestres)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                      {registerNivel === 'secundaria' ? 'Año Escolar' : 'Semestre'}
                    </label>
                    {registerNivel === 'secundaria' ? (
                      <select
                        value={registerGrado}
                        onChange={(e) => setRegisterGrado(Number(e.target.value))}
                        className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none font-display"
                      >
                        <option value={1}>1° de Secundaria</option>
                        <option value={2}>2° de Secundaria</option>
                        <option value={3}>3° de Secundaria</option>
                      </select>
                    ) : (
                      <select
                        value={registerGrado}
                        onChange={(e) => setRegisterGrado(Number(e.target.value))}
                        className="w-full text-xs p-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none font-display"
                      >
                        <option value={1}>1er Semestre</option>
                        <option value={2}>2do Semestre</option>
                        <option value={3}>3er Semestre</option>
                        <option value={4}>4to Semestre</option>
                        <option value={5}>5to Semestre</option>
                        <option value={6}>6to Semestre</option>
                      </select>
                    )}
                  </div>
                </div>
              )}

              <div>
                <label className="text-[11px] font-display font-semibold text-[#596B72] block mb-1">
                  Escuela / Municipio en Veracruz
                </label>
                <div className="relative">
                  <School className="w-4 h-4 text-[#596B72] absolute left-3 top-3" />
                  <input
                    type="text"
                    value={registerSchool}
                    onChange={(e) => setRegisterSchool(e.target.value)}
                    placeholder="Ej. Secundaria Técnica #26 · Boca del Río"
                    className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl bg-white border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={registerLoading}
                className={`w-full py-2.5 mt-1 rounded-full text-white font-display font-bold text-xs shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 ${
                  registerRole === 'student' ? 'bg-[#126B73]' : 'bg-[#E76D55] shadow-[0_3px_0_#711707]'
                }`}
              >
                {registerLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creando tu cuenta...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>
                      {registerRole === 'student'
                        ? 'Crear mi Cuenta de Estudiante'
                        : 'Crear mi Cuenta de Docente'}
                    </span>
                  </>
                )}
              </button>
            </form>

            {/* SEPARADOR: O REGISTRARME CON GOOGLE */}
            <div className="relative flex items-center justify-center my-0.5">
              <div className="border-t border-[#E8E5DC] w-full"></div>
              <span className="bg-[#F7F5EF] px-2.5 text-[10px] text-[#596B72] font-semibold uppercase tracking-wider shrink-0">
                o también puedes registrarte con
              </span>
            </div>

            {/* BOTÓN OFICIAL DE GOOGLE ABAJO */}
            <div className="flex flex-col gap-1.5">
              {googleLoading && (
                <div className="p-2.5 bg-white rounded-xl border border-[#126B73] flex items-center justify-center gap-2 text-xs font-display font-bold text-[#126B73] animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creando cuenta con Google...</span>
                </div>
              )}
              <div
                id="google-official-btn-register"
                ref={googleBtnRef}
                className="w-full flex justify-center min-h-[44px] overflow-hidden rounded-xl"
              />
            </div>

            {/* SWITCH A LOGIN */}
            <div className="text-center pt-1">
              <span className="text-[11px] text-[#596B72]">¿Ya tienes una cuenta registrada? </span>
              <button
                type="button"
                onClick={() => {
                  setMode('login');
                  setLoginError(null);
                }}
                className="text-[11px] text-[#126B73] font-display font-bold hover:underline cursor-pointer"
              >
                Inicia sesión aquí
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
