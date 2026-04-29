import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  SearchAutocomplete,
  type SearchSuggestion,
} from "./search-autocomplete";

// Mock lucide-react icons
jest.mock("lucide-react", () => ({
  Search: () => <div data-testid="search-icon">Search</div>,
  Loader2: () => <div data-testid="loader-icon">Loading</div>,
}));

describe("SearchAutocomplete", () => {
  const mockSuggestions: SearchSuggestion[] = [
    {
      id: "1",
      label: "Apple iPhone",
      value: "Apple iPhone",
      description: "Latest smartphone",
    },
    {
      id: "2",
      label: "Apple MacBook",
      value: "Apple MacBook",
      description: "Professional laptop",
    },
    {
      id: "3",
      label: "Apple iPad",
      value: "Apple iPad",
      description: "Tablet device",
    },
  ];

  const mockSearch = jest.fn().mockImplementation(async (query: string) => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 100));
    return mockSuggestions.filter((suggestion) =>
      suggestion.label.toLowerCase().includes(query.toLowerCase()),
    );
  });

  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders input with placeholder", () => {
    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        placeholder="Search products..."
      />,
    );

    expect(
      screen.getByPlaceholderText("Search products..."),
    ).toBeInTheDocument();
  });

  it("shows search icon by default", () => {
    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    expect(screen.getByTestId("search-icon")).toBeInTheDocument();
  });

  it("hides search icon when showSearchIcon is false", () => {
    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        showSearchIcon={false}
      />,
    );

    expect(screen.queryByTestId("search-icon")).not.toBeInTheDocument();
  });

  it("does not show suggestions for short queries", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        minQueryLength={2}
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "a");

    // Should not call search for queries shorter than minQueryLength
    expect(mockSearch).not.toHaveBeenCalled();

    // Should not show suggestions dropdown
    await waitFor(() => {
      expect(screen.queryByRole("list")).not.toBeInTheDocument();
    });
  });

  it("shows suggestions after typing valid query", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        minQueryLength={2}
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(mockSearch).toHaveBeenCalledWith("Apple");
    });

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
      expect(screen.getByText("Apple iPhone")).toBeInTheDocument();
      expect(screen.getByText("Apple MacBook")).toBeInTheDocument();
      expect(screen.getByText("Apple iPad")).toBeInTheDocument();
    });
  });

  it("shows loading state during search", async () => {
    const user = userEvent.setup();
    let resolveSearch: (value: SearchSuggestion[]) => void;

    mockSearch.mockImplementationOnce(() => {
      return new Promise((resolve) => {
        resolveSearch = resolve;
      });
    });

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        loadingMessage="Searching..."
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByTestId("loader-icon")).toBeInTheDocument();
      expect(screen.getByText("Searching...")).toBeInTheDocument();
    });

    // Resolve the search
    resolveSearch!(mockSuggestions);

    await waitFor(() => {
      expect(screen.queryByTestId("loader-icon")).not.toBeInTheDocument();
      expect(screen.getByText("Apple iPhone")).toBeInTheDocument();
    });
  });

  it("shows no results message when search returns empty", async () => {
    const user = userEvent.setup();
    mockSearch.mockResolvedValueOnce([]);

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        noResultsMessage="No products found"
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "xyz");

    await waitFor(() => {
      expect(screen.getByText("No products found")).toBeInTheDocument();
    });
  });

  it("shows error message when search fails", async () => {
    const user = userEvent.setup();
    mockSearch.mockRejectedValueOnce(new Error("API Error"));

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByText("API Error")).toBeInTheDocument();
    });
  });

  it("calls onSelect when suggestion is clicked", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByText("Apple iPhone")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Apple iPhone"));

    expect(mockOnSelect).toHaveBeenCalledWith({
      id: "1",
      label: "Apple iPhone",
      value: "Apple iPhone",
      description: "Latest smartphone",
    });
  });

  it("highlights matching text in suggestions", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      const highlightedText = screen.getByText("Apple", { selector: "mark" });
      expect(highlightedText).toBeInTheDocument();
      expect(highlightedText).toHaveClass("bg-yellow-200");
    });
  });

  it("supports keyboard navigation with arrow keys", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    // Arrow down to select first item
    await user.keyboard("{ArrowDown}");

    const firstItem = screen.getByText("Apple iPhone").closest("li");
    expect(firstItem).toHaveClass("bg-accent");

    // Arrow down again
    await user.keyboard("{ArrowDown}");

    const secondItem = screen.getByText("Apple MacBook").closest("li");
    expect(secondItem).toHaveClass("bg-accent");

    // Arrow up to go back
    await user.keyboard("{ArrowUp}");

    expect(firstItem).toHaveClass("bg-accent");
  });

  it("selects item with Enter key", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    // Arrow down to select first item
    await user.keyboard("{ArrowDown}");

    // Press Enter to select
    await user.keyboard("{Enter}");

    expect(mockOnSelect).toHaveBeenCalledWith({
      id: "1",
      label: "Apple iPhone",
      value: "Apple iPhone",
      description: "Latest smartphone",
    });
  });

  it("closes dropdown with Escape key", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByRole("list")).not.toBeInTheDocument();
    });
  });

  it("closes dropdown when input loses focus", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete onSearch={mockSearch} onSelect={mockOnSelect} />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    await user.tab(); // Move focus away from input

    await waitFor(
      () => {
        expect(screen.queryByRole("list")).not.toBeInTheDocument();
      },
      { timeout: 200 },
    ); // Account for the 150ms delay
  });

  it("limits number of suggestions", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        maxSuggestions={2}
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument();
      // Should only show 2 suggestions even though mock returns 3
      expect(screen.getAllByRole("listitem")).toHaveLength(2);
    });
  });

  it("respects debounce delay", async () => {
    const user = userEvent.setup();

    render(
      <SearchAutocomplete
        onSearch={mockSearch}
        onSelect={mockOnSelect}
        debounceDelay={200}
      />,
    );

    const input = screen.getByPlaceholderText("Search...");
    await user.type(input, "Apple");

    // Should not call search immediately
    expect(mockSearch).not.toHaveBeenCalled();

    // Should call search after debounce delay
    await waitFor(
      () => {
        expect(mockSearch).toHaveBeenCalledWith("Apple");
      },
      { timeout: 250 },
    );
  });
});
