import React, { useState, useEffect } from 'react';
import type { ClassGroup } from '../../types/curriculum';
import { apiService } from '../../services/api';
import { ClassDetailModal } from './ClassDetailModal';
import { Users2, Plus, CheckCircle2, AlertCircle, ChevronRight } from 'lucide-react';

interface ClassesViewProps {
  onStartExercise?: (topic: string) => void;
}

export const ClassesView: React.FC<ClassesViewProps> = ({ onStartExercise }) => {
  const [classes, setClasses] = useState<ClassGroup[]>([]);
  const [joinCode, setJoinCode] = useState('');
  const [joinStatus, setJoinStatus] = useState<{ success: boolean; message: string } | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedClass, setSelectedClass] = useState<ClassGroup | null>(null);

  useEffect(() => {
    apiService.getClasses().then(setClasses);
  }, []);

  const handleJoinClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinCode.trim()) return;

    const res = await apiService.joinClassWithCode(joinCode);
    setJoinStatus(res);

    if (res.success) {
      setTimeout(() => {
        setShowModal(false);
        setJoinCode('');
        setJoinStatus(null);
      }, 1500);
    }
  };

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-4xl lg:max-w-5xl mx-auto w-full">
      {/* Header con botón para unirse */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display font-extrabold text-xl md:text-2xl text-[#0A1D2C]">
            Mis Clases
          </h1>
          <p className="text-xs md:text-sm text-[#596B72]">
            Grupos escolares donde tu maestro sigue tu avance con Jarol.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="shrink-0 flex items-center gap-1.5 px-3 md:px-4 py-2 rounded-full bg-[#126B73] text-white font-display font-bold text-xs md:text-sm shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 stroke-[3px]" />
          <span>Unirse</span>
        </button>
      </div>

      {/* Lista de Clases */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {classes.map((cls) => (
          <button
            key={cls.id}
            onClick={() => setSelectedClass(cls)}
            className="w-full text-left p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] hover:border-[#126B73] transition-all flex flex-col gap-2.5 active:translate-y-0.5 cursor-pointer"
          >
            <div className="flex items-start justify-between w-full">
              <div>
                <span className="text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
                  {cls.subject}
                </span>
                <h3 className="font-display font-bold text-base text-[#0A1D2C] mt-1">
                  {cls.name}
                </h3>
                <p className="text-xs text-[#596B72] mt-0.5">
                  Titular: <strong className="text-[#0A1D2C]">{cls.teacherName}</strong>
                </p>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-[11px] font-mono font-bold bg-[#F7F5EF] px-2 py-1 rounded-md border border-[#E8E5DC] text-[#126B73]">
                  {cls.code}
                </span>
                <ChevronRight className="w-4 h-4 text-[#596B72]" />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-[#E8E5DC] text-xs text-[#596B72] w-full">
              <span className="flex items-center gap-1">
                <Users2 className="w-3.5 h-3.5" />
                {cls.studentCount} compañeros
              </span>
              <span className="font-display font-semibold text-[#126B73]">
                {cls.averageMastery}% de avance grupal
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Modal Detalle de Clase */}
      {selectedClass && (
        <ClassDetailModal
          cls={selectedClass}
          onClose={() => setSelectedClass(null)}
          onStartExercise={onStartExercise}
        />
      )}

      {/* Modal Unirse a Clase con Código */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 border border-[#E8E5DC] shadow-xl flex flex-col gap-3.5 animate-scaleUp">
            <h3 className="font-display font-bold text-lg text-[#0A1D2C]">
              Unirte a una clase
            </h3>
            <p className="text-xs text-[#596B72]">
              Ingresa el código que te proporcionó tu maestro (ejemplo: <strong className="font-mono text-[#126B73]">JAROL-3B</strong>).
            </p>

            <form onSubmit={handleJoinClass} className="flex flex-col gap-3">
              <input
                type="text"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                placeholder="Código (ej. JAROL-3B)"
                maxLength={10}
                className="w-full text-center uppercase tracking-widest font-mono font-bold text-lg p-2.5 rounded-xl border-2 border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
              />

              {joinStatus && (
                <div
                  className={`p-2 rounded-lg text-xs font-medium flex items-center gap-1.5 ${
                    joinStatus.success
                      ? 'bg-emerald-50 text-emerald-800'
                      : 'bg-rose-50 text-rose-800'
                  }`}
                >
                  {joinStatus.success ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  )}
                  <span>{joinStatus.message}</span>
                </div>
              )}

              <div className="flex gap-2 mt-1">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 rounded-full border border-[#E8E5DC] text-xs font-display font-semibold text-[#596B72] hover:bg-[#F7F5EF]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 rounded-full bg-[#126B73] text-white text-xs font-display font-bold shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158]"
                >
                  Unirme
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
