import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Settings, ListMusic, Music } from 'lucide-react';
import { formatDuration } from './utils';

export interface AudioTrack {
  id: string;
  src: string;
  title: string;
  artist?: string;
  cover?: string;
}

interface AudioPlayerProps {
  playlist: AudioTrack[];
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ playlist }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showSettings, setShowSettings] = useState(false);
  const [showPlaylist, setShowPlaylist] = useState(false);

  const currentTrack = playlist[currentTrackIndex];

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      setCurrentTime(audio.currentTime);
      setProgress((audio.currentTime / audio.duration) * 100 || 0);
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      handleNextTrack();
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [currentTrackIndex]);

  useEffect(() => {
    if (isPlaying && audioRef.current) {
      audioRef.current.play().catch(() => setIsPlaying(false));
    }
  }, [currentTrackIndex]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleNextTrack = () => {
    setCurrentTrackIndex((prev) => (prev + 1) % playlist.length);
  };

  const handlePrevTrack = () => {
    setCurrentTrackIndex((prev) => (prev - 1 + playlist.length) % playlist.length);
  };

  const playTrack = (index: number) => {
    setCurrentTrackIndex(index);
    setIsPlaying(true);
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (audioRef.current) {
      const newTime = (Number(e.target.value) / 100) * duration;
      audioRef.current.currentTime = newTime;
      setProgress(Number(e.target.value));
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = Number(e.target.value);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
      setVolume(newVolume);
      if (newVolume === 0) {
        setIsMuted(true);
      } else {
        setIsMuted(false);
      }
    }
  };

  const changePlaybackRate = (rate: number) => {
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
      setPlaybackRate(rate);
      setShowSettings(false);
    }
  };

  if (!playlist || playlist.length === 0) return null;

  return (
    <div className="w-full max-w-md mx-auto bg-gray-900 text-white rounded-xl shadow-2xl overflow-hidden border border-gray-800">
      <audio ref={audioRef} src={currentTrack.src} />
      
      <div className="p-6">
        {/* Album Art & Info */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-20 h-20 bg-gray-800 rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center border border-gray-700 shadow-inner">
            {currentTrack.cover ? (
              <img src={currentTrack.cover} alt="Cover" className="w-full h-full object-cover" />
            ) : (
              <Music size={32} className="text-gray-500" />
            )}
          </div>
          <div className="overflow-hidden">
            <h3 className="text-lg font-bold truncate text-gray-100">{currentTrack.title}</h3>
            <p className="text-sm text-gray-400 truncate">{currentTrack.artist || 'Unknown Artist'}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <input
            type="range"
            min="0"
            max="100"
            value={progress || 0}
            onChange={handleProgressChange}
            className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500 mb-2"
          />
          <div className="flex justify-between text-xs text-gray-400 font-medium">
            <span>{formatDuration(currentTime)}</span>
            <span>{formatDuration(duration)}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button onClick={toggleMute} className="text-gray-400 hover:text-indigo-400 transition">
              {isMuted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-16 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500 hidden sm:block"
            />
          </div>

          <div className="flex items-center space-x-4">
            <button onClick={handlePrevTrack} className="text-gray-400 hover:text-indigo-400 transition">
              <SkipBack size={24} />
            </button>
            <button
              onClick={togglePlay}
              className="w-12 h-12 flex items-center justify-center bg-indigo-600 hover:bg-indigo-500 text-white rounded-full transition shadow-lg shadow-indigo-500/30"
            >
              {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
            </button>
            <button onClick={handleNextTrack} className="text-gray-400 hover:text-indigo-400 transition">
              <SkipForward size={24} />
            </button>
          </div>

          <div className="flex items-center space-x-3 relative">
            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`transition ${showSettings ? 'text-indigo-400' : 'text-gray-400 hover:text-indigo-400'}`}
              >
                <Settings size={18} />
              </button>

              {showSettings && (
                <div className="absolute bottom-full right-0 mb-2 w-32 bg-gray-800 text-white text-sm rounded-md shadow-xl overflow-hidden border border-gray-700 z-10">
                  <div className="px-3 py-2 border-b border-gray-700 font-semibold bg-gray-900 text-xs uppercase tracking-wider text-gray-400">
                    Speed
                  </div>
                  {[0.5, 1, 1.25, 1.5, 2].map((rate) => (
                    <button
                      key={rate}
                      onClick={() => changePlaybackRate(rate)}
                      className={`w-full text-left px-3 py-2 hover:bg-gray-700 transition ${playbackRate === rate ? 'text-indigo-400 font-medium' : 'text-gray-300'}`}
                    >
                      {rate}x {rate === 1 && '(Normal)'}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={() => setShowPlaylist(!showPlaylist)}
              className={`transition ${showPlaylist ? 'text-indigo-400' : 'text-gray-400 hover:text-indigo-400'}`}
            >
              <ListMusic size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Playlist View */}
      {showPlaylist && (
        <div className="border-t border-gray-800 bg-gray-900/50 max-h-60 overflow-y-auto">
          {playlist.map((track, index) => (
            <div
              key={track.id}
              onClick={() => playTrack(index)}
              className={`flex items-center space-x-3 p-3 cursor-pointer transition border-b border-gray-800/50 last:border-0 hover:bg-gray-800 ${
                index === currentTrackIndex ? 'bg-gray-800/80 border-l-2 border-l-indigo-500' : 'border-l-2 border-l-transparent'
              }`}
            >
              <div className="w-10 h-10 bg-gray-800 rounded flex-shrink-0 flex items-center justify-center overflow-hidden">
                {track.cover ? (
                  <img src={track.cover} alt="" className="w-full h-full object-cover" />
                ) : (
                  <Music size={16} className="text-gray-500" />
                )}
              </div>
              <div className="flex-1 overflow-hidden">
                <p className={`text-sm font-medium truncate ${index === currentTrackIndex ? 'text-indigo-400' : 'text-gray-200'}`}>
                  {track.title}
                </p>
                <p className="text-xs text-gray-500 truncate">{track.artist}</p>
              </div>
              {index === currentTrackIndex && isPlaying && (
                <div className="flex space-x-1 w-4 h-4 items-end justify-center">
                  <div className="w-1 bg-indigo-400 animate-[bounce_1s_infinite_0ms]"></div>
                  <div className="w-1 bg-indigo-400 animate-[bounce_1s_infinite_200ms]"></div>
                  <div className="w-1 bg-indigo-400 animate-[bounce_1s_infinite_400ms]"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
