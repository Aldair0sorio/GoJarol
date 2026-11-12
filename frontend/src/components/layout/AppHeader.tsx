import { AccountMenu } from '../profile/AccountMenu';

export function AppHeader({ onOpenProfile }: { onOpenProfile?: () => void }) {
  return <header className="sticky top-0 z-40 border-b border-[#E8E5DC] bg-[#F7F5EF]/95 px-3 py-2 backdrop-blur-md md:hidden">
    <div className="mx-auto flex max-w-2xl min-w-0 items-center justify-between gap-2">
      <div className="flex shrink-0 items-center gap-2"><img src="/mascot/jarol-crab.png" alt="" className="h-10 w-10 object-contain"/><span className="font-display text-lg font-bold text-[#0A1D2C]">Go Jarol</span></div>
      <AccountMenu onOpenProfile={() => onOpenProfile?.()}/>
    </div>
  </header>;
}
