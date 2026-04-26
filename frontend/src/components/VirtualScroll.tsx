import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { cn } from '../lib/utils'

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
  renderItem: (item: VirtualScrollItem, index: number) => React.ReactNode
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
  const [itemSizes, setItemSizes] = useState(new Map<number, number>())
  const containerRef = useRef<HTMLDivElement>(null)
  const itemsRef = useRef<Map<number, HTMLDivElement>>(new Map())

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
    let height = 0
    for (let i = 0; i < items.length; i++) {
      height += getItemHeight(i)
    }
    return height
  }, [items.length, getItemHeight])

  // Calculate visible range
  const visibleRange = useMemo(() => {
    let start = 0
    let end = 0
    let accumulatedHeight = 0

    // Find start index
    for (let i = 0; i < items.length; i++) {
      const itemHeight = getItemHeight(i)
      if (accumulatedHeight + itemHeight > scrollTop) {
        start = i
        break
      }
      accumulatedHeight += itemHeight
    }

    // Find end index
    accumulatedHeight = 0
    for (let i = 0; i < items.length; i++) {
      const itemHeight = getItemHeight(i)
      accumulatedHeight += itemHeight
      if (accumulatedHeight > scrollTop + containerHeight) {
        end = i + 1
        break
      }
      end = i + 1
    }

    // Add overscan
    start = Math.max(0, start - overscan)
    end = Math.min(items.length, end + overscan)

    return { start, end }
  }, [scrollTop, containerHeight, items.length, getItemHeight, overscan])

  // Calculate offset for visible items
  const getOffsetTop = useCallback((index: number): number => {
    let offset = 0
    for (let i = 0; i < index; i++) {
      offset += getItemHeight(i)
    }
    return offset
  }, [getItemHeight])

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

  // Handle scroll
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop
    setScrollTop(newScrollTop)
    onScroll?.(newScrollTop)
  }, [onScroll])

  // Measure items when they render
  useEffect(() => {
    if (!dynamicHeight) return

    const observer = new ResizeObserver((entries) => {
      entries.forEach((entry) => {
        const element = entry.target as HTMLDivElement
        const index = parseInt(element.dataset.index || '0')
        const height = entry.contentRect.height
        updateItemSize(index, height)
      })
    })

    itemsRef.current.forEach((element) => {
      observer.observe(element)
    })

    return () => {
      observer.disconnect()
    }
  }, [dynamicHeight, updateItemSize, visibleRange])

  return (
    <div
      ref={containerRef}
      className={cn('overflow-auto', className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {items.slice(visibleRange.start, visibleRange.end).map((item, index) => {
          const actualIndex = visibleRange.start + index
          const offsetTop = getOffsetTop(actualIndex)
          const itemHeight = getItemHeight(actualIndex)

          return (
            <div
              key={item.id}
              ref={(element) => {
                if (element && dynamicHeight) {
                  itemsRef.current.set(actualIndex, element)
                }
              }}
              data-index={actualIndex}
              style={{
                position: 'absolute',
                top: offsetTop,
                left: 0,
                right: 0,
                height: dynamicHeight ? 'auto' : itemHeight,
              }}
            >
              {renderItem(item, actualIndex)}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default VirtualScroll
