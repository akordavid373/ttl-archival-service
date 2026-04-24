import React from 'react'
import { Printer, Download, Eye } from 'lucide-react'
import { cn } from '../utils/cn'

interface PrintStylesProps {
  children: React.ReactNode
  title?: string
  showHeader?: boolean
  showFooter?: boolean
  landscape?: boolean
  className?: string
}

export function PrintStyles({ 
  children, 
  title = 'TTL Archival Service', 
  showHeader = true, 
  showFooter = true,
  landscape = false,
  className 
}: PrintStylesProps) {
  const handlePrint = () => {
    window.print()
  }

  const handlePrintPreview = () => {
    window.open(window.location.href + '?print=preview', '_blank')
  }

  const handleDownloadPDF = () => {
    // This would typically use a library like jsPDF or puppeteer
    // For now, we'll trigger the print dialog
    window.print()
  }

  return (
    <>
      {/* Print Controls */}
      <div className="print:hidden flex items-center gap-2 mb-6 p-4 bg-accent/30 rounded-xl">
        <button
          onClick={handlePrint}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors text-sm font-medium"
        >
          <Printer className="h-4 w-4" />
          Print
        </button>
        
        <button
          onClick={handlePrintPreview}
          className="flex items-center gap-2 px-4 py-2 bg-accent text-accent-foreground rounded-xl hover:bg-accent/90 transition-colors text-sm font-medium"
        >
          <Eye className="h-4 w-4" />
          Preview
        </button>
        
        <button
          onClick={handleDownloadPDF}
          className="flex items-center gap-2 px-4 py-2 bg-muted text-muted-foreground rounded-xl hover:bg-muted/80 transition-colors text-sm font-medium"
        >
          <Download className="h-4 w-4" />
          Download PDF
        </button>

        <div className="ml-auto flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={landscape}
              onChange={(e) => {
                if (e.target.checked) {
                  document.body.style.setProperty('--print-orientation', 'landscape')
                } else {
                  document.body.style.removeProperty('--print-orientation')
                }
              }}
              className="rounded"
            />
            Landscape
          </label>
        </div>
      </div>

      {/* Printable Content */}
      <div className={cn('print-content', className)}>
        {/* Print Header */}
        {showHeader && (
          <header className="print-header hidden print:block">
            <div className="flex items-center justify-between mb-8 pb-4 border-b-2 border-gray-300">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center border border-primary/20">
                  <div className="w-6 h-6 bg-primary rounded-sm" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{title}</h1>
                  <p className="text-sm text-gray-600">TTL Archival Service</p>
                </div>
              </div>
              <div className="text-right text-sm text-gray-600">
                <div className="font-medium">Generated on</div>
                <div>{new Date().toLocaleDateString()}</div>
                <div>{new Date().toLocaleTimeString()}</div>
              </div>
            </div>
          </header>
        )}

        {/* Main Content */}
        <main className="print-main">
          {children}
        </main>

        {/* Print Footer */}
        {showFooter && (
          <footer className="print-footer hidden print:block mt-12 pt-4 border-t-2 border-gray-300">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <div>
                <p>© 2024 TTL Archival Service. All rights reserved.</p>
                <p>Confidential and Proprietary</p>
              </div>
              <div className="text-right">
                <p>Page <span className="page-number"></span> of <span className="total-pages"></span></p>
                <p>Printed by TTL Archival System</p>
              </div>
            </div>
          </footer>
        )}
      </div>

      {/* Print Styles */}
      <style jsx>{`
        @media print {
          @page {
            size: ${landscape ? 'landscape' : 'portrait'};
            margin: 1cm;
          }

          * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
          }

          body {
            font-size: 12pt;
            line-height: 1.4;
            color: #000;
            background: #fff !important;
          }

          .print-hidden {
            display: none !important;
          }

          .print-header {
            display: block !important;
          }

          .print-footer {
            display: block !important;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
          }

          .print-main {
            margin-bottom: 60px; /* Space for footer */
          }

          /* Page breaks */
          .page-break-before {
            page-break-before: always;
          }

          .page-break-after {
            page-break-after: always;
          }

          .page-break-inside-avoid {
            page-break-inside: avoid;
          }

          /* Tables */
          table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
          }

          th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
          }

          th {
            background-color: #f5f5f5;
            font-weight: bold;
          }

          /* Images */
          img {
            max-width: 100%;
            height: auto;
            page-break-inside: avoid;
          }

          /* Links */
          a {
            color: #000;
            text-decoration: none;
          }

          a[href^="http"]:after {
            content: " (" attr(href) ")";
            font-size: 0.8em;
            color: #666;
          }

          /* Code blocks */
          pre, code {
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            background: #f5f5f5;
            padding: 2px;
          }

          pre {
            border: 1px solid #ddd;
            padding: 1em;
            page-break-inside: avoid;
          }

          /* Lists */
          ul, ol {
            margin-bottom: 1em;
          }

          li {
            margin-bottom: 0.5em;
          }

          /* Blockquotes */
          blockquote {
            border-left: 4px solid #ddd;
            padding-left: 1em;
            margin: 1em 0;
            font-style: italic;
          }

          /* Hide navigation and controls */
          nav, .print-hidden, .no-print {
            display: none !important;
          }

          /* Ensure colors print well */
          .text-primary {
            color: #000 !important;
          }

          .text-muted-foreground {
            color: #666 !important;
          }

          .bg-primary {
            background: #f0f0f0 !important;
          }

          .bg-accent {
            background: #f8f8f8 !important;
          }

          /* Charts and graphs */
          .chart-container {
            page-break-inside: avoid;
            margin: 1em 0;
          }

          /* Cards and panels */
          .card, .panel {
            border: 1px solid #ddd;
            margin-bottom: 1em;
            page-break-inside: avoid;
          }

          /* Responsive adjustments */
          .grid {
            display: block;
          }

          .grid > * {
            margin-bottom: 1em;
          }

          /* Ensure text doesn't overflow */
          .truncate {
            white-space: normal;
            overflow: visible;
          }

          /* Print-specific typography */
          h1 {
            font-size: 18pt;
            margin-bottom: 0.5em;
          }

          h2 {
            font-size: 16pt;
            margin-bottom: 0.5em;
            page-break-after: avoid;
          }

          h3 {
            font-size: 14pt;
            margin-bottom: 0.5em;
            page-break-after: avoid;
          }

          h4, h5, h6 {
            font-size: 12pt;
            margin-bottom: 0.5em;
            page-break-after: avoid;
          }

          p {
            margin-bottom: 0.5em;
            orphans: 3;
            widows: 3;
          }

          /* Special print classes */
          .print-only {
            display: block !important;
          }

          .screen-only {
            display: none !important;
          }
        }

        /* Print preview styles */
        @media screen and (max-width: 800px) {
          .print-content {
            zoom: 0.8;
          }
        }
      `}</style>
    </>
  )
}

