import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronLeft, ChevronRight, Clock, Globe, Check, X } from 'lucide-react';
import { 
  format, 
  addDays, 
  addWeeks, 
  addMonths, 
  startOfDay, 
  endOfDay, 
  startOfWeek, 
  endOfWeek, 
  startOfMonth, 
  endOfMonth,
  isSameDay,
  isWithinInterval,
  parseISO,
  isValid,
  Locale
} from 'date-fns';
import { enUS } from 'date-fns/locale';

export interface DateRange {
  start: Date | null;
  end: Date | null;
}

export interface DateRangePickerProps {
  value?: DateRange;
  onChange?: (range: DateRange) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  locale?: Locale;
  timeZone?: string;
  minDate?: Date;
  maxDate?: Date;
  validation?: (range: DateRange) => string | null;
  presets?: PresetDateRange[];
}

export interface PresetDateRange {
  label: string;
  value: DateRange;
  description?: string;
}

const DEFAULT_PRESETS: PresetDateRange[] = [
  {
    label: 'Today',
    value: { start: startOfDay(new Date()), end: endOfDay(new Date()) },
    description: 'Current day'
  },
  {
    label: 'Yesterday',
    value: { 
      start: startOfDay(addDays(new Date(), -1)), 
      end: endOfDay(addDays(new Date(), -1)) 
    },
    description: 'Previous day'
  },
  {
    label: 'This Week',
    value: { 
      start: startOfWeek(new Date(), { weekStartsOn: 0 }), 
      end: endOfWeek(new Date(), { weekStartsOn: 0 }) 
    },
    description: 'Sunday to Saturday'
  },
  {
    label: 'Last Week',
    value: { 
      start: startOfWeek(addWeeks(new Date(), -1), { weekStartsOn: 0 }), 
      end: endOfWeek(addWeeks(new Date(), -1), { weekStartsOn: 0 }) 
    },
    description: 'Previous week'
  },
  {
    label: 'This Month',
    value: { 
      start: startOfMonth(new Date()), 
      end: endOfMonth(new Date()) 
    },
    description: 'Current month'
  },
  {
    label: 'Last Month',
    value: { 
      start: startOfMonth(addMonths(new Date(), -1)), 
      end: endOfMonth(addMonths(new Date(), -1)) 
    },
    description: 'Previous month'
  },
  {
    label: 'Last 7 Days',
    value: { 
      start: startOfDay(addDays(new Date(), -7)), 
      end: endOfDay(new Date()) 
    },
    description: 'Past week'
  },
  {
    label: 'Last 30 Days',
    value: { 
      start: startOfDay(addDays(new Date(), -30)), 
      end: endOfDay(new Date()) 
    },
    description: 'Past month'
  }
];

