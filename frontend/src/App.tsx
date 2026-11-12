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
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { LoginPage } from './views/auth/LoginPage';
import { RegisterPage } from './views/auth/RegisterPage';
import { VerificationPendingPage, VerifyEmailPage, VerificationSuccessPage, VerificationInvalidPage, RecoveryPlaceholderPage } from './views/auth/VerificationPages';
import { defaultPathForRole, routeRedirect, tabPaths } from './routing';
import { ProfileView } from './views/ProfileView';

const MainShell: React.FC = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate(); const { pathname } = useLocation();
  const defaultTab = role === 'student' ? 'chat' : 'clases';
  const currentTab = Object.entries(tabPaths).find(([, path]) => path === pathname)?.[0] || defaultTab;
  const setCurrentTab = (tab: string) => navigate(tabPaths[tab] || defaultPathForRole(role));
  const openProfile = () => navigate('/perfil');
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

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
        onOpenProfile={openProfile}
      />

      {/* Área de Contenido Principal Responsiva */}
      <div className="flex-1 flex flex-col min-h-screen w-full min-w-0 relative">
        {/* Cabecera Móvil (se oculta en Desktop donde el Sidebar ya provee el branding) */}
        <AppHeader
            onOpenProfile={openProfile}
        />

        {/* Vistas Principales */}
        <main className="flex-1 flex flex-col overflow-y-auto">
          {currentTab === 'profile' && <ProfileView onBack={() => setCurrentTab(defaultTab)}/>}
          {role === 'student' ? (
            <>
              <div hidden={currentTab !== 'chat'} className="flex-1">
                <ChatView key={user.id}
                  initialPrompt={pendingPrompt}
                  onPromptConsumed={() => setPendingPrompt(null)}
                />
              </div>
              {currentTab === 'retos' && <ChallengesView onStartTopic={handleStartTopic} />}
              {currentTab === 'ligas' && <LeaguesView onGoPractice={() => setCurrentTab('chat')} />}
              {currentTab === 'clases' && (
                <ClassesView onStartExercise={handleStartTopic} />
              )}
              {currentTab === 'progreso' && <ProgressView onPracticeTopic={handleStartTopic} />}
            </>
          ) : (
            currentTab !== 'profile' && (
              <TeacherDashboardView
                activeTab={currentTab === 'panel' || currentTab === 'alumnos' ? currentTab : 'clases'}
                onTabChange={setCurrentTab}
              />
            )
          )}
        </main>

        {/* Navegación Inferior (se oculta en Desktop md:hidden) */}
        <BottomNav currentTab={currentTab} onTabChange={setCurrentTab} />



      </div>
    </div>
  );
};

function AppRoutes() {
  const { isAuthenticated, isLoading, role } = useAuth(); const { pathname } = useLocation();
  if (isLoading) return <main className="flex min-h-dvh items-center justify-center bg-canvas p-6"><p role="status">Recuperando tu sesión…</p></main>;
  const redirect = routeRedirect(pathname, isAuthenticated, role);
  if (redirect) return <Navigate to={redirect} replace/>;
  return <Routes>
    <Route path="/login" element={<LoginPage/>}/>
    <Route path="/registro" element={<RegisterPage/>}/>
    <Route path="/verificacion-pendiente" element={<VerificationPendingPage/>}/>
    <Route path="/verificar-correo/:uid/:token" element={<VerifyEmailPage/>}/>
    <Route path="/verificacion-exitosa" element={<VerificationSuccessPage/>}/>
    <Route path="/verificacion-invalida" element={<VerificationInvalidPage/>}/>
    <Route path="/recuperar-contrasena" element={<RecoveryPlaceholderPage/>}/>
    <Route path="/*" element={<MainShell/>}/>
  </Routes>;
}

export function App() {
  return <BrowserRouter><AuthProvider><AppRoutes/></AuthProvider></BrowserRouter>;
}
export default App;