// Utility components for print-specific layouts
export function PrintSection({ 
  title, 
  children, 
  pageBreak = false,
  className 
}: {
  title: string
  children: React.ReactNode
  pageBreak?: boolean
  className?: string
}) {
  return (
    <section className={cn(
      'print-section mb-8',
      pageBreak && 'page-break-after',
      className
    )}>
      <h2 className="text-lg font-bold mb-4 pb-2 border-b border-gray-200 print:border-b-2 print:border-gray-300">
        {title}
      </h2>
      <div className="page-break-inside-avoid">
        {children}
      </div>
    </section>
  )
}

export function PrintTable({ 
  data, 
  headers,
  title 
}: {
  data: any[][]
  headers: string[]
  title?: string
}) {
  return (
    <div className="print-table page-break-inside-avoid mb-6">
      {title && <h3 className="font-semibold mb-2">{title}</h3>}
      <table className="w-full border-collapse">
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th key={index} className="border border-gray-300 bg-gray-50 p-2 text-left font-semibold">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="border border-gray-300 p-2">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Hook for print utilities
export function usePrintUtils() {
  const addPageBreak = () => {
    const element = document.createElement('div')
    element.className = 'page-break-before'
    return element
  }

  const generatePrintPreview = (content: string) => {
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>Print Preview</title>
            <style>
              @page { margin: 1cm; }
              body { font-family: Arial, sans-serif; font-size: 12pt; }
              ${document.querySelector('style')?.textContent || ''}
            </style>
          </head>
          <body>
            ${content}
          </body>
        </html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  return { addPageBreak, generatePrintPreview }
}
