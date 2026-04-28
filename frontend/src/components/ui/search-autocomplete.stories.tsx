import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { SearchAutocomplete, type SearchSuggestion } from './search-autocomplete'

const meta: Meta<typeof SearchAutocomplete> = {
  title: 'UI/SearchAutocomplete',
  component: SearchAutocomplete,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    onSearch: { action: 'search' },
    onSelect: { action: 'select' },
    debounceDelay: { control: { type: 'number', min: 0, max: 1000, step: 50 } },
    minQueryLength: { control: { type: 'number', min: 1, max: 5 } },
    maxSuggestions: { control: { type: 'number', min: 1, max: 20 } },
  },
}

export default meta
type Story = StoryObj<typeof meta>

// Mock search function
const mockSearch = async (query: string): Promise<SearchSuggestion[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  if (query.length < 2) return []
  
  const mockSuggestions: SearchSuggestion[] = [
    { id: '1', label: 'Apple iPhone 15', value: 'Apple iPhone 15', description: 'Latest iPhone model' },
    { id: '2', label: 'Apple MacBook Pro', value: 'Apple MacBook Pro', description: 'Professional laptop' },
    { id: '3', label: 'Apple iPad Air', value: 'Apple iPad Air', description: 'Tablet computer' },
    { id: '4', label: 'Apple Watch Series 9', value: 'Apple Watch Series 9', description: 'Smartwatch' },
    { id: '5', label: 'Apple AirPods Pro', value: 'Apple AirPods Pro', description: 'Wireless earbuds' },
  ]
  
  return mockSuggestions.filter(suggestion => 
    suggestion.label.toLowerCase().includes(query.toLowerCase()) ||
    suggestion.description?.toLowerCase().includes(query.toLowerCase())
  )
}

export const Default: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Search for products...',
  },
}

export const WithCustomDelay: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Search (500ms delay)...',
    debounceDelay: 500,
  },
}

export const WithMinQueryLength: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Type at least 3 characters...',
    minQueryLength: 3,
  },
}

export const WithMaxSuggestions: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Search (max 3 results)...',
    maxSuggestions: 3,
  },
}

export const WithoutSearchIcon: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Search...',
    showSearchIcon: false,
  },
}

export const Disabled: Story = {
  args: {
    onSearch: mockSearch,
    onSelect: fn(),
    placeholder: 'Search disabled...',
    disabled: true,
  },
}

// Mock search function that returns no results
const mockNoResults = async (query: string): Promise<SearchSuggestion[]> => {
  await new Promise(resolve => setTimeout(resolve, 300))
  return []
}

export const NoResults: Story = {
  args: {
    onSearch: mockNoResults,
    onSelect: fn(),
    placeholder: 'Search (no results)...',
    noResultsMessage: 'No products found',
  },
}

// Mock search function that throws an error
const mockError = async (query: string): Promise<SearchSuggestion[]> => {
  await new Promise(resolve => setTimeout(resolve, 300))
  throw new Error('Search API failed')
}

export const WithError: Story = {
  args: {
    onSearch: mockError,
    onSelect: fn(),
    placeholder: 'Search (with error)...',
  },
}

// Mock search function with descriptions
const mockWithDescriptions = async (query: string): Promise<SearchSuggestion[]> => {
  await new Promise(resolve => setTimeout(resolve, 400))
  
  if (query.length < 2) return []
  
  const mockSuggestions: SearchSuggestion[] = [
    { id: '1', label: 'React Documentation', value: 'React Documentation', description: 'Official React docs and tutorials' },
    { id: '2', label: 'React Hooks', value: 'React Hooks', description: 'Learn about useState, useEffect, and more' },
    { id: '3', label: 'React Router', value: 'React Router', description: 'Routing library for React applications' },
    { id: '4', label: 'Redux Toolkit', value: 'Redux Toolkit', description: 'State management solution' },
    { id: '5', label: 'React Testing Library', value: 'React Testing Library', description: 'Testing utilities for React' },
  ]
  
  return mockSuggestions.filter(suggestion => 
    suggestion.label.toLowerCase().includes(query.toLowerCase()) ||
    suggestion.description?.toLowerCase().includes(query.toLowerCase())
  )
}

export const WithDescriptions: Story = {
  args: {
    onSearch: mockWithDescriptions,
    onSelect: fn(),
    placeholder: 'Search React resources...',
  },
}
