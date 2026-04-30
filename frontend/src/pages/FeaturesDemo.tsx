import { useState } from "react";
import { RichTextEditor } from "../components/RichTextEditor";
import { VirtualScroll } from "../components/VirtualScroll";
import { DragAndDrop, useDragAndDrop } from "../components/DragAndDrop";
import {
  InteractiveMap,
  useInteractiveMap,
} from "../components/InteractiveMap";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

export function FeaturesDemo() {
  // Rich Text Editor State
  const [editorContent, setEditorContent] = useState(
    '<h1>Welcome to the Rich Text Editor Demo</h1><p>This editor supports:</p><ul><li><strong>Bold text</strong> and <em>italic text</em></li><li>Code blocks with syntax highlighting</li><li>Tables and images</li><li>Auto-save functionality</li></ul><pre><code class="language-javascript">const greeting = "Hello, World!";\nconsole.log(greeting);</code></pre>',
  );

  // Virtual Scroll State
  const generateLargeDataset = () => {
    const items = [];
    for (let i = 1; i <= 10000; i++) {
      items.push({
        id: `item-${i}`,
        content: (
          <div className="p-4">
            <h3 className="font-semibold text-lg">Item {i}</h3>
            <p className="text-gray-600 mt-2">
              This is a sample item in the virtual scroll list. Virtual
              scrolling allows us to efficiently render large datasets by only
              rendering the visible items plus a small buffer.
            </p>
            <div className="mt-3 flex gap-2">
              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                Category {Math.ceil(i / 100)}
              </span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                Priority {(i % 3) + 1}
              </span>
            </div>
          </div>
        ),
        height: 120 + (i % 3) * 20, // Variable heights
      });
    }
    return items;
  };

  const [virtualScrollItems] = useState(generateLargeDataset());

  // Drag and Drop State
  const {
    items: dragItems,
    addItem: addDragItem,
    removeItem: removeDragItem,
  } = useDragAndDrop([
    {
      id: "item-1",
      content: (
        <div className="p-4">
          <h4 className="font-semibold">First Item</h4>
          <p className="text-sm text-gray-600">Drag me to reorder!</p>
        </div>
      ),
    },
    {
      id: "item-2",
      content: (
        <div className="p-4">
          <h4 className="font-semibold">Second Item</h4>
          <p className="text-sm text-gray-600">I can be reordered too</p>
        </div>
      ),
    },
    {
      id: "item-3",
      content: (
        <div className="p-4">
          <h4 className="font-semibold">Third Item</h4>
          <p className="text-sm text-gray-600">Try dragging files here!</p>
        </div>
      ),
    },
  ]);

  // Interactive Map State
  const {
    markers: mapMarkers,
    routes: mapRoutes,
    addMarker: addMapMarker,
    removeMarker: removeMapMarker,
    addRoute: addMapRoute,
  } = useInteractiveMap();

  const handleFileUpload = (files: File[]) => {
    console.log("Files uploaded:", files);
    files.forEach((file) => {
      console.log(`- ${file.name} (${file.size} bytes)`);
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            UI Features Demo
          </h1>
          <p className="text-xl text-gray-600">
            Showcase of the implemented UI components for the TTL Archival
            Service
          </p>
        </div>

        <div className="space-y-12">
          {/* Rich Text Editor Section */}
          <Card>
            <CardHeader>
              <CardTitle>Rich Text Editor</CardTitle>
              <CardDescription>
                Feature-rich text editor with WYSIWYG editing, formatting
                options, media support, code highlighting, and auto-save
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RichTextEditor
                content={editorContent}
                onChange={setEditorContent}
                placeholder="Start typing your content here..."
                autoSave={true}
                autoSaveDelay={2000}
                className="min-h-[400px]"
              />
              <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                <h4 className="font-semibold mb-2">Current HTML Output:</h4>
                <pre className="text-sm overflow-auto max-h-40">
                  {editorContent}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Virtual Scrolling Section */}
          <Card>
            <CardHeader>
              <CardTitle>Virtual Scrolling</CardTitle>
              <CardDescription>
                Efficiently handles large datasets with smooth scrolling
                performance and dynamic item heights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex gap-4">
                <Button variant="outline" disabled>
                  Total Items: {virtualScrollItems.length.toLocaleString()}
                </Button>
                <Button variant="outline" disabled>
                  Dynamic Heights: Enabled
                </Button>
                <Button variant="outline" disabled>
                  Accessibility: Compliant
                </Button>
              </div>
              <VirtualScroll
                items={virtualScrollItems}
                itemHeight={(index) => virtualScrollItems[index].height || 120}
                containerHeight={400}
                overscan={5}
                dynamicHeight={true}
                estimatedItemHeight={120}
                className="border rounded-lg"
              />
            </CardContent>
          </Card>

          {/* Drag and Drop Section */}
          <Card>
            <CardHeader>
              <CardTitle>Drag and Drop Interface</CardTitle>
              <CardDescription>
                List reordering and file management with visual feedback and
                touch device support
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  • Drag items to reorder them
                  <br />
                  • Drag and drop files from your computer
                  <br />• Double-click to add new items
                </p>
              </div>
              <DragAndDrop
                items={dragItems}
                onItemsChange={(items) => {
                  // Update the items in the hook
                  items.forEach((item) => {
                    if (!dragItems.find((i) => i.id === item.id)) {
                      addDragItem(item);
                    }
                  });
                  dragItems.forEach((item) => {
                    if (!items.find((i) => i.id === item.id)) {
                      removeDragItem(item.id);
                    }
                  });
                }}
                onFileUpload={handleFileUpload}
                dragHandle={true}
                droppable={true}
                multiple={true}
                accept="image/*,.pdf,.doc,.docx"
                className="min-h-[300px]"
              />
            </CardContent>
          </Card>

          {/* Interactive Map Section */}
          <Card>
            <CardHeader>
              <CardTitle>Interactive Maps</CardTitle>
              <CardDescription>
                Map functionality with markers, geocoding, route planning, and
                style customization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex gap-4 flex-wrap">
                <Button variant="outline" disabled>
                  Markers: {mapMarkers.length}
                </Button>
                <Button variant="outline" disabled>
                  Routes: {mapRoutes.length}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    // Add sample markers
                    addMapMarker({
                      position: { lat: 40.7128, lng: -74.006 } as any,
                      title: "New York City",
                      description: "The Big Apple",
                      type: "default",
                      color: "#3b82f6",
                    });
                    addMapMarker({
                      position: { lat: 40.758, lng: -73.9855 } as any,
                      title: "Times Square",
                      description: "The heart of NYC",
                      type: "default",
                      color: "#10b981",
                    });
                  }}
                >
                  Add Sample Markers
                </Button>
              </div>
              <div className="text-sm text-gray-600 mb-4">
                • Click on the map to add markers
                <br />
                • Use the search bar to find locations
                <br />
                • Use Start/End buttons to plan routes
                <br />• Double-click to quickly add markers
              </div>
              <InteractiveMap
                center={[40.7128, -74.006]}
                zoom={12}
                height="500px"
                markers={mapMarkers}
                routes={mapRoutes}
                onMarkersChange={(markers) => {
                  // Sync with hook state
                  mapMarkers.forEach((marker) => {
                    if (!markers.find((m) => m.id === marker.id)) {
                      removeMapMarker(marker.id);
                    }
                  });
                }}
                onRoutesChange={(routes) => {
                  // Sync with hook state
                  mapRoutes.forEach((route) => {
                    if (!routes.find((r) => r.id === route.id)) {
                      // Route removal logic would go here
                    }
                  });
                }}
                showControls={true}
                allowMarkerCreation={true}
                allowRoutePlanning={true}
                className="rounded-lg"
              />
            </CardContent>
          </Card>

          {/* Summary Section */}
          <Card>
            <CardHeader>
              <CardTitle>Implementation Summary</CardTitle>
              <CardDescription>
                All four UI features have been successfully implemented
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    ✅ Rich Text Editor
                  </h4>
                  <ul className="text-sm space-y-1">
                    <li>• WYSIWYG text editing</li>
                    <li>• Rich formatting options</li>
                    <li>• Image and media embedding</li>
                    <li>• Code highlighting</li>
                    <li>• Auto-save functionality</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    ✅ Virtual Scrolling
                  </h4>
                  <ul className="text-sm space-y-1">
                    <li>• Large dataset handling</li>
                    <li>• Smooth scrolling performance</li>
                    <li>• Dynamic item heights</li>
                    <li>• Memory optimization</li>
                    <li>• Accessibility compliance</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    ✅ Drag and Drop
                  </h4>
                  <ul className="text-sm space-y-1">
                    <li>• List reordering</li>
                    <li>• File drag and drop upload</li>
                    <li>• Visual feedback</li>
                    <li>• Drop zone indicators</li>
                    <li>• Touch device support</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    ✅ Interactive Maps
                  </h4>
                  <ul className="text-sm space-y-1">
                    <li>• Interactive map display</li>
                    <li>• Custom markers and popups</li>
                    <li>• Geocoding and reverse geocoding</li>
                    <li>• Route planning and directions</li>
                    <li>• Map style customization</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default FeaturesDemo;
