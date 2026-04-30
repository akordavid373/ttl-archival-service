// UI Component Library Exports
// This file provides a single entry point for all UI components

// Core Components
export { Button, buttonVariants } from "./button";
export type { ButtonProps } from "./button";

export {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./card";

export { Input, inputVariants } from "./input";

export { Badge, badgeVariants } from "./badge";

export { Tabs, TabsList, TabsTrigger, TabsContent } from "./tabs";

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from "./dialog";

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from "./select";

export { SearchAutocomplete } from "./search-autocomplete";
export type {
  SearchAutocompleteProps,
  SearchSuggestion,
} from "./search-autocomplete";

// Re-export design tokens
export { default as tokens } from "../../utils/tokens";

// Re-export utility functions
export { cn } from "../../utils/cn";

// Component version
export const COMPONENT_LIBRARY_VERSION = "1.0.0";
