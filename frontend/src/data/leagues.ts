export type LeagueTierId = 'bronce' | 'plata' | 'oro' | 'diamante';

export interface LeagueTier {
  id: LeagueTierId;
  name: string;
  minXp: number;
  imageUrl: string;
  tagline: string;
  cardBg: string;
  cardBorder: string;
  badgeBg: string;
  badgeText: string;
  barColor: string;
}

export interface BackendLeagueRank {
  id: string;
  name: string;
  xp: number;
  minXp: number;
  nextRank: string | null;
  xpToNext: number;
  progressPercent: number;
}

export interface LeagueStatus {
  tier: LeagueTier;
  nextTier: LeagueTier | null;
  xp: number;
  xpToNext: number;
  progressPercent: number;
}

export const LEAGUE_TIERS: LeagueTier[] = [
  {
    id: 'bronce',
    name: 'Bronce',
    minXp: 0,
    imageUrl: '/leagues/bronce.png',
    tagline: 'Inicio de tu aventura con Jarol',
    cardBg: 'bg-orange-50/70',
    cardBorder: 'border-amber-700/30',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-900',
    barColor: 'bg-amber-700',
  },
  {
    id: 'plata',
    name: 'Plata',
    minXp: 500,
    imageUrl: '/leagues/plata.png',
    tagline: 'Constancia en tus primeros retos',
    cardBg: 'bg-slate-50',
    cardBorder: 'border-slate-300',
    badgeBg: 'bg-slate-200/80',
    badgeText: 'text-slate-800',
    barColor: 'bg-slate-500',
  },
  {
    id: 'oro',
    name: 'Oro',
    minXp: 1200,
    imageUrl: '/leagues/oro.png',
    tagline: 'Dominio sólido de la materia',
    cardBg: 'bg-amber-50',
    cardBorder: 'border-[#E4AA50]',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-950',
    barColor: 'bg-[#E4AA50]',
  },
  {
    id: 'diamante',
    name: 'Diamante',
    minXp: 2500,
    imageUrl: '/leagues/diamante.png',
    tagline: 'Élite académica Go Jarol',
    cardBg: 'bg-sky-50',
    cardBorder: 'border-sky-400',
    badgeBg: 'bg-sky-100',
    badgeText: 'text-sky-900',
    barColor: 'bg-sky-500',
  },
];

export function getLeagueTierById(id?: string | null): LeagueTier {
  const normalized = (id || '').toLowerCase();
  return LEAGUE_TIERS.find((tier) => tier.id === normalized) || LEAGUE_TIERS[0];
}

/** Calcula la liga actual y el progreso hacia la siguiente a partir del XP (espejo de progress.ranks.rank_for_xp). */
export function getLeagueForXp(xpValue?: number | null, backendLeague?: BackendLeagueRank | null): LeagueStatus {
  const safeXp = Math.max(Math.floor(backendLeague?.xp ?? xpValue ?? 0), 0);

  let currentIndex = 0;
  for (let i = 0; i < LEAGUE_TIERS.length; i += 1) {
    if (safeXp >= LEAGUE_TIERS[i].minXp) {
      currentIndex = i;
    }
  }

  const tier = backendLeague?.id ? getLeagueTierById(backendLeague.id) : LEAGUE_TIERS[currentIndex];
  const resolvedIndex = LEAGUE_TIERS.findIndex((item) => item.id === tier.id);
  const nextTier = resolvedIndex + 1 < LEAGUE_TIERS.length ? LEAGUE_TIERS[resolvedIndex + 1] : null;

  if (nextTier) {
    const span = nextTier.minXp - tier.minXp;
    const progressPercent =
      backendLeague?.progressPercent !== undefined
        ? backendLeague.progressPercent
        : Math.max(0, Math.min(100, Math.round(((safeXp - tier.minXp) / span) * 100)));
    const xpToNext =
      backendLeague?.xpToNext !== undefined
        ? backendLeague.xpToNext
        : Math.max(0, nextTier.minXp - safeXp);

    return { tier, nextTier, xp: safeXp, xpToNext, progressPercent };
  }

  return {
    tier,
    nextTier: null,
    xp: safeXp,
    xpToNext: 0,
    progressPercent: 100,
  };
}
