import { useState, useRef, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, useMapEvents } from 'react-leaflet'
import { Icon, LatLng, LatLngBounds, LeafletMouseEvent } from 'leaflet'
import { cn } from '../utils/cn'
import { Button } from './ui/button'
import { 
  Navigation, 
  Route, 
  Search, 
  Plus, 
  Trash2, 
  Maximize2, 
  Minimize2
} from 'lucide-react'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icon in react-leaflet
delete (Icon.Default.prototype as any)._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface MapMarker {
  id: string
  position: LatLng
  title: string
  description?: string
  type?: 'default' | 'start' | 'end' | 'waypoint'
  color?: string
}

interface MapRoute {
  id: string
  name: string
  waypoints: LatLng[]
  color?: string
  distance?: number
  duration?: string
}

interface InteractiveMapProps {
  center?: [number, number]
  zoom?: number
  height?: string
  className?: string
  markers?: MapMarker[]
  routes?: MapRoute[]
  onMarkersChange?: (markers: MapMarker[]) => void
  onRoutesChange?: (routes: MapRoute[]) => void
  onMarkerClick?: (marker: MapMarker) => void
  onMapClick?: (latlng: LatLng) => void
  showControls?: boolean
  allowMarkerCreation?: boolean
  allowRoutePlanning?: boolean
  tileLayer?: string
}

// Custom hook for map events
function MapEventHandler({
  onMapClick,
  onMarkerAdd,
}: {
  onMapClick?: (latlng: LatLng) => void
  onMarkerAdd?: (latlng: LatLng) => void
}) {
  useMapEvents({
    click: (e: LeafletMouseEvent) => {
      if (onMapClick) {
        onMapClick(e.latlng)
      }
    },
    dblclick: (e: LeafletMouseEvent) => {
      if (onMarkerAdd) {
        onMarkerAdd(e.latlng)
        e.originalEvent.preventDefault()
      }
    },
  })
  return null
}

