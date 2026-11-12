import type { UserRole } from './types/auth';

export const tabPaths: Record<string, string> = { chat: '/chat', profile: '/perfil', retos: '/retos', ligas: '/ligas', clases: '/clases', progreso: '/progreso', panel: '/panel', alumnos: '/alumnos' };
const publicPaths = new Set(['/login', '/registro', '/recuperar-contrasena', '/verificacion-pendiente', '/verificacion-exitosa', '/verificacion-invalida']);

export function defaultPathForRole(role: UserRole): string {
  return role === 'student' ? '/chat' : '/clases';
}

// Fixed local destinations: no redirect is derived from user-controlled query strings.
export function routeRedirect(path: string, authenticated: boolean, role: UserRole): string | null {
  const home = defaultPathForRole(role);
  if (path === '/') return authenticated ? home : '/login';
  if (publicPaths.has(path) || /^\/verificar-correo\/[^/]+\/[^/]+\/?$/.test(path)) {
    return authenticated && ['/login', '/registro'].includes(path) ? home : null;
  }
  if (!authenticated) return '/login';
  if (!Object.values(tabPaths).includes(path)) return home;
  if (role === 'student' && ['/panel', '/alumnos'].includes(path)) return home;
  if (role !== 'student' && ['/chat', '/retos', '/ligas', '/progreso'].includes(path)) return home;
  return null;
}
