import React, { useState } from "react";
import { AudioPlayer, AudioTrack } from "../components/media/AudioPlayer";
import { VideoPlayer } from "../components/media/VideoPlayer";
import { DateRangePicker, DateRange } from "../components/DateRangePicker";

const audioPlaylist: AudioTrack[] = [
  {
    id: "1",
    src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    title: "SoundHelix Song 1",
    artist: "SoundHelix",
    cover: "https://picsum.photos/seed/audio1/200/200.jpg",
  },
  {
    id: "2",
    src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    title: "SoundHelix Song 2",
    artist: "SoundHelix",
    cover: "https://picsum.photos/seed/audio2/200/200.jpg",
  },
  {
    id: "3",
    src: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    title: "SoundHelix Song 3",
    artist: "SoundHelix",
    cover: "https://picsum.photos/seed/audio3/200/200.jpg",
  },
];

const videoSubtitles = [
  {
    src: "https://www.w3schools.com/html/mov_bbb.vtt",
    srcLang: "en",
    label: "English",
  },
];

const MediaDemo: React.FC = () => {
  const [dateRange, setDateRange] = useState<DateRange>({
    start: null,
    end: null,
  });

  const validateDateRange = (range: DateRange): string | null => {
    if (!range.start || !range.end) return null;

    const daysDiff =
      Math.abs(range.end.getTime() - range.start.getTime()) /
      (1000 * 60 * 60 * 24);
    if (daysDiff > 365) {
      return "Date range cannot exceed 365 days";
    }

    if (range.end < range.start) {
      return "End date must be after start date";
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Media Components Demo
          </h1>
          <p className="text-gray-600">
            Showcase of custom media player and date range picker components
          </p>
        </div>

        {/* Audio Player Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Audio Player with Playlist
          </h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <AudioPlayer playlist={audioPlaylist} />
          </div>
        </section>

        {/* Video Player Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Video Player with Subtitles
          </h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <VideoPlayer
              src="https://www.w3schools.com/html/mov_bbb.mp4"
              poster="https://picsum.photos/seed/video/800/450.jpg"
              subtitles={videoSubtitles}
            />
          </div>
        </section>

        {/* Date Range Picker Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Advanced Date Range Picker
          </h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="max-w-md">
              <DateRangePicker
                value={dateRange}
                onChange={setDateRange}
                validation={validateDateRange}
                placeholder="Select date range"
              />
              {dateRange.start && dateRange.end && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">
                    Selected Range:
                  </h3>
                  <p className="text-sm text-gray-600">
                    Start: {dateRange.start.toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    End: {dateRange.end.toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    Duration:{" "}
                    {Math.abs(
                      dateRange.end.getTime() - dateRange.start.getTime(),
                    ) /
                      (1000 * 60 * 60 * 24)}{" "}
                    days
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Component Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Audio Player Features */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Audio Player</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Playlist management
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Playback speed control
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Volume control with mute
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Progress tracking
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Album art display
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Responsive design
                </li>
              </ul>
            </div>

            {/* Video Player Features */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Video Player</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Custom controls
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Subtitle support
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Playback speed control
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Volume control
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Fullscreen support
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Responsive design
                </li>
              </ul>
            </div>

            {/* Date Range Picker Features */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                Date Range Picker
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Preset date ranges
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Custom validation
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Timezone support
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Localization
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Range selection
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Min/max date limits
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default MediaDemo;
