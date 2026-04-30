import React from "react";
import { VideoPlayer } from "../components/media/VideoPlayer";
import { AudioPlayer, AudioTrack } from "../components/media/AudioPlayer";

const samplePlaylist: AudioTrack[] = [
  {
    id: "1",
    src: "https://actions.google.com/sounds/v1/water/rain_on_roof.ogg",
    title: "Rain on Roof",
    artist: "Nature Sounds",
    cover:
      "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
  },
  {
    id: "2",
    src: "https://actions.google.com/sounds/v1/weather/thunderstorm_heavy.ogg",
    title: "Heavy Thunderstorm",
    artist: "Nature Sounds",
    cover:
      "https://images.unsplash.com/photo-1605727216801-e27ce1d0ce49?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
  },
  {
    id: "3",
    src: "https://actions.google.com/sounds/v1/water/waves_crashing_on_rock_beach.ogg",
    title: "Waves Crashing",
    artist: "Ocean Sounds",
    cover:
      "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
  },
];

const sampleVideo = {
  src: "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  poster: "https://peach.blender.org/wp-content/uploads/title_anouncement.jpg",
  subtitles: [
    {
      src: "data:text/vtt;charset=utf-8,WEBVTT%0A%0A1%0A00:00:01.000%20--%3E%2000:00:05.000%0AWelcome%20to%20Big%20Buck%20Bunny!%0A",
      srcLang: "en",
      label: "English",
    },
  ],
};

export const MediaPlayground: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Media Components
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Showcase of the custom media players with advanced controls.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        {/* Video Player Section */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
              Video Player
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Custom controls, playback speed, subtitles, and fullscreen
              support.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <VideoPlayer
              src={sampleVideo.src}
              poster={sampleVideo.poster}
              subtitles={sampleVideo.subtitles}
            />
          </div>
        </div>

        {/* Audio Player Section */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
              Audio Player
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Playlist management, album art, custom controls, and playback
              speed.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <AudioPlayer playlist={samplePlaylist} />
          </div>
        </div>
      </div>
    </div>
  );
};
