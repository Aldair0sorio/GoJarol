import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppHeader } from './components/layout/AppHeader';
import { BottomNav } from './components/layout/BottomNav';
import { DesktopSidebar } from './components/layout/DesktopSidebar';
import { ChatView } from './views/student/ChatView';
import { ChallengesView } from './views/student/ChallengesView';
import { LeaguesView } from './views/student/LeaguesView';
import { ClassesView } from './views/student/ClassesView';
import { ProgressView } from './views/student/ProgressView';
import { TeacherDashboardView } from './views/teacher/TeacherDashboardView';
import { AuthModal } from './components/auth/AuthModal';
import { ProfileModal } from './components/profile/ProfileModal';

const MainShell: React.FC = () => {
  const { role, isAuthenticated } = useAuth();
  const [currentTab, setCurrentTab] = useState('chat');
  const [showAuthModal, setShowAuthModal] = useState(!isAuthenticated);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

  // Al montar o si no está autenticado, abrir el modal de autenticación
  React.useEffect(() => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
    }
  }, [isAuthenticated]);

  // Sincronizar tab al cambiar de rol
  React.useEffect(() => {
    if (role === 'teacher') {
      setCurrentTab('panel');
    } else {
      setCurrentTab('chat');
    }
  }, [role]);

  const handleStartTopic = (topicOrPrompt?: string) => {
    if (topicOrPrompt) {
      setPendingPrompt(topicOrPrompt);
    }
    setCurrentTab('chat');
  };

  return (
    <div className="w-full min-h-screen bg-[#F7F5EF] flex flex-col md:flex-row antialiased selection:bg-[#DCEFEB]">
      {/* Sidebar de navegación en Tablet y Desktop (md: y lg:) */}
      <DesktopSidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        onOpenProfile={() => setShowProfileModal(true)}
        onOpenAuth={() => setShowAuthModal(true)}
      />

      {/* Área de Contenido Principal Responsiva */}
      <div className="flex-1 flex flex-col min-h-screen w-full relative">
        {/* Cabecera Móvil (se oculta en Desktop donde el Sidebar ya provee el branding) */}
        <AppHeader
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
        />

        {/* Vistas Principales */}
        <main className="flex-1 flex flex-col overflow-y-auto">
          {role === 'student' ? (
            <>
              {currentTab === 'chat' && (
                <ChatView
                  initialPrompt={pendingPrompt}
                  onPromptConsumed={() => setPendingPrompt(null)}
                />
              )}
              {currentTab === 'retos' && <ChallengesView onStartTopic={handleStartTopic} />}
              {currentTab === 'ligas' && <LeaguesView onGoPractice={() => setCurrentTab('chat')} />}
              {currentTab === 'clases' && (
                <ClassesView onStartExercise={handleStartTopic} />
              )}
              {currentTab === 'progreso' && <ProgressView onPracticeTopic={handleStartTopic} />}
            </>
          ) : (
            <TeacherDashboardView />
          )}
        </main>

        {/* Navegación Inferior (se oculta en Desktop md:hidden) */}
        <BottomNav currentTab={currentTab} onTabChange={setCurrentTab} />

        {/* Modal de Autenticación / Registro */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />

        {/* Modal de Perfil y Logros */}
        <ProfileModal
          isOpen={showProfileModal}
          onClose={() => setShowProfileModal(false)}
          onOpenAuth={() => setShowAuthModal(true)}
        />
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainShell />
    </AuthProvider>
  );
}

export default App;