const TIME_ZONES = [
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern Time' },
  { value: 'America/Chicago', label: 'Central Time' },
  { value: 'America/Denver', label: 'Mountain Time' },
  { value: 'America/Los_Angeles', label: 'Pacific Time' },
  { value: 'Europe/London', label: 'London' },
  { value: 'Europe/Paris', label: 'Paris' },
  { value: 'Asia/Tokyo', label: 'Tokyo' },
  { value: 'Asia/Shanghai', label: 'Shanghai' },
  { value: 'Australia/Sydney', label: 'Sydney' }
];

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value = { start: null, end: null },
  onChange,
  placeholder = 'Select date range',
  disabled = false,
  className = '',
  locale = enUS,
  timeZone = 'UTC',
  minDate,
  maxDate,
  validation,
  presets = DEFAULT_PRESETS
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectingEnd, setSelectingEnd] = useState(false);
  const [hoveredDate, setHoveredDate] = useState<Date | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [selectedTimeZone, setSelectedTimeZone] = useState(timeZone);
  const [showPresets, setShowPresets] = useState(true);
  const [showTimeZoneSelector, setShowTimeZoneSelector] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (validation) {
      const error = validation(value);
      setValidationError(error);
    }
  }, [value, validation]);

  const handleDateClick = (date: Date) => {
    if (disabled) return;

    if (minDate && date < minDate) return;
    if (maxDate && date > maxDate) return;

    if (!selectingEnd || !value.start) {
      const newRange = { start: date, end: null };
      onChange?.(newRange);
      setSelectingEnd(true);
    } else {
      const newRange = { 
        start: date < value.start ? date : value.start, 
        end: date >= value.start ? date : value.start 
      };
      onChange?.(newRange);
      setSelectingEnd(false);
      setIsOpen(false);
    }
  };

  const handlePresetClick = (preset: PresetDateRange) => {
    if (disabled) return;
    onChange?.(preset.value);
    setSelectingEnd(false);
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange?.({ start: null, end: null });
    setSelectingEnd(false);
  };

  const formatDateDisplay = () => {
    if (value.start && value.end) {
      const start = format(value.start, 'MMM dd, yyyy', { locale });
      const end = format(value.end, 'MMM dd, yyyy', { locale });
      return `${start} - ${end}`;
    } else if (value.start) {
      return format(value.start, 'MMM dd, yyyy', { locale });
    }
    return placeholder;
  };

  const isDateSelected = (date: Date) => {
    if (!value.start) return false;
    if (value.end && isSameDay(date, value.end)) return true;
    return isSameDay(date, value.start);
  };

  const isDateInRange = (date: Date) => {
    if (!value.start || !value.end) return false;
    return isWithinInterval(date, { start: value.start, end: value.end });
  };

  const isDateHovered = (date: Date) => {
    if (!hoveredDate || !value.start || value.end) return false;
    return isWithinInterval(date, { 
      start: hoveredDate < value.start ? hoveredDate : value.start, 
      end: hoveredDate > value.start ? hoveredDate : value.start 
    });
  };

  const renderCalendar = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = startOfWeek(firstDay, { weekStartsOn: 0 });
    const endDate = endOfWeek(lastDay, { weekStartsOn: 0 });

    const days = [];
    const current = startDate;

    while (current <= endDate) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, -1))}
            className="p-1 hover:bg-gray-100 rounded transition"
          >
            <ChevronLeft size={20} />
          </button>
          <h3 className="font-semibold text-gray-900">
            {format(currentMonth, 'MMMM yyyy', { locale })}
          </h3>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-1 hover:bg-gray-100 rounded transition"
          >
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Week days */}
        <div className="grid grid-cols-7 gap-1 p-4">
          {weekDays.map(day => (
            <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar days */}
        <div className="grid grid-cols-7 gap-1 p-4 pt-0">
          {days.map((date, index) => {
            const isCurrentMonth = date.getMonth() === month;
            const isSelected = isDateSelected(date);
            const isInRange = isDateInRange(date);
            const isHovered = isDateHovered(date);
            const isDisabled = (minDate && date < minDate) || (maxDate && date > maxDate);
            const isToday = isSameDay(date, new Date());

            return (
              <button
                key={index}
                onClick={() => handleDateClick(date)}
                onMouseEnter={() => setHoveredDate(date)}
                onMouseLeave={() => setHoveredDate(null)}
                disabled={isDisabled}
                className={`
                  relative p-2 text-sm rounded transition-all
                  ${!isCurrentMonth ? 'text-gray-400' : 'text-gray-900'}
                  ${isDisabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:bg-gray-100'}
                  ${isSelected ? 'bg-blue-500 text-white hover:bg-blue-600' : ''}
                  ${isInRange && !isSelected ? 'bg-blue-100' : ''}
                  ${isHovered && !isSelected && !isInRange ? 'bg-blue-50' : ''}
                  ${isToday && !isSelected ? 'font-bold border border-blue-300' : ''}
                `}
              >
                {format(date, 'd')}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={formatDateDisplay()}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          readOnly
          disabled={disabled}
          placeholder={placeholder}
          className={`
            w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'}
            ${validationError ? 'border-red-500' : ''}
          `}
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
          {value.start && (
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition"
            >
              <X size={16} />
            </button>
          )}
          <Calendar size={20} className="text-gray-400" />
        </div>
      </div>

      {/* Validation Error */}
      {validationError && (
        <div className="mt-1 text-sm text-red-600">
          {validationError}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="flex">
            {/* Presets Panel */}
            {showPresets && (
              <div className="w-64 border-r border-gray-200">
                <div className="p-4 border-b border-gray-200">
                  <h4 className="font-semibold text-gray-900">Quick Select</h4>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {presets.map((preset, index) => (
                    <button
                      key={index}
                      onClick={() => handlePresetClick(preset)}
                      className="w-full text-left p-3 hover:bg-gray-50 transition border-b border-gray-100 last:border-0"
                    >
                      <div className="font-medium text-gray-900">{preset.label}</div>
                      {preset.description && (
                        <div className="text-sm text-gray-500">{preset.description}</div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Calendar Panel */}
            <div className="flex-1">
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setShowPresets(!showPresets)}
                    className="text-sm text-blue-600 hover:text-blue-700 transition"
                  >
                    {showPresets ? 'Hide' : 'Show'} Presets
                  </button>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="relative">
                    <button
                      onClick={() => setShowTimeZoneSelector(!showTimeZoneSelector)}
                      className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-900 transition"
                    >
                      <Globe size={16} />
                      <span>{selectedTimeZone}</span>
                    </button>
                    {showTimeZoneSelector && (
                      <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                        {TIME_ZONES.map(tz => (
                          <button
                            key={tz.value}
                            onClick={() => {
                              setSelectedTimeZone(tz.value);
                              setShowTimeZoneSelector(false);
                            }}
                            className="w-full text-left px-3 py-2 hover:bg-gray-50 transition text-sm"
                          >
                            {tz.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="p-4">
                {renderCalendar()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
