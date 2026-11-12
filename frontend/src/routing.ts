import type { UserRole } from './types/auth';

export const tabPaths: Record<string, string> = { chat: '/chat', profile: '/perfil', retos: '/retos', ligas: '/ligas', clases: '/clases', progreso: '/progreso', panel: '/panel', alumnos: '/alumnos' };
const publicPaths = new Set(['/login', '/registro', '/recuperar-contrasena', '/verificacion-pendiente', '/verificacion-exitosa', '/verificacion-invalida']);

// Fixed local destinations: no redirect is derived from user-controlled query strings.
export function routeRedirect(path: string, authenticated: boolean, role: UserRole): string | null {
  if (path === '/') return authenticated ? '/chat' : '/login';
  if (publicPaths.has(path) || /^\/verificar-correo\/[^/]+\/[^/]+\/?$/.test(path)) {
    return authenticated && ['/login', '/registro'].includes(path) ? '/chat' : null;
  }
  if (!authenticated) return '/login';
  if (!Object.values(tabPaths).includes(path)) return '/chat';
  if (role === 'student' && ['/panel', '/alumnos'].includes(path)) return '/chat';
  if (role !== 'student' && ['/retos', '/ligas', '/progreso'].includes(path)) return '/chat';
  return null;
}
