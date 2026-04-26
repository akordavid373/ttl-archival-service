import React, { useState } from 'react'
import { Modal, AlertModal, ConfirmModal, useModal } from '../components/ui/Modal'
import { DataTable, Column } from '../components/ui/DataTable'
import { Form, ValidationRules, FieldConfig } from '../components/ui/Form'

// Sample data for the table
interface SampleData {
  id: number
  name: string
  email: string
  status: 'Active' | 'Inactive' | 'Pending'
  createdAt: string
  role: string
}

const sampleData: SampleData[] = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active', createdAt: '2024-01-15', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Pending', createdAt: '2024-01-16', role: 'User' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Inactive', createdAt: '2024-01-17', role: 'User' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', status: 'Active', createdAt: '2024-01-18', role: 'Moderator' },
  { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', status: 'Active', createdAt: '2024-01-19', role: 'User' },
  { id: 6, name: 'Diana Prince', email: 'diana@example.com', status: 'Pending', createdAt: '2024-01-20', role: 'Admin' },
  { id: 7, name: 'Edward Norton', email: 'edward@example.com', status: 'Active', createdAt: '2024-01-21', role: 'User' },
  { id: 8, name: 'Fiona Green', email: 'fiona@example.com', status: 'Inactive', createdAt: '2024-01-22', role: 'Moderator' },
]

