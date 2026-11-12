import React, { useEffect, useState } from 'react';
import { apiService, type LeaderboardEntry } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Trophy, Flame, Sparkles, Medal, ArrowUp, Users } from 'lucide-react';

interface LeaguesViewProps {
  onGoPractice: () => void;
}

export const LeaguesView: React.FC<LeaguesViewProps> = ({ onGoPractice }) => {
  const { user } = useAuth();
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiService
      .getLeaderboard()
      .then((data) => {
        setEntries(data);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const topThree = entries.slice(0, 3);

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
              Liga Estudiantil Veracruz
            </span>
            <h1 className="font-display font-extrabold text-lg leading-tight">
              Clasificación General en Vivo
            </h1>
          </div>
        </div>

        <div className="text-right">
          <div className="inline-flex items-center gap-1 text-[11px] font-semibold bg-white/10 px-2.5 py-1 rounded-full border border-white/20 text-[#DCEFEB]">
            <Users className="w-3.5 h-3.5" />
            <span>{entries.length} estudiantes</span>
          </div>
        </div>
      </div>

      {/* Podio Top 3 (si hay al menos 1 estudiante registrado) */}
      {topThree.length > 0 && (
        <div className="bg-white rounded-2xl p-4 border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4">
          <h2 className="font-display font-bold text-xs uppercase tracking-wider text-[#596B72] mb-3 text-center">
            Podio de Puntos de Experiencia (XP)
          </h2>

          <div className="flex items-end justify-center gap-3 pt-2 pb-1">
            {/* Segundo Lugar (Plata) */}
            {topThree[1] && (
              <div className="flex flex-col items-center flex-1">
                <div className="relative">
                  <img
                    src="/mascot/jarol-crab.png"
                    alt={topThree[1].name}
                    className="w-12 h-12 rounded-full object-contain bg-[#F7F5EF] p-1 ring-2 ring-slate-300"
                  />
                  <span className="absolute -top-2 -right-1 w-5 h-5 rounded-full bg-slate-300 text-slate-800 font-display font-bold text-xs flex items-center justify-center border border-white">
                    2
                  </span>
                </div>
                <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[100px] text-center">
                  {topThree[1].name}
                </span>
                <span className="text-[11px] font-semibold text-[#126B73]">
                  {topThree[1].xp} XP
                </span>
                <div className="w-full h-12 bg-slate-100 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-slate-300 text-slate-600 font-display font-bold text-xs">
                  Plata
                </div>
              </div>
            )}

            {/* Primer Lugar (Oro) */}
            {topThree[0] && (
              <div className="flex flex-col items-center flex-1 -mt-2">
                <div className="relative">
                  <img
                    src="/mascot/jarol-crab.png"
                    alt={topThree[0].name}
                    className="w-14 h-14 rounded-full object-contain bg-amber-50 p-1 ring-4 ring-[#E4AA50] shadow-sm"
                  />
                  <span className="absolute -top-2.5 -right-1 w-6 h-6 rounded-full bg-[#E4AA50] text-amber-950 font-display font-extrabold text-xs flex items-center justify-center border-2 border-white shadow-xs">
                    👑 1
                  </span>
                </div>
                <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[110px] text-center">
                  {topThree[0].name}
                </span>
                <span className="text-xs font-bold text-[#E4AA50]">
                  {topThree[0].xp} XP
                </span>
                <div className="w-full h-16 bg-amber-50 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-[#E4AA50] text-amber-800 font-display font-bold text-sm">
                  Oro
                </div>
              </div>
            )}

            {/* Tercer Lugar (Bronce) */}
            {topThree[2] && (
              <div className="flex flex-col items-center flex-1">
                <div className="relative">
                  <img
                    src="/mascot/jarol-crab.png"
                    alt={topThree[2].name}
                    className="w-12 h-12 rounded-full object-contain bg-[#F7F5EF] p-1 ring-2 ring-amber-600/40"
                  />
                  <span className="absolute -top-2 -right-1 w-5 h-5 rounded-full bg-amber-700 text-white font-display font-bold text-xs flex items-center justify-center border border-white">
                    3
                  </span>
                </div>
                <span className="font-display font-bold text-xs text-[#0A1D2C] mt-1.5 truncate max-w-[100px] text-center">
                  {topThree[2].name}
                </span>
                <span className="text-[11px] font-semibold text-[#126B73]">
                  {topThree[2].xp} XP
                </span>
                <div className="w-full h-9 bg-orange-50 rounded-t-xl mt-2 flex items-center justify-center border-t-2 border-amber-600 text-amber-900 font-display font-bold text-xs">
                  Bronce
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Lista completa de estudiantes registrados en PostgreSQL */}
      <div className="bg-white rounded-2xl p-3 border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4 flex flex-col gap-2">
        <span className="text-xs font-display font-bold text-[#596B72] px-2 py-1">
          Tabla General de Estudiantes Registrados
        </span>

        {isLoading ? (
          <div className="p-6 text-center text-xs text-[#596B72]">
            Cargando clasificación en tiempo real...
          </div>
        ) : entries.length === 0 ? (
          <div className="p-6 text-center text-xs text-[#596B72]">
            Aún no hay estudiantes registrados en la liga. ¡Resuelve tu primer reto para inaugurar el marcador!
          </div>
        ) : (
          entries.map((item) => {
            const isMe = Boolean(item.isCurrentUser || item.id === user.id);
            return (
              <div
                key={item.id}
                className={`flex items-center justify-between p-2.5 rounded-xl transition-colors ${
                  isMe
                    ? 'bg-[#DCEFEB] border-2 border-[#126B73] shadow-xs'
                    : 'bg-[#F7F5EF] hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-6 text-center font-display font-bold text-sm ${
                      isMe ? 'text-[#126B73]' : 'text-[#596B72]'
                    }`}
                  >
                    #{item.rank}
                  </span>

                  <img
                    src="/mascot/jarol-crab.png"
                    alt={item.name}
                    className="w-9 h-9 rounded-full object-contain bg-white p-0.5 ring-1 ring-[#E8E5DC]"
                  />

                  <div>
                    <span
                      className={`font-display font-bold text-xs block ${
                        isMe ? 'text-[#126B73]' : 'text-[#0A1D2C]'
                      }`}
                    >
                      {item.name} {isMe ? '(Tú)' : ''}
                    </span>
                    <span className="text-[10px] text-[#596B72]">{item.grade}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5 text-amber-600">
                    <Flame className="w-3.5 h-3.5 fill-amber-500" />
                    <span className="text-[11px] font-bold">{item.streakDays}d</span>
                  </div>

                  <div className="flex items-center gap-1 font-display font-bold text-xs text-[#0A1D2C] bg-white px-2 py-1 rounded-lg border border-[#E8E5DC]">
                    <Sparkles className="w-3 h-3 text-[#E4AA50] fill-[#E4AA50]" />
                    <span>{item.xp} XP</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Llamado a la acción: Practicar para subir de puesto */}
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
