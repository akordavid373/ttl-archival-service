# Search Autocomplete Component

A comprehensive search autocomplete component with debounced API calls, keyboard navigation, and intelligent text highlighting.

## Features

### ✅ Core Functionality
- **Debounced API calls** - Configurable delay to prevent excessive API requests
- **Keyboard navigation** - Full arrow key, Enter, and Escape support
- **Text highlighting** - Matched text is highlighted in suggestions
- **Loading states** - Visual feedback during API calls
- **No results handling** - Graceful handling when no suggestions are found

### ✅ Advanced Features
- **Configurable parameters** - Minimum query length, max suggestions, debounce delay
- **Error handling** - Graceful error display with user-friendly messages
- **Accessibility** - Proper ARIA support and keyboard navigation
- **TypeScript support** - Full type safety and IntelliSense support
- **Customizable styling** - Built with Tailwind CSS and theme-aware

## Installation

The component is already integrated into the UI library. Simply import and use:

```tsx
import { SearchAutocomplete, type SearchSuggestion } from '@/components/ui'
```

## Usage

### Basic Usage

```tsx
const searchProducts = async (query: string): Promise<SearchSuggestion[]> => {
  const response = await fetch(`/api/search?q=${query}`)
  return response.json()
}

<SearchAutocomplete
  onSearch={searchProducts}
  onSelect={(suggestion) => console.log('Selected:', suggestion)}
  placeholder="Search products..."
/>
```

### Advanced Configuration

```tsx
<SearchAutocomplete
  onSearch={searchProducts}
  onSelect={handleSelection}
  placeholder="Search (min 3 chars)..."
  debounceDelay={500}
  minQueryLength={3}
  maxSuggestions={8}
  noResultsMessage="No products found"
  loadingMessage="Searching..."
  showSearchIcon={true}
  disabled={false}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onSearch` | `(query: string) => Promise<SearchSuggestion[]>` | **Required** | Function to fetch search suggestions |
| `onSelect` | `(suggestion: SearchSuggestion) => void` | **Required** | Callback when a suggestion is selected |
| `placeholder` | `string` | `"Search..."` | Input placeholder text |
| `debounceDelay` | `number` | `300` | Delay in ms before making API calls |
| `minQueryLength` | `number` | `2` | Minimum characters to trigger search |
| `maxSuggestions` | `number` | `10` | Maximum number of suggestions to display |
| `noResultsMessage` | `string` | `"No results found"` | Message when no suggestions are found |
| `loadingMessage` | `string` | `"Searching..."` | Message during API calls |
| `showSearchIcon` | `boolean` | `true` | Show/hide search icon |
| `disabled` | `boolean` | `false` | Disable the input component |
| `className` | `string` | - | Additional CSS classes for wrapper |
| `inputClassName` | `string` | - | Additional CSS classes for input |

## Types

```tsx
interface SearchSuggestion {
  id: string
  label: string
  value: string
  description?: string
}
```

## Keyboard Navigation

- **↑/↓ Arrow Keys** - Navigate through suggestions
- **Enter** - Select highlighted suggestion
- **Escape** - Close suggestions dropdown
- **Tab** - Move focus away (closes dropdown)

## Styling

The component uses Tailwind CSS with theme-aware classes. Key styling features:

- **Highlighted text** - Yellow background with dark text
- **Loading state** - Animated spinner icon
- **Hover states** - Subtle background changes
- **Focus states** - Ring outline for accessibility
- **Error states** - Destructive color scheme

## Testing

Comprehensive test suite included covering:

- ✅ Component rendering
- ✅ Search functionality
- ✅ Keyboard navigation
- ✅ Loading states
- ✅ Error handling
- ✅ Text highlighting
- ✅ Debounce behavior
- ✅ Edge cases

Run tests:
```bash
npm test search-autocomplete
```

## Storybook

Interactive stories available in Storybook:

- **Default** - Basic configuration
- **Custom delay** - Different debounce timing
- **Min query length** - Character threshold
- **Max suggestions** - Result limiting
- **No results** - Empty state handling
- **Error state** - API error handling
- **With descriptions** - Rich suggestion content

View stories:
```bash
npm run storybook
```

## Demo Page

A comprehensive demo page is available at `/pages/SearchAutocompleteDemo.tsx` showcasing:

- Multiple search configurations
- Different data types (products, users, documentation)
- Real-time selection tracking
- Keyboard navigation guide
- Configuration badges

## Performance Considerations

- **Debouncing** prevents excessive API calls
- **Result limiting** controls DOM complexity
- **Efficient scrolling** for large suggestion lists
- **Memoized callbacks** prevent unnecessary re-renders
- **Cleanup functions** prevent memory leaks

## Accessibility

- **ARIA attributes** for screen readers
- **Keyboard navigation** for motor impairments
- **Focus management** for logical tab order
- **Color contrast** meets WCAG standards
- **Semantic HTML** for better structure

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Contributing

When modifying the component:

1. Update types if adding new props
2. Add corresponding tests
3. Update Storybook stories
4. Document breaking changes
5. Test keyboard navigation
6. Verify accessibility compliance