export default function Demo() {
  // Modal states
  const customModal = useModal()
  const alertModal = useModal()
  const confirmModal = useModal()
  const [customModalContent, setCustomModalContent] = useState('')

  // Form state
  const [formSubmitted, setFormSubmitted] = useState(false)
  const [formData, setFormData] = useState({})

  // Table columns
  const tableColumns: Column<SampleData>[] = [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      className: 'font-medium'
    },
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      filterable: true
    },
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      filterable: true
    },
    {
      key: 'role',
      label: 'Role',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => (
        <span className={`px-2 py-1 text-xs rounded-full ${
          value === 'Active' ? 'bg-green-100 text-green-800' :
          value === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'createdAt',
      label: 'Created',
      sortable: true
    }
  ]

  // Form fields
  const formFields: FieldConfig[] = [
    {
      name: 'name',
      label: 'Full Name',
      type: 'text',
      placeholder: 'Enter your full name',
      required: true,
      validationRules: [
        ValidationRules.required(),
        ValidationRules.minLength(2),
        ValidationRules.maxLength(50)
      ]
    },
    {
      name: 'email',
      label: 'Email Address',
      type: 'email',
      placeholder: 'Enter your email',
      required: true,
      validationRules: [
        ValidationRules.required(),
        ValidationRules.email()
      ]
    },
    {
      name: 'phone',
      label: 'Phone Number',
      type: 'phone',
      placeholder: 'Enter your phone number',
      validationRules: [
        ValidationRules.phone()
      ]
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      placeholder: 'Enter a secure password',
      required: true,
      validationRules: [
        ValidationRules.required(),
        ValidationRules.password()
      ]
    },
    {
      name: 'confirmPassword',
      label: 'Confirm Password',
      type: 'password',
      placeholder: 'Confirm your password',
      required: true,
      validationRules: [
        ValidationRules.required(),
        {
          validate: (value) => {
            const password = formData.password || ''
            return value === password || 'Passwords do not match'
          },
          message: 'Passwords do not match'
        }
      ]
    },
    {
      name: 'message',
      label: 'Message',
      type: 'textarea',
      placeholder: 'Enter your message (optional)',
      validationRules: [
        ValidationRules.maxLength(500)
      ]
    }
  ]

  const handleFormSubmit = async (data: any) => {
    setFormData(data)
    setFormSubmitted(true)
    console.log('Form submitted:', data)
  }

  const handleTableRowClick = (row: SampleData) => {
    setCustomModalContent(`You selected: ${row.name} (${row.email})`)
    customModal.open()
  }

  const handleConfirmAction = () => {
    console.log('Confirmed action')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">UI Components Demo</h1>
          <p className="text-gray-600">Demonstration of Modal Dialog System, Data Table, and Form Validation components</p>
        </div>

        {/* Modal Demo Section */}
        <section className="mb-12 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Modal Dialog System</h2>
          <p className="text-gray-600 mb-6">Test different modal types with backdrop click, escape key, and focus trapping.</p>
          
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => {
                setCustomModalContent('This is a custom modal with any content you want to display!')
                customModal.open()
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Open Custom Modal
            </button>
            
            <button
              onClick={() => alertModal.open()}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Open Alert Modal
            </button>
            
            <button
              onClick={() => confirmModal.open()}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Open Confirm Modal
            </button>
          </div>

          {/* Custom Modal */}
          <Modal
            isOpen={customModal.isOpen}
            onClose={customModal.close}
            title="Custom Modal"
            description="This modal can contain any content"
            size="lg"
          >
            <div className="space-y-4">
              <p className="text-gray-700">{customModalContent}</p>
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h3 className="font-semibold text-blue-800 mb-2">Features:</h3>
                <ul className="list-disc list-inside text-blue-700 space-y-1">
                  <li>Backdrop click to close</li>
                  <li>Escape key to close</li>
                  <li>Focus trapping within modal</li>
                  <li>Smooth animations</li>
                  <li>Multiple size options</li>
                  <li>Accessibility support</li>
                </ul>
              </div>
              <div className="flex justify-end">
                <button
                  onClick={customModal.close}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </Modal>

          {/* Alert Modal */}
          <AlertModal
            isOpen={alertModal.isOpen}
            onClose={alertModal.close}
            title="Success!"
            message="The operation completed successfully."
            onConfirm={() => console.log('Alert confirmed')}
          />

          {/* Confirm Modal */}
          <ConfirmModal
            isOpen={confirmModal.isOpen}
            onClose={confirmModal.close}
            title="Confirm Action"
            message="Are you sure you want to perform this action? This cannot be undone."
            onConfirm={handleConfirmAction}
            variant="destructive"
          />
        </section>

        {/* Data Table Demo Section */}
        <section className="mb-12 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Advanced Data Table</h2>
          <p className="text-gray-600 mb-6">Interactive table with sorting, filtering, pagination, and export functionality.</p>
          
          <DataTable
            data={sampleData}
            columns={tableColumns}
            pageSize={5}
            searchable={true}
            exportable={true}
            onRowClick={handleTableRowClick}
            emptyMessage="No data available"
          />
        </section>

        {/* Form Validation Demo Section */}
        <section className="mb-12 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Enhanced Form Validation</h2>
          <p className="text-gray-600 mb-6">Real-time validation with accessibility features and comprehensive error handling.</p>
          
          {formSubmitted && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <h3 className="font-semibold text-green-800 mb-2">Form Submitted Successfully!</h3>
              <pre className="text-sm text-green-700 whitespace-pre-wrap">
                {JSON.stringify(formData, null, 2)}
              </pre>
              <button
                onClick={() => setFormSubmitted(false)}
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Reset Form
              </button>
            </div>
          )}

          {!formSubmitted && (
            <Form
              fields={formFields}
              onSubmit={handleFormSubmit}
              submitText="Submit Form"
              onChange={(data, errors) => setFormData(data)}
            />
          )}
        </section>

        {/* Features Summary */}
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Implementation Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Modal Dialog System</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>✓ Multiple modal types (alert, confirm, custom)</li>
                <li>✓ Backdrop click to close functionality</li>
                <li>✓ Focus trapping within modal</li>
                <li>✓ Escape key to close modal</li>
                <li>✓ Animation effects for open/close</li>
                <li>✓ Accessibility support</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Advanced Data Table</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>✓ Pagination controls with page size options</li>
                <li>✓ Column sorting functionality</li>
                <li>✓ Search/filter capabilities</li>
                <li>✓ Responsive design for mobile devices</li>
                <li>✓ Export functionality (CSV, PDF)</li>
                <li>✓ Interactive row selection</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Enhanced Form Validation</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>✓ Real-time validation on field blur/change</li>
                <li>✓ Clear error messages with field highlighting</li>
                <li>✓ Accessible error announcements</li>
                <li>✓ Validation rules for email, phone, passwords</li>
                <li>✓ Form submission prevention on errors</li>
                <li>✓ Password visibility toggle</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
