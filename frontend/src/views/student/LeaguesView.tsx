import React from 'react';
import { MOCK_LEADERBOARD } from '../../services/mockData';
import { Trophy, Flame, Sparkles, Medal, ArrowUp, Clock } from 'lucide-react';

interface LeaguesViewProps {
  onGoPractice: () => void;
}

export const LeaguesView: React.FC<LeaguesViewProps> = ({ onGoPractice }) => {
  const topThree = MOCK_LEADERBOARD.slice(0, 3);
  const remainingList = MOCK_LEADERBOARD.slice(3);

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-3xl lg:max-w-4xl mx-auto w-full">
      {/* Header de la Liga */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-[#126B73] to-[#005158] text-white shadow-[0_4px_16px_rgba(18,107,115,0.2)] mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-white/15 backdrop-blur-md flex items-center justify-center border border-white/20 shadow-xs">
            <Trophy className="w-6 h-6 text-[#E4AA50] fill-[#E4AA50]" />
          </div>
          <div>
            <span className="text-[10px] font-display font-bold uppercase tracking-wider text-[#DCEFEB] block">
              Liga Semanal Veracruz
            </span>
            <h1 className="font-display font-extrabold text-lg leading-tight">
              División Sotavento · Plata
            </h1>
          </div>
        </div>

        <div className="text-right">
          <div className="inline-flex items-center gap-1 text-[11px] font-semibold bg-white/10 px-2 py-0.5 rounded-full border border-white/20 text-[#DCEFEB]">
            <Clock className="w-3 h-3" />
            <span>2 días</span>
          </div>
        </div>
      </div>

      {/* Podio Top 3 */}
      <div className="bg-white rounded-2xl p-4 border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4">
        <h2 className="font-display font-bold text-xs uppercase tracking-wider text-[#596B72] mb-3 text-center">
          Puntos de Experiencia Semanal
        </h2>

        <div className="flex items-end justify-center gap-3 pt-2 pb-1">
          {/* Segundo Lugar (Plata) */}
          <div className="flex flex-col items-center flex-1">
            <div className="relative">
              <img
                src={topThree[1].avatarUrl}
                alt={topThree[1].name}
                className="w-12 h-12 rounded-full object-cover ring-2 ring-slate-300"
              />
              <span className="absolute -top-2 -right-1 w-5 h-5 rounded-full bg-slate-300 text-slate-800 font-display font-bold text-xs flex items-center justify-center border border-white">
                2
              </span>
            </div>
            <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[85px] text-center">
              {topThree[1].name}
            </span>
            <span className="text-[11px] font-semibold text-[#126B73]">
              {topThree[1].xp} XP
            </span>
            <div className="w-full h-12 bg-slate-100 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-slate-300 text-slate-600 font-display font-bold text-xs">
              Plata
            </div>
          </div>

          {/* Primer Lugar (Oro) */}
          <div className="flex flex-col items-center flex-1 -mt-2">
            <div className="relative">
              <img
                src={topThree[0].avatarUrl}
                alt={topThree[0].name}
                className="w-14 h-14 rounded-full object-cover ring-4 ring-[#E4AA50] shadow-sm"
              />
              <span className="absolute -top-2.5 -right-1 w-6 h-6 rounded-full bg-[#E4AA50] text-amber-950 font-display font-extrabold text-xs flex items-center justify-center border-2 border-white shadow-xs">
                👑 1
              </span>
            </div>
            <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[90px] text-center">
              {topThree[0].name}
            </span>
            <span className="text-xs font-bold text-[#E4AA50]">
              {topThree[0].xp} XP
            </span>
            <div className="w-full h-16 bg-amber-50 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-[#E4AA50] text-amber-800 font-display font-bold text-sm">
              Oro
            </div>
          </div>

          {/* Tercer Lugar (Bronce) */}
          <div className="flex flex-col items-center flex-1">
            <div className="relative">
              <img
                src={topThree[2].avatarUrl}
                alt={topThree[2].name}
                className="w-12 h-12 rounded-full object-cover ring-2 ring-amber-600/40"
              />
              <span className="absolute -top-2 -right-1 w-5 h-5 rounded-full bg-amber-700 text-white font-display font-bold text-xs flex items-center justify-center border border-white">
                3
              </span>
            </div>
            <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[85px] text-center">
              {topThree[2].name}
            </span>
            <span className="text-[11px] font-semibold text-[#126B73]">
              {topThree[2].xp} XP
            </span>
            <div className="w-full h-9 bg-orange-50 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-amber-600 text-amber-900 font-display font-bold text-xs">
              Bronce
            </div>
          </div>
        </div>
      </div>

      {/* Lista del resto de la liga */}
      <div className="bg-white rounded-2xl p-3 border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4 flex flex-col gap-2">
        <span className="text-xs font-display font-bold text-[#596B72] px-2 py-1">
          Tabla General del Salón
        </span>

        {remainingList.map((user) => (
          <div
            key={user.id}
            className={`flex items-center justify-between p-2.5 rounded-xl transition-colors ${
              user.isCurrentUser
                ? 'bg-[#DCEFEB] border-2 border-[#126B73] shadow-xs'
                : 'bg-[#F7F5EF] hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <span
                className={`w-6 text-center font-display font-bold text-sm ${
                  user.isCurrentUser ? 'text-[#126B73]' : 'text-[#596B72]'
                }`}
              >
                #{user.rank}
              </span>

              <img
                src={user.avatarUrl}
                alt={user.name}
                className="w-9 h-9 rounded-full object-cover ring-1 ring-[#E8E5DC]"
              />

              <div>
                <span
                  className={`font-display font-bold text-xs block ${
                    user.isCurrentUser ? 'text-[#126B73]' : 'text-[#0A1D2C]'
                  }`}
                >
                  {user.name}
                </span>
                <span className="text-[10px] text-[#596B72]">
                  {user.school}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-0.5 text-amber-600">
                <Flame className="w-3.5 h-3.5 fill-amber-500" />
                <span className="text-[11px] font-bold">{user.streakDays}d</span>
              </div>

              <div className="flex items-center gap-1 font-display font-bold text-xs text-[#0A1D2C] bg-white px-2 py-1 rounded-lg border border-[#E8E5DC]">
                <Sparkles className="w-3 h-3 text-[#E4AA50] fill-[#E4AA50]" />
                <span>{user.xp} XP</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Llamado a la acción: Practicar para subir de puesto */}
      <button
        onClick={onGoPractice}
        className="w-full py-3 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_4px_0_#711707] active:translate-y-0.5 active:shadow-[0_2px_0_#711707] transition-all cursor-pointer"
      >
        <Medal className="w-4 h-4" />
        <span>Gana +30 XP practicando fracciones</span>
        <ArrowUp className="w-4 h-4 stroke-[3px]" />
      </button>
    </div>
  );
};
