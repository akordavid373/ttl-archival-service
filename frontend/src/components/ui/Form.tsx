import React, { useState, useCallback, useRef, useEffect } from 'react'
import { Eye, EyeOff, AlertCircle, Check } from 'lucide-react'
import { cn } from '../../utils/cn'

export interface ValidationRule {
  validate: (value: string) => boolean | string
  message: string
}

export interface FieldConfig {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'phone' | 'textarea'
  placeholder?: string
  required?: boolean
  validationRules?: ValidationRule[]
  autoComplete?: string
  className?: string
}

export interface FormData {
  [key: string]: string
}

export interface FormErrors {
  [key: string]: string
}

export interface FormTouched {
  [key: string]: boolean
}

// Predefined validation rules
export const ValidationRules = {
  required: (message?: string): ValidationRule => ({
    validate: (value) => value.trim().length > 0 || message || 'This field is required',
    message: message || 'This field is required'
  }),

  email: (message?: string): ValidationRule => ({
    validate: (value) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value) || message || 'Please enter a valid email address'
    },
    message: message || 'Please enter a valid email address'
  }),

  phone: (message?: string): ValidationRule => ({
    validate: (value) => {
      const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/
      return phoneRegex.test(value) || message || 'Please enter a valid phone number'
    },
    message: message || 'Please enter a valid phone number'
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    validate: (value) => value.length >= min || message || `Must be at least ${min} characters`,
    message: message || `Must be at least ${min} characters`
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    validate: (value) => value.length <= max || message || `Must be no more than ${max} characters`,
    message: message || `Must be no more than ${max} characters`
  }),

  password: (message?: string): ValidationRule => ({
    validate: (value) => {
      // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
      return passwordRegex.test(value) || message || 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
    },
    message: message || 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
  }),

  pattern: (regex: RegExp, message?: string): ValidationRule => ({
    validate: (value) => regex.test(value) || message || 'Please enter a valid format',
    message: message || 'Please enter a valid format'
  })
}

export interface FormProps {
  fields: FieldConfig[]
  onSubmit: (data: FormData) => void | Promise<void>
  submitText?: string
  className?: string
  initialData?: FormData
  onChange?: (data: FormData, errors: FormErrors) => void
  disabled?: boolean
}

