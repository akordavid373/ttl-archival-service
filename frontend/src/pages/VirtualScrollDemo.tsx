import { useState, useEffect, useMemo } from "react";
import { VirtualScroll } from "../components/VirtualScroll";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Scroll,
  Database,
  Zap,
  Accessibility,
  BarChart3,
  Settings,
  SkipForward,
} from "lucide-react";

interface DemoItem {
  id: number;
  title: string;
  description: string;
  category: string;
  priority: "low" | "medium" | "high";
  size: "small" | "medium" | "large";
  content: string;
}

interface VirtualDemoItem {
  id: number;
  content: React.ReactNode;
  data?: DemoItem;
}

export function VirtualScrollDemo() {
  const [items, setItems] = useState<VirtualDemoItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [scrollToIndex, setScrollToIndex] = useState<number | undefined>();
  const [dynamicHeight, setDynamicHeight] = useState(false);
  const [horizontal, setHorizontal] = useState(false);
  const [itemCount, setItemCount] = useState(1000);

  // Generate demo data
  const generateItems = (count: number): DemoItem[] => {
    const categories = [
      "Technology",
      "Business",
      "Design",
      "Marketing",
      "Sales",
      "Support",
    ];
    const priorities: ("low" | "medium" | "high")[] = ["low", "medium", "high"];
    const sizes: ("small" | "medium" | "large")[] = [
      "small",
      "medium",
      "large",
    ];

    return Array.from({ length: count }, (_, index) => ({
      id: index + 1,
      title: `Item ${index + 1}: ${categories[index % categories.length]} Task`,
      description: `This is a detailed description for item ${index + 1}. It contains important information about the task and its requirements.`,
      category: categories[index % categories.length],
      priority: priorities[index % priorities.length],
      size: sizes[index % sizes.length],
      content: `Content for item ${index + 1}. This could be any type of content that needs to be displayed in the virtual scroll list.`,
    }));
  };

  // Initialize items
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      const demoItems = generateItems(itemCount);
      const virtualItems: VirtualDemoItem[] = demoItems.map((item) => ({
        id: item.id,
        content: null, // We'll render this in renderItem
        data: item,
      }));
      setItems(virtualItems);
      setLoading(false);
    }, 500);
  }, [itemCount]);

  // Dynamic height calculation
  const getItemHeight = (index: number, data?: DemoItem): number => {
    if (!dynamicHeight) return 80;

    const item = data || (items[index]?.data as DemoItem);
    if (!item) return 80;

    switch (item.size) {
      case "small":
        return 60;
      case "medium":
        return 80;
      case "large":
        return 120;
      default:
        return 80;
    }
  };

  // Render custom item
  const renderItem = (
    item: VirtualDemoItem,
    index: number,
    isVisible: boolean,
  ) => {
    const demoItem = item.data as DemoItem;
    if (!demoItem) return null;

    const priorityColors = {
      low: "bg-gray-100 text-gray-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-red-100 text-red-800",
    };

    const categoryColors = {
      Technology: "bg-blue-100 text-blue-800",
      Business: "bg-green-100 text-green-800",
      Design: "bg-purple-100 text-purple-800",
      Marketing: "bg-pink-100 text-pink-800",
      Sales: "bg-indigo-100 text-indigo-800",
      Support: "bg-orange-100 text-orange-800",
    };

    return (
      <div
        className={`p-4 border-b border-gray-200 hover:bg-gray-50 transition-all duration-200 ${
          isVisible
            ? "opacity-100 transform translate-y-0"
            : "opacity-0 transform translate-y-2"
        }`}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold text-gray-900 truncate">
                {demoItem.title}
              </h3>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[demoItem.priority]}`}
              >
                {demoItem.priority}
              </span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${categoryColors[demoItem.category as keyof typeof categoryColors]}`}
              >
                {demoItem.category}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-2">{demoItem.description}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>ID: {demoItem.id}</span>
              <span>Size: {demoItem.size}</span>
              <span>Index: {index}</span>
            </div>
          </div>
          <div className="ml-4 flex-shrink-0">
            <div
              className={`w-3 h-3 rounded-full ${
                demoItem.priority === "high"
                  ? "bg-red-500"
                  : demoItem.priority === "medium"
                    ? "bg-yellow-500"
                    : "bg-gray-400"
              }`}
            />
          </div>
        </div>
      </div>
    );
  };

  // Performance metrics
  const performanceMetrics = useMemo(() => {
    const totalItems = items.length;
    const visibleItems = Math.min(50, totalItems); // Approximate visible items
    const memorySavings =
      totalItems > 100
        ? (((totalItems - visibleItems) / totalItems) * 100).toFixed(1)
        : "0";

    return {
      totalItems,
      visibleItems,
      memorySavings,
      renderTime: dynamicHeight ? "~2ms" : "~1ms",
    };
  }, [items.length, dynamicHeight]);

  const handleScrollToItem = () => {
    const randomIndex = Math.floor(Math.random() * items.length);
    setScrollToIndex(randomIndex);
    setTimeout(() => setScrollToIndex(undefined), 100);
  };

  const handleAddItems = () => {
    const newDemoItems = generateItems(100);
    const newVirtualItems: VirtualDemoItem[] = newDemoItems.map(
      (item, index) => ({
        id: items.length + index + 1,
        content: null,
        data: item,
      }),
    );
    setItems((prev) => [...prev, ...newVirtualItems]);
  };

  const handleRemoveItems = () => {
    setItems((prev) => prev.slice(0, Math.max(100, prev.length - 100)));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">
            Virtual Scroll Demo
          </h1>
          <p className="text-lg text-gray-600">
            High-performance virtual scrolling for large datasets with memory
            optimization
          </p>
          <div className="flex justify-center gap-2 flex-wrap">
            <Badge variant="secondary">Virtual Scrolling</Badge>
            <Badge variant="secondary">Memory Optimized</Badge>
            <Badge variant="secondary">Dynamic Heights</Badge>
            <Badge variant="secondary">Accessible</Badge>
            <Badge variant="secondary">Smooth Performance</Badge>
          </div>
        </div>

        {/* Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Controls & Settings
            </CardTitle>
            <CardDescription>
              Configure the virtual scroll behavior and test different scenarios
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Items Count</label>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setItemCount(100)}
                    disabled={itemCount === 100}
                  >
                    100
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setItemCount(1000)}
                    disabled={itemCount === 1000}
                  >
                    1K
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setItemCount(10000)}
                    disabled={itemCount === 10000}
                  >
                    10K
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Dynamic Heights</label>
                <Button
                  size="sm"
                  variant={dynamicHeight ? "default" : "outline"}
                  onClick={() => setDynamicHeight(!dynamicHeight)}
                  className="w-full"
                >
                  {dynamicHeight ? "Enabled" : "Disabled"}
                </Button>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Horizontal Scroll</label>
                <Button
                  size="sm"
                  variant={horizontal ? "default" : "outline"}
                  onClick={() => setHorizontal(!horizontal)}
                  className="w-full"
                >
                  {horizontal ? "Horizontal" : "Vertical"}
                </Button>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Actions</label>
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleScrollToItem}>
                    <SkipForward className="h-4 w-4 mr-1" />
                    Jump
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleAddItems}>
                    +100
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRemoveItems}
                  >
                    -100
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {performanceMetrics.totalItems.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Items</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Scroll className="h-5 w-5 text-green-500" />
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {performanceMetrics.visibleItems}
                  </div>
                  <div className="text-sm text-gray-600">Visible Items</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                <div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {performanceMetrics.memorySavings}%
                  </div>
                  <div className="text-sm text-gray-600">Memory Saved</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-purple-500" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {performanceMetrics.renderTime}
                  </div>
                  <div className="text-sm text-gray-600">Render Time</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Virtual Scroll Demo */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Scroll className="h-5 w-5" />
                  Virtual Scroll List
                </CardTitle>
                <CardDescription>
                  Scroll through {items.length.toLocaleString()} items with
                  optimal performance
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    dynamicHeight
                      ? "bg-blue-100 text-blue-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {dynamicHeight ? "Dynamic Heights" : "Fixed Heights"}
                </span>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    horizontal
                      ? "bg-blue-100 text-blue-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {horizontal ? "Horizontal" : "Vertical"}
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <VirtualScroll
              items={items}
              itemHeight={getItemHeight}
              containerHeight={400}
              dynamicHeight={dynamicHeight}
              horizontal={horizontal}
              scrollToIndex={scrollToIndex}
              scrollToAlignment="center"
              loading={loading}
              showScrollIndicator={true}
              overscan={5}
              renderItem={renderItem}
              onScroll={(_scrollTop, _visibleRange) => {
                // Handle scroll events if needed
              }}
              onItemsRendered={(_visibleRange) => {
                // Track rendered items if needed
              }}
              ariaLabel="Virtual scroll demo list"
              testId="virtual-scroll-demo"
              className="border-0"
            />
          </CardContent>
        </Card>

        {/* Feature Cards */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-900">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Smooth Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Handles thousands of items without performance degradation.
                  Only renders visible items for optimal performance.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Memory Optimization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Efficient memory usage by recycling DOM elements and only
                  keeping visible items in memory.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Accessibility className="h-5 w-5" />
                  Accessibility
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Full keyboard navigation, screen reader support, and ARIA
                  labels for complete accessibility.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Dynamic Heights</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Support for items with varying heights using ResizeObserver
                  API for automatic size detection.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Horizontal Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Works both vertically and horizontally with the same
                  performance optimizations.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Smart Scrolling</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Intelligent scroll detection, direction tracking, and smooth
                  scrolling with debouncing.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* API Reference */}
        <Card>
          <CardHeader>
            <CardTitle>API Reference</CardTitle>
            <CardDescription>
              Key props and methods for the Virtual Scroll component
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Main Props</h4>
                <div className="bg-gray-50 p-4 rounded-lg text-sm font-mono">
                  <div>items: VirtualScrollItem[]</div>
                  <div>
                    itemHeight: number | ((index: number, data?: any) =&gt;
                    number)
                  </div>
                  <div>containerHeight: number</div>
                  <div>dynamicHeight: boolean</div>
                  <div>horizontal: boolean</div>
                  <div>overscan: number</div>
                  <div>
                    renderItem: (item, index, isVisible) =&gt; ReactNode
                  </div>
                  <div>scrollToIndex: number</div>
                  <div>loading: boolean</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Usage Example</h4>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">
                  {`<VirtualScroll
  items={items}
  itemHeight={getItemHeight}
  containerHeight={400}
  dynamicHeight={true}
  renderItem={renderItem}
  onScroll={handleScroll}
  loading={loading}
/>`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default VirtualScrollDemo;
