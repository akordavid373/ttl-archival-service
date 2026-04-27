import { useState, useEffect, useCallback, useRef } from 'react'

interface UseInfiniteScrollOptions {
  hasNextPage: boolean
  fetchNextPage: () => Promise<void>
  threshold?: number
  enabled?: boolean
}

interface UseInfiniteScrollReturn {
  isFetchingNextPage: boolean
  error: Error | null
  retry: () => void
  scrollContainerRef: React.RefObject<HTMLDivElement>
  resetScroll: () => void
}

export function useInfiniteScroll({
  hasNextPage,
  fetchNextPage,
  threshold = 200,
  enabled = true
}: UseInfiniteScrollOptions): UseInfiniteScrollReturn {
  const [isFetchingNextPage, setIsFetchingNextPage] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const retryTimeoutRef = useRef<number>()

  const loadMore = useCallback(async () => {
    if (!hasNextPage || isFetchingNextPage || !enabled) return

    setIsFetchingNextPage(true)
    setError(null)

    try {
      await fetchNextPage()
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to load more data')
      setError(error)
      console.error('Infinite scroll error:', error)
    } finally {
      setIsFetchingNextPage(false)
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage, enabled])

  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current || !enabled) return

    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current
    
    // Check if we've reached the threshold
    if (scrollHeight - scrollTop - clientHeight <= threshold) {
      loadMore()
    }
  }, [loadMore, threshold, enabled])

  const retry = useCallback(() => {
    if (error) {
      setError(null)
      loadMore()
    }
  }, [error, loadMore])

  const resetScroll = useCallback(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = 0
    }
    setError(null)
    setIsFetchingNextPage(false)
  }, [])

  // Restore scroll position from session storage
  useEffect(() => {
    if (!scrollContainerRef.current) return

    const savedScrollPosition = sessionStorage.getItem('archive-scroll-position')
    if (savedScrollPosition) {
      const position = parseInt(savedScrollPosition, 10)
      scrollContainerRef.current.scrollTop = position
    }
  }, [])

  // Save scroll position to session storage
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    const handleScrollSave = () => {
      sessionStorage.setItem('archive-scroll-position', container.scrollTop.toString())
    }

    container.addEventListener('scroll', handleScrollSave, { passive: true })
    
    return () => {
      container.removeEventListener('scroll', handleScrollSave)
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  // Add scroll event listener
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container || !enabled) return

    container.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      container.removeEventListener('scroll', handleScroll)
    }
  }, [handleScroll, enabled])

  return {
    isFetchingNextPage,
    error,
    retry,
    scrollContainerRef,
    resetScroll
  }
}