export function Form({
  fields,
  onSubmit,
  submitText = 'Submit',
  className,
  initialData = {},
  onChange,
  disabled = false
}: FormProps) {
  const [formData, setFormData] = useState<FormData>(initialData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState<FormTouched>({})
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [announceMessage, setAnnounceMessage] = useState('')
  const liveRegionRef = useRef<HTMLDivElement>(null)

  // Initialize form data with empty values
  useEffect(() => {
    const initialFormData: FormData = {}
    fields.forEach(field => {
      initialFormData[field.name] = initialData[field.name] || ''
    })
    setFormData(initialFormData)
  }, [fields, initialData])

  // Announce errors for screen readers
  const announceToScreenReader = useCallback((message: string) => {
    setAnnounceMessage(message)
    if (liveRegionRef.current) {
      liveRegionRef.current.textContent = message
    }
  }, [])

  // Validate a single field
  const validateField = useCallback((field: FieldConfig, value: string): string | null => {
    if (!field.validationRules) return null

    for (const rule of field.validationRules) {
      const result = rule.validate(value)
      if (result !== true) {
        return typeof result === 'string' ? result : rule.message
      }
    }

    return null
  }, [])

  // Validate all fields
  const validateForm = useCallback((data: FormData): FormErrors => {
    const newErrors: FormErrors = {}

    fields.forEach(field => {
      const error = validateField(field, data[field.name] || '')
      if (error) {
        newErrors[field.name] = error
      }
    })

    return newErrors
  }, [fields, validateField])

  // Handle field change
  const handleFieldChange = useCallback((fieldName: string, value: string) => {
    const newFormData = { ...formData, [fieldName]: value }
    setFormData(newFormData)

    // Validate field if it has been touched
    if (touched[fieldName]) {
      const field = fields.find(f => f.name === fieldName)
      if (field) {
        const error = validateField(field, value)
        setErrors(prev => ({
          ...prev,
          [fieldName]: error || ''
        }))
      }
    }

    onChange?.(newFormData, errors)
  }, [formData, touched, fields, validateField, errors, onChange])

  // Handle field blur
  const handleFieldBlur = useCallback((fieldName: string) => {
    setTouched(prev => ({ ...prev, [fieldName]: true }))
    
    const field = fields.find(f => f.name === fieldName)
    if (field) {
      const error = validateField(field, formData[fieldName] || '')
      setErrors(prev => ({
        ...prev,
        [fieldName]: error || ''
      }))

      // Announce error for screen readers
      if (error) {
        announceToScreenReader(`${field.label}: ${error}`)
      }
    }
  }, [fields, formData, validateField, announceToScreenReader])

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Mark all fields as touched
    const allTouched: FormTouched = {}
    fields.forEach(field => {
      allTouched[field.name] = true
    })
    setTouched(allTouched)

    // Validate all fields
    const newErrors = validateForm(formData)
    setErrors(newErrors)

    // Check if there are any errors
    const hasErrors = Object.values(newErrors).some(error => error)
    
    if (hasErrors) {
      // Find first error field and announce it
      const firstErrorField = fields.find(field => newErrors[field.name])
      if (firstErrorField) {
        announceToScreenReader(`Form validation failed. ${firstErrorField.label}: ${newErrors[firstErrorField.name]}`)
      }
      return
    }

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
      announceToScreenReader('Form submitted successfully')
    } catch (error) {
      announceToScreenReader('Form submission failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }, [fields, formData, validateForm, onSubmit, announceToScreenReader])

  // Toggle password visibility
  const togglePasswordVisibility = useCallback((fieldName: string) => {
    setShowPasswords(prev => ({ ...prev, [fieldName]: !prev[fieldName] }))
  }, [])

  // Get field input type
  const getInputType = useCallback((field: FieldConfig) => {
    if (field.type === 'password' && showPasswords[field.name]) {
      return 'text'
    }
    return field.type
  }, [showPasswords])

  return (
    <form onSubmit={handleSubmit} className={cn('space-y-6', className)}>
      {/* Screen reader live region */}
      <div
        ref={liveRegionRef}
        className="sr-only"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      />

      {fields.map(field => (
        <div key={field.name} className="space-y-2">
          <label 
            htmlFor={field.name}
            className={cn(
              'block text-sm font-medium text-gray-700',
              errors[field.name] && touched[field.name] && 'text-red-600'
            )}
          >
            {field.label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>

          <div className="relative">
            {field.type === 'textarea' ? (
              <textarea
                id={field.name}
                value={formData[field.name] || ''}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                onBlur={() => handleFieldBlur(field.name)}
                placeholder={field.placeholder}
                required={field.required}
                disabled={disabled}
                autoComplete={field.autoComplete}
                className={cn(
                  'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  errors[field.name] && touched[field.name]
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-300',
                  disabled && 'opacity-50 cursor-not-allowed',
                  field.className
                )}
                rows={3}
              />
            ) : (
              <input
                id={field.name}
                type={getInputType(field)}
                value={formData[field.name] || ''}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                onBlur={() => handleFieldBlur(field.name)}
                placeholder={field.placeholder}
                required={field.required}
                disabled={disabled}
                autoComplete={field.autoComplete}
                className={cn(
                  'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  errors[field.name] && touched[field.name]
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-300',
                  disabled && 'opacity-50 cursor-not-allowed',
                  field.type === 'password' && 'pr-10',
                  field.className
                )}
              />
            )}

            {/* Password visibility toggle */}
            {field.type === 'password' && (
              <button
                type="button"
                onClick={() => togglePasswordVisibility(field.name)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
                aria-label={showPasswords[field.name] ? 'Hide password' : 'Show password'}
              >
                {showPasswords[field.name] ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            )}

            {/* Field validation icon */}
            {touched[field.name] && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                {errors[field.name] ? (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                ) : (
                  <Check className="h-4 w-4 text-green-500" />
                )}
              </div>
            )}
          </div>

          {/* Error message */}
          {errors[field.name] && touched[field.name] && (
            <div 
              className="flex items-center gap-1 text-sm text-red-600"
              role="alert"
              aria-live="polite"
            >
              <AlertCircle className="h-4 w-4" />
              <span>{errors[field.name]}</span>
            </div>
          )}
        </div>
      ))}

      {/* Submit button */}
      <button
        type="submit"
        disabled={disabled || isSubmitting}
        className={cn(
          'w-full py-2 px-4 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
          disabled || isSubmitting
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
        )}
      >
        {isSubmitting ? 'Submitting...' : submitText}
      </button>
    </form>
  )
}

// Form field component for individual field usage
export interface FormFieldProps {
  field: FieldConfig
  value: string
  onChange: (value: string) => void
  onBlur?: () => void
  error?: string
  touched?: boolean
  disabled?: boolean
  showPasswordToggle?: boolean
  showPassword?: boolean
  onTogglePassword?: () => void
}

export function FormField({
  field,
  value,
  onChange,
  onBlur,
  error,
  touched,
  disabled,
  showPasswordToggle,
  showPassword,
  onTogglePassword
}: FormFieldProps) {
  const getInputType = () => {
    if (field.type === 'password' && showPassword) {
      return 'text'
    }
    return field.type
  }

  return (
    <div className="space-y-2">
      <label 
        htmlFor={field.name}
        className={cn(
          'block text-sm font-medium text-gray-700',
          error && touched && 'text-red-600'
        )}
      >
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        {field.type === 'textarea' ? (
          <textarea
            id={field.name}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            placeholder={field.placeholder}
            required={field.required}
            disabled={disabled}
            autoComplete={field.autoComplete}
            className={cn(
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              error && touched
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-300',
              disabled && 'opacity-50 cursor-not-allowed',
              field.className
            )}
            rows={3}
          />
        ) : (
          <input
            id={field.name}
            type={getInputType()}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            placeholder={field.placeholder}
            required={field.required}
            disabled={disabled}
            autoComplete={field.autoComplete}
            className={cn(
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              error && touched
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-300',
              disabled && 'opacity-50 cursor-not-allowed',
              field.type === 'password' && 'pr-10',
              field.className
            )}
          />
        )}

        {/* Password visibility toggle */}
        {field.type === 'password' && showPasswordToggle && (
          <button
            type="button"
            onClick={onTogglePassword}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        )}

        {/* Field validation icon */}
        {touched && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            {error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <Check className="h-4 w-4 text-green-500" />
            )}
          </div>
        )}
      </div>

      {/* Error message */}
      {error && touched && (
        <div 
          className="flex items-center gap-1 text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
