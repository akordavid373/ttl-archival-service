import { useState } from "react";
import {
  SearchAutocomplete,
  type SearchSuggestion,
} from "../components/ui/search-autocomplete";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";

const SearchAutocompleteDemo = () => {
  const [selectedItems, setSelectedItems] = useState<SearchSuggestion[]>([]);

  // Mock search function for products
  const searchProducts = async (query: string): Promise<SearchSuggestion[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 300));

    if (query.length < 2) return [];

    const products = [
      {
        id: "1",
        label: "Apple iPhone 15 Pro",
        value: "Apple iPhone 15 Pro",
        description: "Latest iPhone with titanium design",
      },
      {
        id: "2",
        label: "Apple MacBook Pro M3",
        value: "Apple MacBook Pro M3",
        description: "Professional laptop with M3 chip",
      },
      {
        id: "3",
        label: "Apple iPad Air",
        value: "Apple iPad Air",
        description: "Versatile tablet for work and play",
      },
      {
        id: "4",
        label: "Apple Watch Series 9",
        value: "Apple Watch Series 9",
        description: "Advanced health and fitness features",
      },
      {
        id: "5",
        label: "Apple AirPods Pro 2",
        value: "Apple AirPods Pro 2",
        description: "Premium wireless earbuds with ANC",
      },
      {
        id: "6",
        label: "Samsung Galaxy S24 Ultra",
        value: "Samsung Galaxy S24 Ultra",
        description: "Android flagship with S Pen",
      },
      {
        id: "7",
        label: "Samsung Galaxy Tab S9",
        value: "Samsung Galaxy Tab S9",
        description: "High-performance Android tablet",
      },
      {
        id: "8",
        label: "Google Pixel 8 Pro",
        value: "Google Pixel 8 Pro",
        description: "AI-powered smartphone",
      },
      {
        id: "9",
        label: "Dell XPS 15",
        value: "Dell XPS 15",
        description: "Premium Windows laptop",
      },
      {
        id: "10",
        label: "Sony WH-1000XM5",
        value: "Sony WH-1000XM5",
        description: "Industry-leading noise cancellation",
      },
    ];

    return products.filter(
      (product) =>
        product.label.toLowerCase().includes(query.toLowerCase()) ||
        product.description.toLowerCase().includes(query.toLowerCase()),
    );
  };

  // Mock search function for users
  const searchUsers = async (query: string): Promise<SearchSuggestion[]> => {
    await new Promise((resolve) => setTimeout(resolve, 200));

    if (query.length < 2) return [];

    const users = [
      {
        id: "1",
        label: "John Smith",
        value: "john.smith",
        description: "Software Engineer",
      },
      {
        id: "2",
        label: "Sarah Johnson",
        value: "sarah.johnson",
        description: "Product Designer",
      },
      {
        id: "3",
        label: "Mike Chen",
        value: "mike.chen",
        description: "Data Scientist",
      },
      {
        id: "4",
        label: "Emily Davis",
        value: "emily.davis",
        description: "Marketing Manager",
      },
      {
        id: "5",
        label: "Alex Thompson",
        value: "alex.thompson",
        description: "DevOps Engineer",
      },
      {
        id: "6",
        label: "Jessica Wilson",
        value: "jessica.wilson",
        description: "UX Researcher",
      },
      {
        id: "7",
        label: "David Brown",
        value: "david.brown",
        description: "Backend Developer",
      },
      {
        id: "8",
        label: "Lisa Anderson",
        value: "lisa.anderson",
        description: "Project Manager",
      },
    ];

    return users.filter(
      (user) =>
        user.label.toLowerCase().includes(query.toLowerCase()) ||
        user.description.toLowerCase().includes(query.toLowerCase()),
    );
  };

  // Mock search function for documentation
  const searchDocs = async (query: string): Promise<SearchSuggestion[]> => {
    await new Promise((resolve) => setTimeout(resolve, 400));

    if (query.length < 3) return [];

    const docs = [
      {
        id: "1",
        label: "React Documentation",
        value: "react-docs",
        description: "Official React documentation and API reference",
      },
      {
        id: "2",
        label: "TypeScript Handbook",
        value: "typescript-handbook",
        description: "Complete TypeScript guide",
      },
      {
        id: "3",
        label: "Tailwind CSS Docs",
        value: "tailwind-docs",
        description: "Utility-first CSS framework documentation",
      },
      {
        id: "4",
        label: "Node.js Guide",
        value: "nodejs-guide",
        description: "Node.js runtime documentation",
      },
      {
        id: "5",
        label: "Express.js Tutorial",
        value: "express-tutorial",
        description: "Web framework for Node.js",
      },
      {
        id: "6",
        label: "MongoDB Manual",
        value: "mongodb-manual",
        description: "NoSQL database documentation",
      },
      {
        id: "7",
        label: "Docker Guide",
        value: "docker-guide",
        description: "Container platform documentation",
      },
      {
        id: "8",
        label: "AWS Documentation",
        value: "aws-docs",
        description: "Amazon Web Services documentation",
      },
    ];

    return docs.filter(
      (doc) =>
        doc.label.toLowerCase().includes(query.toLowerCase()) ||
        doc.description.toLowerCase().includes(query.toLowerCase()),
    );
  };

  const handleSelect = (suggestion: SearchSuggestion) => {
    setSelectedItems((prev) => [...prev, suggestion]);
  };

  const clearSelections = () => {
    setSelectedItems([]);
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">Search Autocomplete Demo</h1>
          <p className="text-lg text-muted-foreground">
            Interactive demonstration of the SearchAutocomplete component with
            various configurations
          </p>
        </div>

        {/* Product Search Demo */}
        <Card>
          <CardHeader>
            <CardTitle>Product Search</CardTitle>
            <CardDescription>
              Search for products with debounced API calls and keyboard
              navigation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SearchAutocomplete
              onSearch={searchProducts}
              onSelect={handleSelect}
              placeholder="Search for products (min 2 characters)..."
              debounceDelay={300}
              minQueryLength={2}
              maxSuggestions={5}
              noResultsMessage="No products found"
              loadingMessage="Searching products..."
            />
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Debounce: 300ms</Badge>
              <Badge variant="outline">Min query: 2 chars</Badge>
              <Badge variant="outline">Max results: 5</Badge>
            </div>
          </CardContent>
        </Card>

        {/* User Search Demo */}
        <Card>
          <CardHeader>
            <CardTitle>User Search</CardTitle>
            <CardDescription>
              Faster search with shorter debounce and different styling
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SearchAutocomplete
              onSearch={searchUsers}
              onSelect={handleSelect}
              placeholder="Search for users..."
              debounceDelay={150}
              minQueryLength={2}
              maxSuggestions={8}
              noResultsMessage="No users found"
              loadingMessage="Finding users..."
            />
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Debounce: 150ms</Badge>
              <Badge variant="outline">Min query: 2 chars</Badge>
              <Badge variant="outline">Max results: 8</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Documentation Search Demo */}
        <Card>
          <CardHeader>
            <CardTitle>Documentation Search</CardTitle>
            <CardDescription>
              Search with longer minimum query length and descriptions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SearchAutocomplete
              onSearch={searchDocs}
              onSelect={handleSelect}
              placeholder="Search documentation (min 3 characters)..."
              debounceDelay={500}
              minQueryLength={3}
              maxSuggestions={6}
              noResultsMessage="No documentation found"
              loadingMessage="Searching documentation..."
            />
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Debounce: 500ms</Badge>
              <Badge variant="outline">Min query: 3 chars</Badge>
              <Badge variant="outline">Max results: 6</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Selected Items */}
        {selectedItems.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                Selected Items
                <button
                  onClick={clearSelections}
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  Clear All
                </button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {selectedItems.map((item, index) => (
                  <div
                    key={`${item.id}-${index}`}
                    className="flex justify-between items-center p-3 bg-muted rounded-lg"
                  >
                    <div>
                      <div className="font-medium">{item.label}</div>
                      {item.description && (
                        <div className="text-sm text-muted-foreground">
                          {item.description}
                        </div>
                      )}
                    </div>
                    <Badge variant="secondary">{item.value}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Keyboard Navigation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <kbd className="px-2 py-1 bg-muted rounded text-xs">↑</kbd>
                  <span>Navigate up</span>
                </div>
                <div className="flex items-center space-x-2">
                  <kbd className="px-2 py-1 bg-muted rounded text-xs">↓</kbd>
                  <span>Navigate down</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <kbd className="px-2 py-1 bg-muted rounded text-xs">
                    Enter
                  </kbd>
                  <span>Select highlighted item</span>
                </div>
                <div className="flex items-center space-x-2">
                  <kbd className="px-2 py-1 bg-muted rounded text-xs">Esc</kbd>
                  <span>Close dropdown</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SearchAutocompleteDemo;
