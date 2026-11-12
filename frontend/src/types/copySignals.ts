// Señales de copia del grupo (GET /classes/:id/copy-signals/). Solo conteos, nunca texto de mensajes.
export type CopySignal = 'ok' | 'revisar';

export interface CopySignalStudent {
  id: string;
  name: string;
  answerRequests: number;
  bypassAttempts: number;
  stepsSolved: number;
  hintsUsed: number;
  copySignal: CopySignal;
  reason: string;
}

export interface CopySignalTotals {
  students: number;
  studentsToReview: number;
  answerRequests: number;
  bypassAttempts: number;
  stepsSolved: number;
  hintsUsed: number;
}

export interface CopySignalsReport {
  classId: string;
  className: string;
  windowDays: number;
  rule: string;
  privacyNote: string;
  totals: CopySignalTotals;
  students: CopySignalStudent[];
  recommendations: string[];
}
