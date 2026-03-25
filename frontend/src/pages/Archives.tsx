import React, { useState, useEffect, useCallback } from 'react'
import { 
  Archive as ArchiveIcon, 
  Plus,
  RefreshCw,
  X
} from 'lucide-react'
import { FileUpload } from '../components/FileUpload'
import { cn } from '../utils/cn'
import { ArchiveFiltersSidebar } from '../components/Archives/ArchiveFilters'
import { ArchiveBrowser } from '../components/Archives/ArchiveBrowser'
import { ArchiveDetails } from '../components/Archives/ArchiveDetails'
import { DetailedArchiveEntry, ArchiveFilters, ArchiveSort } from '../types/archive'
import { ArchivalPolicy } from '../types/policy'
import { useNotifications } from '../context/NotificationContext'
import axios from 'axios'

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || '/api/v1';

export function Archives() {
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [archives, setArchives] = useState<DetailedArchiveEntry[]>([])
  const [totalRecords, setTotalRecords] = useState(0)
  const [policies, setPolicies] = useState<ArchivalPolicy[]>([])
  
  // Browser State
  const [filters, setFilters] = useState<ArchiveFilters>({})
  const [sort, setSort] = useState<ArchiveSort>({ field: 'created_at', order: 'desc' })
  const [page, setPage] = useState(1)
  const pageSize = 10

  // Details State
  const [selectedArchive, setSelectedArchive] = useState<DetailedArchiveEntry | null>(null)
  const { addNotification } = useNotifications()

  // Fetch Policies for Filters
  const fetchPolicies = useCallback(async () => {
    try {
      const resp = await axios.get(`${API_BASE_URL}/policies`)
      setPolicies(resp.data)
    } catch (err) {
      console.error('Failed to fetch policies:', err)
      if ((import.meta as any).env.DEV) {
        setPolicies([
          { id: '1', name: 'System Logs', status: 'Active' } as any,
          { id: '2', name: 'User Data TTL', status: 'Active' } as any,
          { id: '3', name: 'Marketing Assets', status: 'Inactive' } as any
        ])
      }
    }
  }, [])

  // Fetch Archives with Filters
  const fetchArchives = useCallback(async (isSilent = false) => {
    if (!isSilent) setIsLoading(true)
    else setIsRefreshing(true)
    
    try {
      const params = {
        page,
        limit: pageSize,
        sort_field: sort.field,
        sort_order: sort.order,
        ...filters,
        status: filters.status?.join(',')
      }
      const response = await axios.get(`${API_BASE_URL}/archives`, { params })
      setArchives(response.data.items)
      setTotalRecords(response.data.total)
    } catch (error) {
      console.error('Failed to fetch archives:', error)
      if ((import.meta as any).env.DEV) {
        // Mock data logic
        const mockPolicies = ['System Logs', 'User Data TTL', 'Marketing Assets', 'Security Audits']
        const mockItems: DetailedArchiveEntry[] = Array(pageSize).fill(0).map((_, i) => ({
          id: `ARC-${1000 + i + (page-1)*pageSize}`,
          filename: `dataset_optimized_v${i+1}_${page}.zip`,
          size: 1024 * 1024 * (i + 5),
          size_formatted: `${(i+5).toFixed(1)} MB`,
          created_at: new Date().toLocaleDateString(),
          status: i % 3 === 0 ? 'Verified' : i % 3 === 1 ? 'Archived' : 'Expiring',
          checksum: 'SHA256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
          blockchain_tx_id: i % 2 === 0 ? '0x' + Math.random().toString(16).substr(2, 64) : undefined,
          policy_id: String((i % 3) + 1),
          policy_name: mockPolicies[i % 4],
          storage_location: 'S3 Standard (US-East)',
          original_data_id: `DATA-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
          blockchain_network: 'Stellar',
          metadata: { node: 'Stellar-Validator-01', region: 'us-east-1' }
        }))
        setArchives(mockItems)
        setTotalRecords(1240)
      } else {
        addNotification({
          title: 'Fetch Error',
          message: 'Failed to retrieve archive records from the node.',
          type: 'error',
          timestamp: new Date()
        })
      }
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [page, filters, sort, addNotification])

  useEffect(() => {
    fetchPolicies()
  }, [fetchPolicies])

  useEffect(() => {
    fetchArchives()
  }, [fetchArchives])

  const deleteArchive = async (id: string) => {
    if (!window.confirm('IRREVERSIBLE ACTION: Are you sure you want to permanently prune this archive metadata? Data on Stellar remains immutable.')) return
    
    try {
      await axios.delete(`${API_BASE_URL}/archives/${id}`)
      setArchives((prev: DetailedArchiveEntry[]) => prev.filter((a: DetailedArchiveEntry) => a.id !== id))
      if (selectedArchive?.id === id) setSelectedArchive(null)
      addNotification({ status: 'Metadata Purged', message: `Archive ${id} record has been safely removed.`, type: 'info', timestamp: new Date() } as any)
    } catch (err) {
      console.error('Delete failed:', err)
      if ((import.meta as any).env.DEV) {
        setArchives((prev: DetailedArchiveEntry[]) => prev.filter((a: DetailedArchiveEntry) => a.id !== id))
        if (selectedArchive?.id === id) setSelectedArchive(null)
      } else {
        addNotification({ title: 'System Error', message: 'Failed to prune archive record.', type: 'error', timestamp: new Date() })
      }
    }
  }

  const downloadArchive = (archive: DetailedArchiveEntry) => {
    addNotification({
       title: 'Recovery Initiated', 
       message: `Preparing high-speed recovery for ${archive.filename}. This may take a moment.`, 
       type: 'info', 
       timestamp: new Date() 
    })
    // Mock download
    setTimeout(() => {
      window.alert(`Simulating secure download for ${archive.filename} via high-availability node.`)
    }, 1000)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 relative pb-12">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Archive Record Browser</h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <ArchiveIcon className="h-4 w-4" />
            Auditing global retention nodes and cryptographically anchored storage.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
             onClick={() => fetchArchives(true)}
             disabled={isRefreshing}
             className="p-3 bg-secondary text-secondary-foreground rounded-2xl border border-border shadow-sm hover:bg-accent transition-all group disabled:opacity-50"
          >
            <RefreshCw className={cn("h-5 w-5", isRefreshing && "animate-spin")} />
          </button>
          <button 
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center gap-2 px-6 py-4 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all group"
          >
            <Plus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
            Establish New Archive
          </button>
        </div>
      </header>

      {/* Upload Overlay */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6 bg-background/80 backdrop-blur-xl animate-in fade-in duration-300 overflow-y-auto">
          <div className="bg-card w-full max-w-2xl rounded-[2.5rem] border border-border/50 shadow-2xl overflow-hidden relative animate-in zoom-in-95 duration-300 my-8">
             <div className="p-8 border-b border-border/40 flex items-center justify-between bg-accent/20">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary text-primary-foreground rounded-2xl shadow-lg shadow-primary/20">
                    <ArchiveIcon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold tracking-tight leading-none">Initialize Archival Pack</h3>
                    <p className="text-[10px] text-muted-foreground mt-2 uppercase font-extrabold tracking-widest">Dataset Chain Validation</p>
                  </div>
                </div>
                <button 
                  onClick={() => setIsUploadOpen(false)}
                  className="p-3 hover:bg-card/50 rounded-2xl text-muted-foreground hover:text-foreground transition-all border border-transparent hover:border-border/60"
                >
                  <X className="h-6 w-6" />
                </button>
             </div>
             <div className="p-8">
               <FileUpload onUploadComplete={() => {
                 setTimeout(() => {
                    setIsUploadOpen(false)
                    fetchArchives()
                 }, 1000)
               }} />
             </div>
             <div className="p-8 bg-accent/10 border-t border-border/30 flex justify-end gap-3">
               <button onClick={() => setIsUploadOpen(false)} className="px-6 py-3 text-xs font-bold hover:bg-accent rounded-2xl transition-colors">Discard Draft</button>
               <button className="px-8 py-3 bg-primary text-primary-foreground font-bold text-xs rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.05] transition-all">Proceed to Encrypt & Anchor</button>
             </div>
          </div>
        </div>
      )}

      {/* Main Core UI Split Layout */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        <ArchiveFiltersSidebar 
          filters={filters}
          policies={policies}
          onChange={(newFilters) => {
            setFilters(newFilters)
            setPage(1) // Reset to first page on filter change
          }}
          onClear={() => {
            setFilters({})
            setPage(1)
          }}
        />
        
        <ArchiveBrowser 
          archives={archives}
          total={totalRecords}
          page={page}
          pageSize={pageSize}
          isLoading={isLoading}
          onPageChange={setPage}
          onSortChange={setSort}
          onSearch={(query) => {
            setFilters(prev => ({ ...prev, search: query || undefined }))
            setPage(1)
          }}
          onViewDetails={setSelectedArchive}
          onDownload={downloadArchive}
          onDelete={deleteArchive}
        />
      </div>

      {/* Record Details Panel */}
      {selectedArchive && (
        <>
          <div 
            className="fixed inset-0 z-40 bg-background/40 backdrop-blur-sm animate-in fade-in duration-500" 
            onClick={() => setSelectedArchive(null)} 
          />
          <ArchiveDetails 
            archive={selectedArchive}
            onClose={() => setSelectedArchive(null)}
            onDownload={downloadArchive}
            onDelete={deleteArchive}
          />
        </>
      )}
    </div>
  )
}
