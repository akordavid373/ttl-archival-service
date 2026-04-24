import { useEffect, useRef, useState, useCallback, useMemo, useLayoutEffect } from 'react'
import { cn } from '../utils/cn'

interface VirtualScrollItem {
  id: string | number
  height?: number
  content: React.ReactNode
  data?: any
}

interface VirtualScrollProps {
  items: VirtualScrollItem[]
  itemHeight?: number | ((index: number, data?: any) => number)
  containerHeight?: number
  overscan?: number
  className?: string
  onScroll?: (scrollTop: number, visibleRange: { start: number; end: number }) => void
  renderItem?: (item: VirtualScrollItem, index: number, isVisible: boolean) => React.ReactNode
  estimatedItemHeight?: number
  dynamicHeight?: boolean
  scrollToIndex?: number
  scrollToAlignment?: 'start' | 'center' | 'end' | 'auto'
  onItemsRendered?: (visibleRange: { start: number; end: number }) => void
  loading?: boolean
  loadingComponent?: React.ReactNode
  emptyComponent?: React.ReactNode
  showScrollIndicator?: boolean
  horizontal?: boolean
  threshold?: number
  debounceScroll?: number
  ariaLabel?: string
  testId?: string
}

export function VirtualScroll({
  items,
  itemHeight = 50,
  containerHeight = 400,
  overscan = 5,
  className = '',
  onScroll,
  renderItem,
  estimatedItemHeight = 50,
  dynamicHeight = false,
  scrollToIndex,
  scrollToAlignment = 'start',
  onItemsRendered,
  loading = false,
  loadingComponent,
  emptyComponent,
  showScrollIndicator = true,
  horizontal = false,
  threshold = 100,
  debounceScroll = 16,
  ariaLabel = 'Virtual scrollable list',
  testId
}: VirtualScrollProps) {
  const [scrollTop, setScrollTop] = useState(0)
  const [scrollLeft, setScrollLeft] = useState(0)
  const [itemSizes, setItemSizes] = useState<Map<number, number>>(new Map())
  const [isScrolling, setIsScrolling] = useState(false)
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down' | 'left' | 'right' | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const itemsRef = useRef<Map<number, HTMLDivElement>>(new Map())
  const scrollElementRef = useRef<HTMLDivElement>(null)
  const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const lastScrollTopRef = useRef(0)
  const lastScrollLeftRef = useRef(0)
  const resizeObserverRef = useRef<ResizeObserver>()

  // Calculate item height
  const getItemHeight = useCallback((index: number, data?: any): number => {
    if (dynamicHeight && itemSizes.has(index)) {
      return itemSizes.get(index)!
    }
    if (typeof itemHeight === 'function') {
      return itemHeight(index, data)
    }
    return itemHeight as number
  }, [itemHeight, itemSizes, dynamicHeight])

  // Calculate total height/width
  const totalSize = useMemo(() => {
    if (horizontal) {
      if (dynamicHeight && itemSizes.size > 0) {
        let width = 0
        for (let i = 0; i < items.length; i++) {
          width += itemSizes.get(i) || estimatedItemHeight
        }
        return width
      }
      return items.length * getItemHeight(0)
    } else {
      if (dynamicHeight && itemSizes.size > 0) {
        let height = 0
        for (let i = 0; i < items.length; i++) {
          height += itemSizes.get(i) || estimatedItemHeight
        }
        return height
      }
      return items.length * getItemHeight(0)
    }
  }, [items.length, getItemHeight, itemSizes, estimatedItemHeight, dynamicHeight, horizontal])

  // Calculate visible range with enhanced performance
  const visibleRange = useMemo(() => {
    const scrollPos = horizontal ? scrollLeft : scrollTop
    const containerSize = horizontal ? containerHeight : containerHeight
    let start = 0
    let offsetPos = 0
    let end = 0

    if (dynamicHeight && itemSizes.size > 0) {
      // Find start index based on accumulated sizes
      let accumulatedSize = 0
      for (let i = 0; i < items.length; i++) {
        const itemSize = itemSizes.get(i) || estimatedItemHeight
        if (accumulatedSize + itemSize > scrollPos) {
          start = i
          offsetPos = accumulatedSize
          break
        }
        accumulatedSize += itemSize
      }

      // Calculate end index
      let visibleSize = 0
      end = start
      for (let i = start; i < items.length; i++) {
        visibleSize += itemSizes.get(i) || estimatedItemHeight
        if (visibleSize > containerSize) {
          end = i + 1
          break
        }
        end = i + 1
      }
    } else {
      const itemSize = getItemHeight(0)
      start = Math.floor(scrollPos / itemSize)
      const visibleCount = Math.ceil(containerSize / itemSize)
      end = Math.min(start + visibleCount, items.length)
      offsetPos = start * itemSize
    }

    // Add overscan for better performance
    const startIndex = Math.max(0, start - overscan)
    const endIndex = Math.min(items.length, end + overscan)

    return { startIndex, endIndex, offsetPos }
  }, [scrollTop, scrollLeft, containerHeight, items.length, getItemHeight, overscan, itemSizes, estimatedItemHeight, dynamicHeight, horizontal])

  // Enhanced scroll handling with debouncing and direction detection
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop
    const newScrollLeft = e.currentTarget.scrollLeft
    
    // Detect scroll direction
    const verticalDirection = newScrollTop > lastScrollTopRef.current ? 'down' : 'up'
    const horizontalDirection = newScrollLeft > lastScrollLeftRef.current ? 'right' : 'left'
    const newDirection = horizontal ? horizontalDirection : verticalDirection
    
    if (newDirection !== scrollDirection) {
      setScrollDirection(newDirection)
    }
    
    lastScrollTopRef.current = newScrollTop
    lastScrollLeftRef.current = newScrollLeft
    
    setIsScrolling(true)
    
    // Clear existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current)
    }
    
    // Set new timeout to detect when scrolling stops
    scrollTimeoutRef.current = setTimeout(() => {
      setIsScrolling(false)
      setScrollDirection(null)
    }, 150)
    
    if (horizontal) {
      setScrollLeft(newScrollLeft)
    } else {
      setScrollTop(newScrollTop)
    }
    
    onScroll?.(horizontal ? newScrollLeft : newScrollTop, {
      start: visibleRange.startIndex,
      end: visibleRange.endIndex
    })
  }, [onScroll, visibleRange.startIndex, visibleRange.endIndex, horizontal, scrollDirection])

  // Update item sizes for dynamic height
  const updateItemSize = useCallback((index: number, size: number) => {
    if (!dynamicHeight) return
    
    setItemSizes(prev => {
      const newSizes = new Map(prev)
      if (newSizes.get(index) !== size) {
        newSizes.set(index, size)
      }
      return newSizes
    })
  }, [dynamicHeight])

  // Measure items when they render
  useEffect(() => {
    if (!dynamicHeight) return

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const element = entry.target as HTMLDivElement
        const index = parseInt(element.dataset.index || '0')
        if (!isNaN(index)) {
          updateItemSize(index, entry.contentRect.height)
        }
      }
    })

    itemsRef.current.forEach((element) => {
      observer.observe(element)
    })

    return () => {
      observer.disconnect()
    }
  }, [dynamicHeight, updateItemSize, visibleRange])

  // Enhanced accessibility: handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!containerRef.current) return

    const itemSize = getItemHeight(0)
    const currentScrollPos = horizontal ? scrollLeft : scrollTop
    const maxScrollPos = totalSize - (horizontal ? containerHeight : containerHeight)
    let newScrollPos = currentScrollPos

    switch (e.key) {
      case 'ArrowUp':
        if (horizontal) break
        e.preventDefault()
        newScrollPos = Math.max(0, currentScrollPos - itemSize)
        break
      case 'ArrowDown':
        if (horizontal) break
        e.preventDefault()
        newScrollPos = Math.min(maxScrollPos, currentScrollPos + itemSize)
        break
      case 'ArrowLeft':
        if (!horizontal) break
        e.preventDefault()
        newScrollPos = Math.max(0, currentScrollPos - itemSize)
        break
      case 'ArrowRight':
        if (!horizontal) break
        e.preventDefault()
        newScrollPos = Math.min(maxScrollPos, currentScrollPos + itemSize)
        break
      case 'PageUp':
        e.preventDefault()
        newScrollPos = Math.max(0, currentScrollPos - (horizontal ? containerHeight : containerHeight))
        break
      case 'PageDown':
        e.preventDefault()
        newScrollPos = Math.min(maxScrollPos, currentScrollPos + (horizontal ? containerHeight : containerHeight))
        break
      case 'Home':
        e.preventDefault()
        newScrollPos = 0
        break
      case 'End':
        e.preventDefault()
        newScrollPos = maxScrollPos
        break
    }

    if (newScrollPos !== currentScrollPos && scrollElementRef.current) {
      if (horizontal) {
        scrollElementRef.current.scrollLeft = newScrollPos
      } else {
        scrollElementRef.current.scrollTop = newScrollPos
      }
    }
  }, [horizontal, scrollLeft, scrollTop, totalSize, containerHeight, getItemHeight])

  // Enhanced render item with visibility tracking
  const renderVirtualItem = useCallback((item: VirtualScrollItem, index: number, isVisible: boolean) => {
    if (renderItem) {
      return renderItem(item, index, isVisible)
    }

    return (
      <div className={`p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors duration-150 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}>
        {item.content}
      </div>
    )
  }, [renderItem])

  // Calculate offset for dynamic height items
  const getItemOffset = useCallback((index: number): number => {
    if (!dynamicHeight || itemSizes.size === 0) {
      return index * getItemHeight(0)
    }

    let offset = 0
    for (let i = 0; i < index; i++) {
      offset += itemSizes.get(i) || estimatedItemHeight
    }
    return offset
  }, [dynamicHeight, itemSizes, estimatedItemHeight, getItemHeight])

  // Scroll to specific index
  const scrollToItem = useCallback((index: number, alignment: 'start' | 'center' | 'end' | 'auto' = 'start') => {
    if (!scrollElementRef.current || index < 0 || index >= items.length) return

    let offset = getItemOffset(index)
    const itemSize = getItemHeight(index, items[index]?.data)
    const containerSize = horizontal ? containerHeight : containerHeight
    const maxScroll = totalSize - containerSize

    if (alignment === 'center') {
      offset = offset - (containerSize - itemSize) / 2
    } else if (alignment === 'end') {
      offset = offset - (containerSize - itemSize)
    } else if (alignment === 'auto') {
      const currentScrollPos = horizontal ? scrollLeft : scrollTop
      if (offset < currentScrollPos) {
        alignment = 'start'
      } else if (offset + itemSize > currentScrollPos + containerSize) {
        alignment = 'end'
      } else {
        return // Item is already visible
      }
    }

    offset = Math.max(0, Math.min(offset, maxScroll))

    if (horizontal) {
      scrollElementRef.current.scrollLeft = offset
    } else {
      scrollElementRef.current.scrollTop = offset
    }
  }, [horizontal, scrollLeft, scrollTop, totalSize, containerHeight, getItemOffset, getItemHeight, items])

  // Handle scrollToIndex prop
  useEffect(() => {
    if (scrollToIndex !== undefined) {
      scrollToItem(scrollToIndex, scrollToAlignment)
    }
  }, [scrollToIndex, scrollToAlignment, scrollToItem])

  // Call onItemsRendered callback
  useEffect(() => {
    onItemsRendered?.({
      start: visibleRange.startIndex,
      end: visibleRange.endIndex
    })
  }, [visibleRange.startIndex, visibleRange.endIndex, onItemsRendered])

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative overflow-auto focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg',
        horizontal ? 'overflow-x-auto overflow-y-hidden' : 'overflow-y-auto overflow-x-hidden',
        className
      )}
      style={{ 
        height: horizontal ? 'auto' : containerHeight, 
        width: horizontal ? containerHeight : 'auto' 
      }}
      onScroll={handleScroll}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role={horizontal ? 'region' : 'region'}
      aria-label={ariaLabel}
      aria-orientation={horizontal ? 'horizontal' : 'vertical'}
      data-testid={testId}
    >
      <div
        ref={scrollElementRef}
        className="relative"
        style={{ 
          [horizontal ? 'width' : 'height']: totalSize, 
          [horizontal ? 'minWidth' : 'minHeight']: horizontal ? containerHeight : containerHeight 
        }}
      >
        {/* Loading indicator */}
        {loading && (
          <div className="absolute top-0 left-0 right-0 z-10 flex justify-center p-4">
            {loadingComponent || (
              <div className="flex items-center gap-2 bg-white rounded-lg shadow-lg px-4 py-2">
                <div className="animate-spin h-4 w-4 border border-current border-t-transparent rounded-full" />
                <span className="text-sm text-gray-600">Loading...</span>
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!loading && items.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            {emptyComponent || (
              <div className="text-center text-gray-500 py-8">
                <p className="text-lg font-medium">No items to display</p>
                <p className="text-sm mt-1">Try adjusting your filters or add some content</p>
              </div>
            )}
          </div>
        )}

        {/* Spacer before visible items */}
        <div
          style={{
            [horizontal ? 'width' : 'height']: dynamicHeight 
              ? getItemOffset(visibleRange.startIndex) 
              : visibleRange.offsetPos,
            position: 'absolute',
            top: 0,
            left: 0,
            [horizontal ? 'height' : 'width']: '100%',
          }}
        />

        {/* Visible items */}
        {items.slice(visibleRange.startIndex, visibleRange.endIndex).map((item, index) => {
          const actualIndex = visibleRange.startIndex + index
          const itemOffset = dynamicHeight 
            ? getItemOffset(actualIndex) 
            : visibleRange.offsetPos + index * getItemHeight(actualIndex, item.data)
          const itemSizeValue = getItemHeight(actualIndex, item.data)
          const isVisible = actualIndex >= visibleRange.startIndex && actualIndex < visibleRange.endIndex

          return (
            <div
              key={item.id}
              ref={(el) => {
                if (el && dynamicHeight) {
                  itemsRef.current.set(actualIndex, el)
                }
              }}
              data-index={actualIndex}
              className={cn(
                'absolute left-0 top-0',
                horizontal ? 'h-full' : 'w-full'
              )}
              style={{
                [horizontal ? 'left' : 'top']: itemOffset,
                [horizontal ? 'width' : 'height']: dynamicHeight ? 'auto' : itemSizeValue,
                transition: isScrolling ? 'none' : 'opacity 0.2s ease-in-out',
              }}
              role="listitem"
              aria-rowindex={actualIndex + 1}
              aria-setsize={items.length}
            >
              {renderVirtualItem(item, actualIndex, isVisible)}
            </div>
          )
        })}
      </div>

      {/* Scroll indicator and performance info */}
      {showScrollIndicator && items.length > 0 && (
        <div className="absolute bottom-2 right-2 bg-gray-800 text-white px-2 py-1 rounded text-xs shadow-lg z-20">
          <div className="flex flex-col gap-1">
            <span>{items.length.toLocaleString()} items</span>
            {items.length > 1000 && (
              <span className="text-green-300">Optimized</span>
            )}
            {isScrolling && (
              <span className="text-yellow-300">Scrolling...</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Hook for managing virtual scroll state
export function useVirtualScroll(_options: {
  itemCount: number
  itemHeight?: number | ((index: number) => number)
  containerHeight?: number
  overscan?: number
}) {
  const [scrollTop, setScrollTop] = useState(0)
  
  const scrollToIndex = useCallback((_index: number, _alignment: 'start' | 'center' | 'end' = 'start') => {
    // This would need to be implemented based on the scroll container
    // For now, this is a placeholder for the hook interface
  }, [])

  const scrollToTop = useCallback(() => {
    setScrollTop(0)
  }, [])

  const scrollToBottom = useCallback(() => {
    // Calculate bottom scroll position
    // This would need the total height calculation
  }, [])

  return {
    scrollTop,
    setScrollTop,
    scrollToIndex,
    scrollToTop,
    scrollToBottom,
  }
}
