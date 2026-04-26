import React, { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';

const InstallPWA: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handler = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }
    
    setDeferredPrompt(null);
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-24 right-4 z-50 animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="bg-primary text-primary-foreground p-4 rounded-2xl shadow-2xl border border-primary/20 flex items-center gap-4 max-w-sm">
        <div className="bg-white/10 p-2 rounded-xl">
          <Download size={24} />
        </div>
        <div className="flex-1">
          <p className="font-bold text-sm">Install App</p>
          <p className="text-xs opacity-90">Install TTL Archival for a better offline experience.</p>
        </div>
        <div className="flex flex-col gap-2">
          <button 
            onClick={handleInstall}
            className="px-4 py-1.5 bg-white text-primary rounded-lg text-xs font-bold hover:bg-opacity-90 transition-all"
          >
            Install
          </button>
          <button 
            onClick={() => setIsVisible(false)}
            className="text-[10px] opacity-70 hover:opacity-100 flex items-center justify-center gap-1"
          >
            <X size={10} />
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstallPWA;
