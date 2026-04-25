import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { Input } from './input'
import { Search, User, Mail } from 'lucide-react'

const meta: Meta<typeof Input> = {
  title: 'UI/Input',
  component: Input,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A flexible input component with variants, sizes, and built-in validation states.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'error', 'success'],
      description: 'Input variant style',
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'default', 'lg'],
      description: 'Input size',
    },
    type: {
      control: { type: 'select' },
      options: ['text', 'email', 'password', 'number', 'search'],
      description: 'Input type',
    },
    placeholder: {
      control: { type: 'text' },
      description: 'Placeholder text',
    },
    disabled: {
      control: { type: 'boolean' },
      description: 'Disable the input',
    },
    required: {
      control: { type: 'boolean' },
      description: 'Mark input as required',
    },
    label: {
      control: { type: 'text' },
      description: 'Input label',
    },
    description: {
      control: { type: 'text' },
      description: 'Helper text description',
    },
    error: {
      control: { type: 'text' },
      description: 'Error message',
    },
    success: {
      control: { type: 'text' },
      description: 'Success message',
    },
  },
  args: { onChange: fn() },
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    placeholder: 'Enter text...',
  },
}

export const WithLabel: Story = {
  args: {
    label: 'Username',
    placeholder: 'Enter your username',
  },
}

export const WithDescription: Story = {
  args: {
    label: 'Email',
    type: 'email',
    placeholder: 'Enter your email',
    description: 'We\'ll never share your email with anyone else.',
  },
}

export const Error: Story = {
  args: {
    label: 'Password',
    type: 'password',
    placeholder: 'Enter your password',
    error: 'Password must be at least 8 characters',
  },
}

export const Success: Story = {
  args: {
    label: 'Username',
    placeholder: 'Enter your username',
    success: 'Username is available',
  },
}

export const Disabled: Story = {
  args: {
    label: 'Disabled Input',
    placeholder: 'This input is disabled',
    disabled: true,
  },
}

export const Small: Story = {
  args: {
    size: 'sm',
    placeholder: 'Small input',
  },
}

export const Large: Story = {
  args: {
    size: 'lg',
    placeholder: 'Large input',
  },
}

export const WithLeftIcon: Story = {
  args: {
    label: 'Search',
    type: 'search',
    placeholder: 'Search...',
    leftIcon: <Search className="h-4 w-4" />,
  },
}

export const WithRightIcon: Story = {
  args: {
    label: 'Email',
    type: 'email',
    placeholder: 'Enter your email',
    rightIcon: <Mail className="h-4 w-4" />,
  },
}

export const WithBothIcons: Story = {
  args: {
    label: 'User',
    placeholder: 'Enter username',
    leftIcon: <User className="h-4 w-4" />,
    rightIcon: <Search className="h-4 w-4" />,
  },
}

export const NumberInput: Story = {
  args: {
    label: 'Age',
    type: 'number',
    placeholder: 'Enter your age',
    min: '0',
    max: '120',
  },
}

export const Required: Story = {
  args: {
    label: 'Required Field',
    placeholder: 'This field is required',
    required: true,
  },
}
