import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Settings, Subtitles } from 'lucide-react';
import { formatDuration } from './utils';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  subtitles?: { src: string; srcLang: string; label: string }[];
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ src, poster, subtitles }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showSettings, setShowSettings] = useState(false);
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const updateProgress = () => {
      setCurrentTime(video.currentTime);
      setProgress((video.currentTime / video.duration) * 100);
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    video.addEventListener('timeupdate', updateProgress);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);

    return () => {
      video.removeEventListener('timeupdate', updateProgress);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
  }, []);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (videoRef.current) {
      const newTime = (Number(e.target.value) / 100) * duration;
      videoRef.current.currentTime = newTime;
      setProgress(Number(e.target.value));
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = Number(e.target.value);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setVolume(newVolume);
      if (newVolume === 0) {
        setIsMuted(true);
      } else {
        setIsMuted(false);
      }
    }
  };

  const changePlaybackRate = (rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setPlaybackRate(rate);
      setShowSettings(false);
    }
  };

  const toggleFullscreen = () => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        containerRef.current.requestFullscreen();
      }
    }
  };

  const toggleSubtitles = () => {
    if (videoRef.current) {
      const tracks = videoRef.current.textTracks;
      if (tracks.length > 0) {
        const track = tracks[0];
        if (subtitlesEnabled) {
          track.mode = 'hidden';
        } else {
          track.mode = 'showing';
        }
        setSubtitlesEnabled(!subtitlesEnabled);
      }
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full max-w-4xl mx-auto bg-black rounded-lg overflow-hidden group shadow-lg sm:max-w-5xl lg:max-w-6xl"
    >
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full h-auto cursor-pointer"
        onClick={togglePlay}
        crossOrigin="anonymous"
      >
        {subtitles?.map((sub, index) => (
          <track
            key={index}
            kind="subtitles"
            src={sub.src}
            srcLang={sub.srcLang}
            label={sub.label}
            default={index === 0}
          />
        ))}
      </video>

      {/* Controls Overlay */}
      <div className="absolute bottom-0 left-0 right-0 p-3 sm:p-4 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        {/* Progress Bar */}
        <input
          type="range"
          min="0"
          max="100"
          value={progress || 0}
          onChange={handleProgressChange}
          className="w-full h-1 mb-4 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />

        <div className="flex items-center justify-between text-white">
          <div className="flex items-center space-x-4">
            <button onClick={togglePlay} className="hover:text-blue-400 transition">
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>

            <div className="flex items-center space-x-2">
              <button onClick={toggleMute} className="hover:text-blue-400 transition">
                {isMuted || volume === 0 ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div className="text-sm font-medium">
              {formatDuration(currentTime)} / {formatDuration(duration)}
            </div>
          </div>

          <div className="flex items-center space-x-4 relative">
            {subtitles && subtitles.length > 0 && (
              <button
                onClick={toggleSubtitles}
                className={`hover:text-blue-400 transition ${subtitlesEnabled ? 'text-blue-500' : ''}`}
                title="Toggle Subtitles"
              >
                <Subtitles size={20} />
              </button>
            )}

            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="hover:text-blue-400 transition flex items-center"
              >
                <Settings size={20} />
              </button>

              {showSettings && (
                <div className="absolute bottom-full right-0 mb-2 w-32 bg-gray-800 text-white text-sm rounded-md shadow-lg overflow-hidden border border-gray-700">
                  <div className="px-3 py-2 border-b border-gray-700 font-semibold bg-gray-900">
                    Speed
                  </div>
                  {[0.5, 1, 1.5, 2].map((rate) => (
                    <button
                      key={rate}
                      onClick={() => changePlaybackRate(rate)}
                      className={`w-full text-left px-3 py-2 hover:bg-gray-700 transition ${playbackRate === rate ? 'text-blue-400' : ''}`}
                    >
                      {rate}x {rate === 1 && '(Normal)'}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button onClick={toggleFullscreen} className="hover:text-blue-400 transition">
              <Maximize size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
