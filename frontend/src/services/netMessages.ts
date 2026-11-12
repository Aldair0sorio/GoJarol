import type { NetFailure } from './api';

export interface FailureNotice {
  text: string;
  /** false en 401/403: reintentar no sirve, hay que volver a iniciar sesión. */
  canRetry: boolean;
}

type Subject = 'mensaje' | 'respuesta' | 'pista';

/** Mensajes claros cuando una petición no llega. Nunca simulan una respuesta del tutor. */
export function failureNotice(reason: NetFailure, subject: Subject): FailureNotice {
  const notSent = subject === 'pista' ? 'no pudimos pedir la pista' : `tu ${subject} no se envió`;
  switch (reason) {
    case 'offline':
      return { text: `Sin conexión: ${notSent}. Toca para reintentar.`, canRetry: true };
    case 'timeout': {
      const mayHaveArrived =
        subject === 'pista' ? 'Tu solicitud' : `Tu ${subject}`;
      return {
        text: `La conexión está lenta, reintenta. ${mayHaveArrived} pudo haber llegado aunque no veas la respuesta.`,
        canRetry: true,
      };
    }
    case 'auth':
      return { text: `Tu sesión ya no es válida: ${notSent}. Vuelve a iniciar sesión.`, canRetry: false };
    default:
      return { text: `El servidor no respondió: ${notSent}. Toca para reintentar.`, canRetry: true };
  }
}

export const LOAD_FAILED = (what: string) =>
  `No pudimos cargar ${what}. Revisa tu conexión y toca para reintentar.`;
