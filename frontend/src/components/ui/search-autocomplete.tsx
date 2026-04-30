import * as React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import { useDebounce } from "../../hooks/useDebounce";
import { cn } from "../../utils/cn";
import { Input } from "./input";
import { Loader2, Search } from "lucide-react";

export interface SearchSuggestion {
  id: string;
  label: string;
  value: string;
  description?: string;
}

export interface SearchAutocompleteProps {
  onSearch: (query: string) => Promise<SearchSuggestion[]>;
  onSelect: (suggestion: SearchSuggestion) => void;
  placeholder?: string;
  debounceDelay?: number;
  className?: string;
  inputClassName?: string;
  disabled?: boolean;
  noResultsMessage?: string;
  loadingMessage?: string;
  minQueryLength?: number;
  maxSuggestions?: number;
  showSearchIcon?: boolean;
}

const SearchAutocomplete = React.forwardRef<
  HTMLInputElement,
  SearchAutocompleteProps
>(
  (
    {
      onSearch,
      onSelect,
      placeholder = "Search...",
      debounceDelay = 300,
      className,
      inputClassName,
      disabled = false,
      noResultsMessage = "No results found",
      loadingMessage = "Searching...",
      minQueryLength = 2,
      maxSuggestions = 10,
      showSearchIcon = true,
      ...props
    },
    ref,
  ) => {
    const [query, setQuery] = useState("");
    const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const [error, setError] = useState<string | null>(null);

    const debouncedQuery = useDebounce(query, debounceDelay);
    const inputRef = useRef<HTMLInputElement>(null);
    const listRef = useRef<HTMLUListElement>(null);

    // Handle search API calls
    useEffect(() => {
      if (debouncedQuery.length < minQueryLength) {
        setSuggestions([]);
        setIsOpen(false);
        return;
      }

      const fetchSuggestions = async () => {
        try {
          setIsLoading(true);
          setError(null);
          const results = await onSearch(debouncedQuery);
          const limitedResults = results.slice(0, maxSuggestions);
          setSuggestions(limitedResults);
          setIsOpen(limitedResults.length > 0);
          setSelectedIndex(-1);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Search failed");
          setSuggestions([]);
          setIsOpen(false);
        } finally {
          setIsLoading(false);
        }
      };

      fetchSuggestions();
    }, [debouncedQuery, onSearch, minQueryLength, maxSuggestions]);

    // Handle keyboard navigation
    const handleKeyDown = useCallback(
      (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (!isOpen && (event.key === "ArrowDown" || event.key === "ArrowUp")) {
          event.preventDefault();
          return;
        }

        switch (event.key) {
          case "ArrowDown":
            event.preventDefault();
            setSelectedIndex((prev) => {
              const nextIndex = prev < suggestions.length - 1 ? prev + 1 : prev;
              if (nextIndex >= 0 && listRef.current?.children[nextIndex]) {
                (
                  listRef.current.children[nextIndex] as HTMLElement
                ).scrollIntoView({
                  block: "nearest",
                });
              }
              return nextIndex;
            });
            break;

          case "ArrowUp":
            event.preventDefault();
            setSelectedIndex((prev) => {
              const nextIndex = prev > 0 ? prev - 1 : -1;
              if (nextIndex >= 0 && listRef.current?.children[nextIndex]) {
                (
                  listRef.current.children[nextIndex] as HTMLElement
                ).scrollIntoView({
                  block: "nearest",
                });
              }
              return nextIndex;
            });
            break;

          case "Enter":
            event.preventDefault();
            if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
              handleSelect(suggestions[selectedIndex]);
            }
            break;

          case "Escape":
            setIsOpen(false);
            setSelectedIndex(-1);
            inputRef.current?.blur();
            break;
        }
      },
      [isOpen, suggestions, selectedIndex],
    );

    const handleSelect = useCallback(
      (suggestion: SearchSuggestion) => {
        setQuery(suggestion.value);
        setIsOpen(false);
        setSelectedIndex(-1);
        onSelect(suggestion);
      },
      [onSelect],
    );

    const handleInputChange = useCallback(
      (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setQuery(value);
        if (value.length === 0) {
          setIsOpen(false);
          setSelectedIndex(-1);
        }
      },
      [],
    );

    const handleInputFocus = useCallback(() => {
      if (suggestions.length > 0 && query.length >= minQueryLength) {
        setIsOpen(true);
      }
    }, [suggestions, query, minQueryLength]);

    const handleInputBlur = useCallback(() => {
      // Delay closing to allow clicking on suggestions
      setTimeout(() => {
        setIsOpen(false);
        setSelectedIndex(-1);
      }, 150);
    }, []);

    // Highlight matching text in suggestions
    const highlightText = (text: string, query: string) => {
      if (!query) return text;
      const parts = text.split(new RegExp(`(${query})`, "gi"));
      return parts.map((part, index) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <mark
            key={index}
            className="bg-yellow-200 text-yellow-900 rounded px-0.5"
          >
            {part}
          </mark>
        ) : (
          part
        ),
      );
    };

    const leftIcon = showSearchIcon ? (
      <Search className="h-4 w-4" />
    ) : undefined;
    const rightIcon = isLoading ? (
      <Loader2 className="h-4 w-4 animate-spin" />
    ) : undefined;

    return (
      <div className={cn("relative w-full", className)}>
        <Input
          ref={ref || inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          leftIcon={leftIcon}
          rightIcon={rightIcon}
          disabled={disabled}
          className={inputClassName}
          {...props}
        />

        {/* Suggestions dropdown */}
        {isOpen && (
          <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-background border border-input rounded-md shadow-lg max-h-64 overflow-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-4 text-muted-foreground">
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {loadingMessage}
              </div>
            ) : error ? (
              <div className="py-4 px-3 text-destructive text-sm">{error}</div>
            ) : suggestions.length === 0 && query.length >= minQueryLength ? (
              <div className="py-4 px-3 text-muted-foreground text-sm">
                {noResultsMessage}
              </div>
            ) : (
              <ul ref={listRef} className="py-1">
                {suggestions.map((suggestion, index) => (
                  <li
                    key={suggestion.id}
                    className={cn(
                      "px-3 py-2 cursor-pointer text-sm transition-colors",
                      selectedIndex === index &&
                        "bg-accent text-accent-foreground",
                      selectedIndex !== index && "hover:bg-accent/50",
                    )}
                    onClick={() => handleSelect(suggestion)}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <div className="flex flex-col">
                      <div className="font-medium">
                        {highlightText(suggestion.label, query)}
                      </div>
                      {suggestion.description && (
                        <div className="text-muted-foreground text-xs mt-1">
                          {highlightText(suggestion.description, query)}
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    );
  },
);

SearchAutocomplete.displayName = "SearchAutocomplete";

export { SearchAutocomplete };
