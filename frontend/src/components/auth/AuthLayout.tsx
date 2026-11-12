import { useEffect, type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const inputClass = 'mt-1 block min-h-12 w-full min-w-0 rounded-xl border border-subtle bg-white px-3 py-2 text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:bg-canvas';
export const primaryClass = 'min-h-12 w-full rounded-xl bg-primary px-5 py-3 font-bold text-white transition-colors hover:bg-primary-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-60';
export const linkClass = 'inline-flex min-h-11 items-center font-semibold text-primary underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-primary';

export function AuthLayout({ title, intro, children }: { title: string; intro: string; children: ReactNode }) {
  const { pathname } = useLocation();
  useEffect(() => { document.title = `${title} · Go Jarol`; document.getElementById('auth-title')?.focus(); }, [pathname, title]);
  return <main className="min-h-dvh bg-canvas px-4 py-6 text-ink sm:px-8 sm:py-12">
    <div className="mx-auto grid w-full max-w-5xl items-start gap-8 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
      <aside className="lg:sticky lg:top-12">
        <Link to="/login" className="inline-flex min-h-11 items-center gap-3 font-display text-xl font-bold"><img src="/mascot/jarol-crab.webp" alt="" width={48} height={48} className="h-12 w-12 object-contain"/>Go Jarol</Link>
        <div className="mt-12 hidden lg:block"><p className="font-display text-4xl font-bold leading-tight">Tu siguiente<br/>«ya entendí»<br/>empieza aquí.</p><p className="mt-5 max-w-xs leading-relaxed text-muted">Aprende a tu ritmo, pregunta sin pena y encuentra nuevas formas de entender.</p><img src="/mascot/jarol-crab.webp" alt="Jarol, tu compañero de aprendizaje" width={160} height={160} loading="lazy" decoding="async" className="mt-8 h-40 w-40 object-contain"/></div>
      </aside>
      <section aria-labelledby="auth-title" className="min-w-0 rounded-2xl border border-subtle bg-surface p-5 sm:p-8">
        <h1 id="auth-title" tabIndex={-1} className="font-display text-2xl font-bold outline-none sm:text-3xl">{title}</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">{intro}</p>
        <div className="mt-7">{children}</div>
      </section>
    </div>
  </main>;
}
