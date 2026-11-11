import React, { useState } from 'react';
import type { ClassGroup } from '../../types/curriculum';
import { X, Users2, BookOpen, Bell, ArrowRight, CheckCircle2 } from 'lucide-react';

interface ClassDetailModalProps {
  cls: ClassGroup;
  onClose: () => void;
  onStartExercise?: (topic: string) => void;
}

export const ClassDetailModal: React.FC<ClassDetailModalProps> = ({
  cls,
  onClose,
  onStartExercise,
}) => {
  const [activeTab, setActiveTab] = useState<'retos' | 'alumnos' | 'avisos'>('retos');

  const mockClassmates = [
    { name: 'Mateo Hernández', xp: 450, status: 'Al corriente' },
    { name: 'Sofía Morales', xp: 380, status: 'Al corriente' },
    { name: 'Emiliano Valdés (Tú)', xp: 320, status: 'Al corriente' },
    { name: 'Carlos Yépez', xp: 340, status: 'Practicando' },
    { name: 'Valeria Cruz', xp: 290, status: 'Al corriente' },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border border-[#E8E5DC] shadow-2xl flex flex-col animate-scaleUp">
        {/* Header */}
        <div className="sticky top-0 bg-[#F7F5EF] p-4 pb-2 border-b border-[#E8E5DC] flex items-center justify-between z-10">
          <div>
            <span className="text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
              {cls.subject}
            </span>
            <h2 className="font-display font-extrabold text-base text-[#0A1D2C] mt-1">
              {cls.name}
            </h2>
            <p className="text-xs text-[#596B72]">
              Titular: <strong className="text-[#0A1D2C]">{cls.teacherName}</strong> · Código:{' '}
              <span className="font-mono font-bold text-[#126B73]">{cls.code}</span>
            </p>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:text-[#0A1D2C] active:scale-95"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pestañas internas */}
        <div className="flex border-b border-[#E8E5DC] bg-white px-3 pt-2">
          <button
            onClick={() => setActiveTab('retos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all ${
              activeTab === 'retos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Retos Asignados</span>
          </button>

          <button
            onClick={() => setActiveTab('alumnos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all ${
              activeTab === 'alumnos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <Users2 className="w-3.5 h-3.5" />
            <span>Compañeros ({cls.studentCount})</span>
          </button>

          <button
            onClick={() => setActiveTab('avisos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all ${
              activeTab === 'avisos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Avisos (1)</span>
          </button>
        </div>

        {/* Contenido según pestaña */}
        <div className="p-4 flex flex-col gap-3">
          {activeTab === 'retos' && (
            <div className="flex flex-col gap-2.5">
              <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] shadow-2xs flex flex-col gap-2">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-[#E76D55] uppercase">
                      Activo esta semana
                    </span>
                    <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                      Suma y Resta de Fracciones con igual denominador
                    </h3>
                    <p className="text-xs text-[#596B72] mt-0.5">
                      3 ejercicios interactivos con ejemplos guiados por Jarol.
                    </p>
                  </div>
                  <span className="text-xs font-bold text-[#126B73] bg-[#DCEFEB] px-2 py-0.5 rounded-full">
                    +60 XP
                  </span>
                </div>

                <button
                  onClick={() => {
                    onClose();
                    if (onStartExercise) onStartExercise('Fracciones');
                  }}
                  className="w-full mt-1 py-2 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-1.5 shadow-[0_2px_0_#005158] active:translate-y-0.5"
                >
                  <span>Resolver con Jarol</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] opacity-70 flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold text-[#596B72] uppercase">
                    Próxima semana
                  </span>
                  <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                    Fracciones equivalentes y mínimo común múltiplo
                  </h3>
                </div>
                <span className="text-[11px] text-[#596B72] font-medium">Bloqueado</span>
              </div>
            </div>
          )}

          {activeTab === 'alumnos' && (
            <div className="flex flex-col gap-2">
              {mockClassmates.map((mate, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] flex items-center justify-between"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-full bg-[#DCEFEB] text-[#126B73] font-display font-bold text-xs flex items-center justify-center">
                      {mate.name[0]}
                    </div>
                    <div>
                      <span className="font-display font-bold text-xs text-[#0A1D2C] block">
                        {mate.name}
                      </span>
                      <span className="text-[10px] text-[#596B72]">{mate.status}</span>
                    </div>
                  </div>

                  <span className="text-xs font-display font-semibold text-[#126B73]">
                    {mate.xp} XP
                  </span>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'avisos' && (
            <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#126B73]" />
                <span className="font-display font-bold text-xs text-[#0A1D2C]">
                  Aviso de la Prof. Laura Mendoza
                </span>
              </div>
              <p className="text-xs text-[#3F484A] leading-relaxed">
                "¡Hola muchachos! Recuerden practicar con Jarol el tema de fracciones. Fíjense bien en que cuando los denominadores son iguales, solo se suman los números de arriba. ¡Ánimo!"
              </p>
              <span className="text-[10px] text-[#596B72] mt-1">Publicado hoy, 9:00 AM</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
