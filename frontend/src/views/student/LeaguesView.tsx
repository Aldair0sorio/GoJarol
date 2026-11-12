import React, { useEffect, useState } from 'react';
import { apiService, type StudentProgressSummary } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { LEAGUE_TIERS, getLeagueForXp } from '../../data/leagues';
import { ConnectionNotice } from '../../components/common/ConnectionNotice';
import { LOAD_FAILED } from '../../services/netMessages';
import { Sparkles, Medal, ArrowUp, CheckCircle2 } from 'lucide-react';

interface LeaguesViewProps {
  onGoPractice: () => void;
}

export const LeaguesView: React.FC<LeaguesViewProps> = ({ onGoPractice }) => {
  const { user, updateUser } = useAuth();
  const [summary, setSummary] = useState<StudentProgressSummary | null>(null);
  const [loadFailed, setLoadFailed] = useState(false);

  // Si falla, se avisa y se usa el XP ya conocido de la sesión (no un 0 inventado).
  const loadProgress = () =>
    apiService.getProgress().then((data) => {
      setLoadFailed(data === null);
      if (!data) return;
      setSummary(data);
      if (data.xp !== undefined && data.xp !== user.xp) {
        updateUser({ xp: data.xp, streakDays: data.streakDays });
      }
    });

  useEffect(() => {
    loadProgress();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const myLeague = getLeagueForXp(summary?.xp ?? user.xp ?? 0, summary?.league);

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-3xl lg:max-w-4xl mx-auto w-full">
      {loadFailed && (
        <ConnectionNotice
          className="mb-4"
          text={LOAD_FAILED('tu liga actualizada')}
          onRetry={() => {
            setLoadFailed(false);
            loadProgress();
          }}
        />
      )}

      {/* Header de la Liga */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-[#126B73] to-[#005158] text-white shadow-[0_4px_16px_rgba(18,107,115,0.2)] mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-12 h-12 rounded-2xl bg-white/15 backdrop-blur-md flex items-center justify-center border border-white/20 shadow-xs shrink-0 p-1">
            <img
              src={myLeague.tier.imageUrl}
              alt={`Liga ${myLeague.tier.name}`}
              width={40}
              height={40}
              loading="lazy"
              decoding="async"
              className="w-full h-full object-contain drop-shadow-xs"
            />
          </div>
          <div className="min-w-0">
            <span className="text-[10px] font-display font-bold uppercase tracking-wider text-[#DCEFEB] block">
              Liga Estudiantil Veracruz
            </span>
            <h1 className="font-display font-extrabold text-lg leading-tight truncate">
              Rangos y Divisiones Go Jarol
            </h1>
          </div>
        </div>

        <div className="text-right shrink-0">
          <div className="inline-flex items-center gap-1 text-[11px] font-semibold bg-white/10 px-2.5 py-1 rounded-full border border-white/20 text-[#DCEFEB]">
            <Sparkles className="w-3.5 h-3.5 text-[#E4AA50]" />
            <span>{myLeague.xp} XP</span>
          </div>
        </div>
      </div>

      {/* Tu Liga Actual + Divisiones por XP */}
      <div className="bg-white rounded-2xl p-4 border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E8E5DC]">
          <div className="flex items-center gap-3">
            <img
              src={myLeague.tier.imageUrl}
              alt={`Liga ${myLeague.tier.name}`}
              width={72}
              height={72}
              loading="lazy"
              decoding="async"
              className="w-16 h-16 sm:w-18 sm:h-18 object-contain shrink-0 drop-shadow-xs"
            />
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[11px] font-display font-bold uppercase tracking-wider text-[#596B72]">
                  Tu liga actual
                </span>
                <span
                  className={`text-[11px] font-display font-extrabold px-2 py-0.5 rounded-full ${myLeague.tier.badgeBg} ${myLeague.tier.badgeText}`}
                >
                  {myLeague.tier.name}
                </span>
              </div>
              <p className="font-display font-extrabold text-base text-[#0A1D2C] mt-0.5">
                {myLeague.xp} XP acumulados
              </p>
              <p className="text-xs text-[#596B72]">{myLeague.tier.tagline}</p>
            </div>
          </div>

          <div className="sm:w-56">
            <div className="flex items-center justify-between text-[11px] font-display font-semibold mb-1">
              <span className="text-[#0A1D2C]">
                {myLeague.nextTier ? `Rumbo a ${myLeague.nextTier.name}` : 'Liga máxima alcanzada'}
              </span>
              <span className="text-[#126B73]">
                {myLeague.nextTier ? `${myLeague.xpToNext} XP restantes` : '100%'}
              </span>
            </div>
            <div className="w-full h-2.5 bg-[#DCEFEB] rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${myLeague.tier.barColor}`}
                style={{ width: `${myLeague.progressPercent}%` }}
              />
            </div>
          </div>
        </div>

        <div className="pt-3">
          <h2 className="font-display font-bold text-[11px] uppercase tracking-wider text-[#596B72] mb-2.5">
            Divisiones de la Liga Go Jarol
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {LEAGUE_TIERS.map((tier) => {
              const isCurrent = tier.id === myLeague.tier.id;
              const isUnlocked = myLeague.xp >= tier.minXp;
              return (
                <div
                  key={tier.id}
                  className={`relative rounded-xl p-2.5 border flex flex-col items-center text-center transition-all ${
                    isCurrent
                      ? `${tier.cardBg} ${tier.cardBorder} ring-2 ring-[#126B73] shadow-xs`
                      : isUnlocked
                      ? `${tier.cardBg} ${tier.cardBorder}`
                      : 'bg-[#F7F5EF]/70 border-[#E8E5DC] opacity-75'
                  }`}
                >
                  {isCurrent && (
                    <span className="absolute -top-2 right-2 bg-[#126B73] text-white text-[9px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shadow-2xs">
                      Tu liga
                    </span>
                  )}
                  {!isCurrent && isUnlocked && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 absolute top-2 right-2" />
                  )}
                  <img
                    src={tier.imageUrl}
                    alt={`Emblema Liga ${tier.name}`}
                    width={64}
                    height={64}
                    loading="lazy"
                    decoding="async"
                    className={`w-14 h-14 sm:w-16 sm:h-16 object-contain mb-1.5 ${
                      !isUnlocked ? 'grayscale-[25%]' : ''
                    }`}
                  />
                  <span className="font-display font-extrabold text-xs text-[#0A1D2C]">
                    {tier.name}
                  </span>
                  <span
                    className={`mt-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${tier.badgeBg} ${tier.badgeText}`}
                  >
                    {tier.minXp === 0 ? 'Inicio (0+ XP)' : `${tier.minXp}+ XP`}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Llamado a la acción: Practicar para subir de rango */}
      <button
        onClick={onGoPractice}
        className="w-full py-3 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_4px_0_#711707] active:translate-y-0.5 active:shadow-[0_2px_0_#711707] transition-all cursor-pointer"
      >
        <Medal className="w-4 h-4" />
        <span>Gana +30 XP resolviendo un reto con Jarol</span>
        <ArrowUp className="w-4 h-4 stroke-[3px]" />
      </button>
    </div>
  );
};
