# Design System Documentation

## Overview

The TTL Archival Service Design System is a comprehensive collection of reusable components, design tokens, and guidelines that ensure consistency across the application. This system is built with accessibility, performance, and developer experience in mind.

## Table of Contents

- [Design Tokens](#design-tokens)
- [Color Palette](#color-palette)
- [Typography](#typography)
- [Spacing](#spacing)
- [Components](#components)
- [Usage Guidelines](#usage-guidelines)
- [Accessibility](#accessibility)
- [Contributing](#contributing)

## Design Tokens

Design tokens are the smallest building blocks of our design system. They are stored in `src/utils/tokens.ts` and include:

### Colors

Our color system is based on HSL values for consistent theming and includes:

- **Primary Colors**: Main brand colors for primary actions
- **Secondary Colors**: Supporting colors for secondary actions
- **Accent Colors**: Highlight colors for emphasis
- **Semantic Colors**: Success, warning, error states
- **Neutral Colors**: Grayscale for text and backgrounds

```typescript
// Example usage
const primaryColor = colors.primary[500] // #3b82f6
const successColor = colors.success[500] // #22c55e
```

### Typography

Typography tokens ensure consistent text styling:

```typescript
// Font families
typography.fontFamily.sans // ['Inter', 'system-ui', 'sans-serif']
typography.fontFamily.mono // ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace']

// Font sizes
typography.fontSize.base // ['1rem', { lineHeight: '1.5rem' }]
typography.fontSize.lg // ['1.125rem', { lineHeight: '1.75rem' }]
```

### Spacing

Consistent spacing scale based on rem units:

```typescript
spacing[4] // '1rem' (16px)
spacing[8] // '2rem' (32px)
spacing[16] // '4rem' (64px)
```

### Border Radius

Consistent border radius values:

```typescript
borderRadius.md // '0.375rem' (6px)
borderRadius.lg // '0.5rem' (8px)
borderRadius.xl // '0.75rem' (12px)
```

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary 50 | #eff6ff | Light backgrounds |
| Primary 500 | #3b82f6 | Primary buttons, links |
| Primary 900 | #1e3a8a | Dark mode primary |

### Semantic Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Success 500 | #22c55e | Success states, confirmations |
| Warning 500 | #f59e0b | Warning states, cautions |
| Error 500 | #ef4444 | Error states, deletions |

## Typography

### Font Hierarchy

1. **Heading 1**: 3rem (48px) - Page titles
2. **Heading 2**: 2.25rem (36px) - Section titles
3. **Heading 3**: 1.875rem (30px) - Subsection titles
4. **Body**: 1rem (16px) - Body text
5. **Small**: 0.875rem (14px) - Supporting text

### Font Weights

- **Light**: 300 - Large headings
- **Normal**: 400 - Body text
- **Medium**: 500 - Emphasis
- **Semibold**: 600 - Subheadings
- **Bold**: 700 - Strong emphasis

## Components

### Button

The Button component is versatile with multiple variants and sizes.

```typescript
import { Button } from '@/components/ui/button'

// Variants
<Button variant="default">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Destructive</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
```

### Card

Flexible card component for content grouping.

```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here.</p>
  </CardContent>
</Card>
```

### Input

Enhanced input component with validation states and icons.

```typescript
import { Input } from '@/components/ui/input'

<Input 
  label="Email"
  type="email"
  placeholder="Enter your email"
  error="Invalid email format"
/>
```

### Badge

Small status indicators and labels.

```typescript
import { Badge } from '@/components/ui/badge'

<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="destructive">Error</Badge>
```

## Usage Guidelines

### Component Usage

1. **Consistency**: Use components as designed without custom styling when possible
2. **Accessibility**: Ensure all interactive elements are keyboard accessible
3. **Responsive**: Design for mobile-first approach
4. **Performance**: Use lazy loading for heavy components

### Color Usage

- **Primary**: Use for main actions and brand elements
- **Secondary**: Use for secondary actions and less important elements
- **Success**: Use for positive feedback and confirmations
- **Warning**: Use for cautionary messages
- **Error**: Use for errors and destructive actions

### Spacing Guidelines

- Use the spacing scale consistently
- Maintain 8px base grid
- Use semantic spacing (margin/padding) based on content hierarchy

## Accessibility

### WCAG Compliance

All components are designed to meet WCAG 2.1 AA standards:

- **Color Contrast**: All text meets 4.5:1 contrast ratio
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Focus Management**: Clear focus indicators and logical tab order

### Testing

- Automated accessibility testing with Storybook a11y addon
- Manual keyboard navigation testing
- Screen reader testing with NVDA/JAWS

### Guidelines

1. **Alt Text**: All images must have descriptive alt text
2. **Labels**: All form inputs must have associated labels
3. **Headings**: Use proper heading hierarchy (h1-h6)
4. **Links**: Link text should be descriptive
5. **Buttons**: Use button elements for actions

## Contributing

### Adding New Components

1. Create component in `src/components/ui/`
2. Add proper TypeScript interfaces
3. Include comprehensive props documentation
4. Create Storybook stories
5. Write unit tests
6. Update this documentation

### Component Structure

```typescript
// Component file structure
ComponentName.tsx          // Main component
ComponentName.stories.tsx  // Storybook stories
ComponentName.test.tsx     // Unit tests
```

### Design Token Updates

1. Update `src/utils/tokens.ts`
2. Update Tailwind config if needed
3. Update CSS variables in `src/index.css`
4. Test across all themes

### Storybook Guidelines

1. **Documentation**: Include component descriptions and prop documentation
2. **Stories**: Cover all variants and states
3. **Controls**: Use Storybook controls for interactive testing
4. **Accessibility**: Include a11y addon testing

## Theme System

### CSS Variables

The theme system uses CSS variables defined in `src/index.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  /* ... more variables */
}

.dark {
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 84% 4.9%;
  /* ... dark theme variables */
}
```

### Theme Switching

Themes are switched by adding/removing the `dark` class to the root element:

```typescript
// Enable dark theme
document.documentElement.classList.add('dark')

// Disable dark theme
document.documentElement.classList.remove('dark')
```

## Performance Considerations

### Bundle Size

- Components are tree-shakeable
- Use dynamic imports for heavy components
- Optimize images and assets

### Rendering

- Use React.memo for expensive components
- Implement proper key props for lists
- Avoid unnecessary re-renders

### CSS

- Use CSS-in-JS sparingly
- Leverage Tailwind's purging
- Minimize custom CSS

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+
- **Legacy**: Limited support for IE11 (not recommended)

## Version History

### v1.0.0
- Initial design system implementation
- Core components: Button, Card, Input, Badge, Tabs, Dialog
- Design tokens and theme system
- Storybook integration
- Comprehensive testing setup

## Resources

- [Storybook](http://localhost:6006) - Interactive component documentation
- [Figma Design System](https://figma.com) - Design mockups and prototypes
- [Component Testing](./testing.md) - Testing guidelines and best practices
- [Accessibility Guide](./accessibility.md) - Detailed accessibility requirements
