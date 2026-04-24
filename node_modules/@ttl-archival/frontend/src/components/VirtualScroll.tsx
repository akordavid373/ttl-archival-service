import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { cn } from '../utils/cn'

interface VirtualScrollItem {
  id: string | number
  height?: number
  content: React.ReactNode
}

interface VirtualScrollProps {
  items: VirtualScrollItem[]
  itemHeight?: number | ((index: number) => number)
  containerHeight?: number
  overscan?: number
  className?: string
  onScroll?: (scrollTop: number) => void
  renderItem?: (item: VirtualScrollItem, index: number) => React.ReactNode
  estimatedItemHeight?: number
  dynamicHeight?: boolean
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
}: VirtualScrollProps) {
  const [scrollTop, setScrollTop] = useState(0)
  const [itemSizes, setItemSizes] = useState<Map<number, number>>(new Map())
  const containerRef = useRef<HTMLDivElement>(null)
  const itemsRef = useRef<Map<number, HTMLDivElement>>(new Map())
  const scrollElementRef = useRef<HTMLDivElement>(null)

  // Calculate item height
  const getItemHeight = useCallback((index: number): number => {
    if (dynamicHeight && itemSizes.has(index)) {
      return itemSizes.get(index)!
    }
    if (typeof itemHeight === 'function') {
      return itemHeight(index)
    }
    return itemHeight as number
  }, [itemHeight, itemSizes, dynamicHeight])

  // Calculate total height
  const totalHeight = useMemo(() => {
    if (dynamicHeight && itemSizes.size > 0) {
      let height = 0
      for (let i = 0; i < items.length; i++) {
        height += itemSizes.get(i) || estimatedItemHeight
      }
      return height
    }
    return items.length * getItemHeight(0)
  }, [items.length, getItemHeight, itemSizes, estimatedItemHeight, dynamicHeight])

  // Calculate visible range
  const visibleRange = useMemo(() => {
    let start = 0
    let offsetTop = 0

    if (dynamicHeight && itemSizes.size > 0) {
      // Find start index based on accumulated heights
      let accumulatedHeight = 0
      for (let i = 0; i < items.length; i++) {
        const itemHeight = itemSizes.get(i) || estimatedItemHeight
        if (accumulatedHeight + itemHeight > scrollTop) {
          start = i
          offsetTop = accumulatedHeight
          break
        }
        accumulatedHeight += itemHeight
      }

      // Calculate end index
      let visibleHeight = 0
      let end = start
      for (let i = start; i < items.length; i++) {
        visibleHeight += itemSizes.get(i) || estimatedItemHeight
        if (visibleHeight > containerHeight) {
          end = i + 1
          break
        }
        end = i + 1
      }
    } else {
      const itemH = getItemHeight(0)
      start = Math.floor(scrollTop / itemH)
      const visibleCount = Math.ceil(containerHeight / itemH)
      end = Math.min(start + visibleCount, items.length)
      offsetTop = start * itemH
    }

    // Add overscan
    const startIndex = Math.max(0, start - overscan)
    const endIndex = Math.min(items.length, end + overscan)

    return { startIndex, endIndex, offsetTop }
  }, [scrollTop, containerHeight, items.length, getItemHeight, overscan, itemSizes, estimatedItemHeight, dynamicHeight])

  // Handle scroll
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop
    setScrollTop(newScrollTop)
    onScroll?.(newScrollTop)
  }, [onScroll])

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

  // Accessibility: handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!containerRef.current) return

    const itemHeight = getItemHeight(0)
    let newScrollTop = scrollTop

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault()
        newScrollTop = Math.max(0, scrollTop - itemHeight)
        break
      case 'ArrowDown':
        e.preventDefault()
        newScrollTop = Math.min(totalHeight - containerHeight, scrollTop + itemHeight)
        break
      case 'PageUp':
        e.preventDefault()
        newScrollTop = Math.max(0, scrollTop - containerHeight)
        break
      case 'PageDown':
        e.preventDefault()
        newScrollTop = Math.min(totalHeight - containerHeight, scrollTop + containerHeight)
        break
      case 'Home':
        e.preventDefault()
        newScrollTop = 0
        break
      case 'End':
        e.preventDefault()
        newScrollTop = totalHeight - containerHeight
        break
    }

    if (newScrollTop !== scrollTop && scrollElementRef.current) {
      scrollElementRef.current.scrollTop = newScrollTop
    }
  }, [scrollTop, totalHeight, containerHeight, getItemHeight])

  // Render item
  const renderVirtualItem = useCallback((item: VirtualScrollItem, index: number) => {
    if (renderItem) {
      return renderItem(item, index)
    }

    return (
      <div className="p-4 border-b border-gray-200 hover:bg-gray-50">
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

  return (
    <div
      ref={containerRef}
      className={cn('relative overflow-auto', className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="region"
      aria-label="Virtual scrollable list"
    >
      <div
        ref={scrollElementRef}
        className="relative"
        style={{ height: totalHeight, minHeight: containerHeight }}
      >
        {/* Spacer before visible items */}
        <div
          style={{
            height: dynamicHeight ? getItemOffset(visibleRange.startIndex) : visibleRange.offsetTop,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        />

        {/* Visible items */}
        {items.slice(visibleRange.startIndex, visibleRange.endIndex).map((item, index) => {
          const actualIndex = visibleRange.startIndex + index
          const itemOffset = dynamicHeight ? getItemOffset(actualIndex) : visibleRange.offsetTop + index * getItemHeight(actualIndex)
          const itemHeightValue = getItemHeight(actualIndex)

          return (
            <div
              key={item.id}
              ref={(el) => {
                if (el && dynamicHeight) {
                  itemsRef.current.set(actualIndex, el)
                }
              }}
              data-index={actualIndex}
              className="absolute left-0 right-0"
              style={{
                top: itemOffset,
                height: dynamicHeight ? 'auto' : itemHeightValue,
              }}
              role="listitem"
              aria-rowindex={actualIndex + 1}
            >
              {renderVirtualItem(item, actualIndex)}
            </div>
          )
        })}
      </div>

      {/* Loading indicator for large datasets */}
      {items.length > 1000 && (
        <div className="absolute bottom-2 right-2 bg-gray-800 text-white px-2 py-1 rounded text-xs">
          {items.length.toLocaleString()} items
        </div>
      )}
    </div>
  )
}

// Hook for managing virtual scroll state
export function useVirtualScroll(options: {
  itemCount: number
  itemHeight?: number | ((index: number) => number)
  containerHeight?: number
  overscan?: number
}) {
  const [scrollTop, setScrollTop] = useState(0)
  
  const scrollToIndex = useCallback((index: number, alignment: 'start' | 'center' | 'end' = 'start') => {
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