// Component for map controls
function MapControls({
  center,
  zoom,
  onFitBounds,
  onToggleFullscreen,
  isFullscreen,
}: {
  center: [number, number]
  zoom: number
  onFitBounds: () => void
  onToggleFullscreen: () => void
  isFullscreen: boolean
}) {
  const map = useMap()

  const handleResetView = () => {
    map.setView(center, zoom)
  }

  const handleZoomIn = () => {
    map.zoomIn()
  }

  const handleZoomOut = () => {
    map.zoomOut()
  }

  return (
    <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
      <Button
        variant="secondary"
        size="sm"
        onClick={handleResetView}
        className="bg-white shadow-md"
      >
        <Navigation className="h-4 w-4" />
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={handleZoomIn}
        className="bg-white shadow-md"
      >
        <Plus className="h-4 w-4" />
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={handleZoomOut}
        className="bg-white shadow-md"
      >
        <Trash2 className="h-4 w-4" />
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={onFitBounds}
        className="bg-white shadow-md"
      >
        <Maximize2 className="h-4 w-4" />
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={onToggleFullscreen}
        className="bg-white shadow-md"
      >
        {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
      </Button>
    </div>
  )
}

export function InteractiveMap({
  center = [40.7128, -74.0060], // New York City
  zoom = 13,
  height = '400px',
  className = '',
  markers = [],
  routes = [],
  onMarkersChange,
  onRoutesChange,
  onMarkerClick,
  onMapClick,
  showControls = true,
  allowMarkerCreation = true,
  allowRoutePlanning = true,
  tileLayer = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
}: InteractiveMapProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null)
  const [routeMode, setRouteMode] = useState<'start' | 'end' | null>(null)
  const mapRef = useRef<any>(null)

  // Geocoding function
  const geocode = useCallback(async (query: string): Promise<LatLng | null> => {
    setIsSearching(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      )
      const data = await response.json()
      if (data && data.length > 0) {
        const { lat, lon } = data[0]
        return new LatLng(parseFloat(lat), parseFloat(lon))
      }
      return null
    } catch (error) {
      console.error('Geocoding error:', error)
      return null
    } finally {
      setIsSearching(false)
    }
  }, [])

  // Reverse geocoding function
  const reverseGeocode = useCallback(async (latlng: LatLng): Promise<string> => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}`
      )
      const data = await response.json()
      return data.display_name || 'Unknown location'
    } catch (error) {
      console.error('Reverse geocoding error:', error)
      return 'Unknown location'
    }
  }, [])

  // Handle search
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return

    const result = await geocode(searchQuery)
    if (result && mapRef.current) {
      mapRef.current.setView(result, 15)
      
      // Add a marker for the search result
      const newMarker: MapMarker = {
        id: `search-${Date.now()}`,
        position: result,
        title: searchQuery,
        description: await reverseGeocode(result),
        type: 'default',
        color: '#3b82f6',
      }
      
      if (onMarkersChange) {
        onMarkersChange([...markers, newMarker])
      }
    }
  }, [searchQuery, geocode, reverseGeocode, markers, onMarkersChange])

  // Handle map click
  const handleMapClick = useCallback((latlng: LatLng) => {
    if (routeMode) {
      // Add waypoint for route planning
      const newMarker: MapMarker = {
        id: `waypoint-${Date.now()}`,
        position: latlng,
        title: routeMode === 'start' ? 'Start Point' : 'End Point',
        type: routeMode,
        color: routeMode === 'start' ? '#10b981' : '#ef4444',
      }
      
      if (onMarkersChange) {
        const updatedMarkers = markers.filter(m => m.type !== routeMode).concat(newMarker)
        onMarkersChange(updatedMarkers)
      }
      
      setRouteMode(null)
    } else if (allowMarkerCreation) {
      const newMarker: MapMarker = {
        id: `marker-${Date.now()}`,
        position: latlng,
        title: `Marker ${markers.length + 1}`,
        description: '', // Will be filled asynchronously
        type: 'default',
        color: '#3b82f6',
      }
      
      if (onMarkersChange) {
        onMarkersChange([...markers, newMarker])
      }
    }
    
    onMapClick?.(latlng)
  }, [routeMode, allowMarkerCreation, markers, onMarkersChange, onMapClick, reverseGeocode])

  // Handle marker click
  const handleMarkerClick = useCallback((marker: MapMarker) => {
    onMarkerClick?.(marker)
  }, [onMarkerClick])

  // Remove marker
  const removeMarker = useCallback((markerId: string) => {
    if (onMarkersChange) {
      onMarkersChange(markers.filter(m => m.id !== markerId))
    }
  }, [markers, onMarkersChange])

  // Calculate route
  const calculateRoute = useCallback(async () => {
    const startMarker = markers.find(m => m.type === 'start')
    const endMarker = markers.find(m => m.type === 'end')
    
    if (!startMarker || !endMarker) return

    try {
      const response = await fetch(
        `https://router.project-osrm.org/route/v1/driving/${startMarker.position.lng},${startMarker.position.lat};${endMarker.position.lng},${endMarker.position.lat}?overview=full&geometries=geojson`
      )
      const data = await response.json()
      
      if (data.routes && data.routes.length > 0) {
        const route = data.routes[0]
        const coordinates = route.geometry.coordinates.map((coord: [number, number]) => 
          new LatLng(coord[1], coord[0])
        )
        
        const newRoute: MapRoute = {
          id: `route-${Date.now()}`,
          name: `Route ${routes.length + 1}`,
          waypoints: coordinates,
          color: '#3b82f6',
          distance: route.distance / 1000, // Convert to km
          duration: `${Math.round(route.duration / 60)} min`, // Convert to minutes
        }
        
        if (onRoutesChange) {
          onRoutesChange([...routes, newRoute])
        }
        
        setSelectedRoute(newRoute.id)
      }
    } catch (error) {
      console.error('Route calculation error:', error)
    }
  }, [markers, routes, onRoutesChange])

  // Fit map to show all markers and routes
  const fitBounds = useCallback(() => {
    if (!mapRef.current) return

    const bounds = new LatLngBounds()
    
    markers.forEach(marker => {
      bounds.extend(marker.position)
    })
    
    routes.forEach(route => {
      route.waypoints.forEach(waypoint => {
        bounds.extend(waypoint)
      })
    })

    if (bounds.isValid && bounds.isValid()) {
      mapRef.current.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [markers, routes])

  // Toggle fullscreen
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev)
  }, [])

  // Get marker icon
  const getMarkerIcon = useCallback((marker: MapMarker) => {
    const color = marker.color || '#3b82f6'
    return new Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color === '#10b981' ? 'green' : color === '#ef4444' ? 'red' : 'blue'}.png`,
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    })
  }, [])

  return (
    <div className={cn('relative rounded-lg overflow-hidden border', className)}>
      {/* Search Bar */}
      <div className="absolute top-4 left-4 z-[1000] flex gap-2">
        <div className="bg-white shadow-md rounded-lg p-2 flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search location..."
            className="px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSearch}
            disabled={isSearching}
            className="bg-white"
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>
        
        {allowRoutePlanning && (
          <div className="bg-white shadow-md rounded-lg p-2 flex gap-2">
            <Button
              variant={routeMode === 'start' ? 'default' : 'secondary'}
              size="sm"
              onClick={() => setRouteMode('start')}
              className="bg-white"
            >
              Start
            </Button>
            <Button
              variant={routeMode === 'end' ? 'default' : 'secondary'}
              size="sm"
              onClick={() => setRouteMode('end')}
              className="bg-white"
            >
              End
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={calculateRoute}
              disabled={!markers.find(m => m.type === 'start') || !markers.find(m => m.type === 'end')}
              className="bg-white"
            >
              <Route className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      {/* Map */}
      <div style={{ height: isFullscreen ? '100vh' : height }}>
        <MapContainer
          center={center}
          zoom={zoom}
          ref={mapRef}
          className="h-full w-full"
          whenCreated={(map: any) => {
            mapRef.current = map
          }}
        >
          <TileLayer
            url={tileLayer}
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          <MapEventHandler
            onMapClick={handleMapClick}
            onMarkerAdd={allowMarkerCreation ? handleMapClick : undefined}
          />

          {/* Markers */}
          {markers.map((marker) => (
            <Marker
              key={marker.id}
              position={marker.position}
              icon={getMarkerIcon(marker)}
              eventHandlers={{
                click: () => handleMarkerClick(marker),
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold">{marker.title}</h3>
                  {marker.description && (
                    <p className="text-sm text-gray-600 mt-1">{marker.description}</p>
                  )}
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => removeMarker(marker.id)}
                    className="mt-2"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Routes */}
          {routes.map((route) => (
            <Polyline
              key={route.id}
              positions={route.waypoints}
              color={route.color || '#3b82f6'}
              weight={selectedRoute === route.id ? 6 : 4}
              opacity={selectedRoute === route.id ? 1 : 0.7}
              eventHandlers={{
                click: () => setSelectedRoute(route.id),
              }}
            />
          ))}

          {/* Controls */}
          {showControls && (
            <MapControls
              center={center}
              zoom={zoom}
              onFitBounds={fitBounds}
              onToggleFullscreen={toggleFullscreen}
              isFullscreen={isFullscreen}
            />
          )}
        </MapContainer>
      </div>

      {/* Route Info */}
      {selectedRoute && (
        <div className="absolute bottom-4 left-4 z-[1000] bg-white shadow-md rounded-lg p-3">
          {routes.find(r => r.id === selectedRoute) && (
            <div className="text-sm">
              <h4 className="font-semibold">{routes.find(r => r.id === selectedRoute)?.name}</h4>
              <p className="text-gray-600">
                Distance: {routes.find(r => r.id === selectedRoute)?.distance?.toFixed(2)} km
              </p>
              <p className="text-gray-600">
                Duration: {routes.find(r => r.id === selectedRoute)?.duration} min
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Hook for map state management
export function useInteractiveMap() {
  const [markers, setMarkers] = useState<MapMarker[]>([])
  const [routes, setRoutes] = useState<MapRoute[]>([])

  const addMarker = useCallback((marker: Omit<MapMarker, 'id'>) => {
    const newMarker: MapMarker = {
      ...marker,
      id: `marker-${Date.now()}`,
    }
    setMarkers(prev => [...prev, newMarker])
    return newMarker
  }, [])

  const removeMarker = useCallback((id: string) => {
    setMarkers(prev => prev.filter(m => m.id !== id))
  }, [])

  const updateMarker = useCallback((id: string, updates: Partial<MapMarker>) => {
    setMarkers(prev => prev.map(m => 
      m.id === id ? { ...m, ...updates } : m
    ))
  }, [])

  const addRoute = useCallback((route: Omit<MapRoute, 'id'>) => {
    const newRoute: MapRoute = {
      ...route,
      id: `route-${Date.now()}`,
    }
    setRoutes(prev => [...prev, newRoute])
    return newRoute
  }, [])

  const removeRoute = useCallback((id: string) => {
    setRoutes(prev => prev.filter(r => r.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setMarkers([])
    setRoutes([])
  }, [])

  return {
    markers,
    routes,
    setMarkers,
    setRoutes,
    addMarker,
    removeMarker,
    updateMarker,
    addRoute,
    removeRoute,
    clearAll,
  }
}
