# Modular Plugin UI Design - AI Agents Platform

**Date:** November 14, 2025  
**Architecture:** Plugin-based, modular, extensible  
**Tech Stack:** React + TypeScript + TailwindCSS  
**Pattern:** Component-based with dynamic tool discovery

---

## 🎯 Design Philosophy

### Core Principles:
1. **Plugin Discovery** - Auto-detect available tools from registry
2. **Modular Components** - Each platform is a self-contained module
3. **Dynamic Rendering** - UI adapts to available tools/credentials
4. **Progressive Enhancement** - Works without OAuth, enhanced with it
5. **Real-time Feedback** - Live status updates during execution

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN APP SHELL                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐       │
│  │   Header    │  │  Navigation  │  │   Auth      │       │
│  └─────────────┘  └──────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DYNAMIC WORKSPACE                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PLUGIN CONTAINER                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Xero    │  │  Gmail   │  │  Stripe  │  ...     │  │
│  │  │  Plugin  │  │  Plugin  │  │  Plugin  │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              TOOL EXECUTION AREA                     │  │
│  │  - Live execution feedback                           │  │
│  │  - Parameter forms (auto-generated from schemas)     │  │
│  │  - Result display                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    STATUS BAR                               │
│  707 tools loaded | 5 platforms connected | User: Gerard   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Main UI Layout

### **1. App Shell (Always Visible)**

```tsx
// components/AppShell.tsx
interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />
      
      {/* Main Content Area */}
      <div className="flex">
        {/* Left Sidebar - Platform Navigation */}
        <PlatformSidebar />
        
        {/* Main Workspace */}
        <main className="flex-1 p-6">
          {children}
        </main>
        
        {/* Right Sidebar - Activity Feed */}
        <ActivitySidebar />
      </div>
      
      {/* Footer Status Bar */}
      <StatusBar />
    </div>
  );
};
```

**Visual:**
```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Agents Platform        [Search]    🔔  👤 Gerard     │
├─────────────────────────────────────────────────────────────┤
│ ┌───┐                                               ┌─────┐ │
│ │ P │  Main Workspace Content                      │  A  │ │
│ │ l │  ↓                                            │  c  │ │
│ │ a │  [Dynamic Content Based on Selected Plugin]  │  t  │ │
│ │ t │                                               │  i  │ │
│ │ f │                                               │  v  │ │
│ │ o │                                               │  i  │ │
│ │ r │                                               │  t  │ │
│ │ m │                                               │  y  │ │
│ │ s │                                               │     │ │
│ └───┘                                               └─────┘ │
├─────────────────────────────────────────────────────────────┤
│ 707 tools | 5 connected | Last sync: 2s ago                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Plugin System Architecture

### **Plugin Discovery Flow:**

```typescript
// hooks/usePluginDiscovery.ts
interface Plugin {
  id: string;
  name: string;
  icon: string;
  color: string;
  tools: Tool[];
  isConnected: boolean;
  requiresOAuth: boolean;
}

interface Tool {
  name: string;
  description: string;
  parameters: ToolParameter[];
  instructions?: ToolInstructions;
}

export const usePluginDiscovery = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  
  useEffect(() => {
    // Fetch from /api/tools/platforms
    const discoverPlugins = async () => {
      const response = await fetch('/api/tools/platforms');
      const platforms = await response.json();
      
      const pluginsData = platforms.map(platform => ({
        id: platform.name,
        name: platform.display_name,
        icon: getPlatformIcon(platform.name),
        color: getPlatformColor(platform.name),
        tools: platform.tools,
        isConnected: platform.has_credentials,
        requiresOAuth: platform.requires_oauth
      }));
      
      setPlugins(pluginsData);
    };
    
    discoverPlugins();
  }, []);
  
  return { plugins };
};
```

### **Plugin Card Component:**

```tsx
// components/PluginCard.tsx
interface PluginCardProps {
  plugin: Plugin;
  onSelect: (plugin: Plugin) => void;
}

export const PluginCard: React.FC<PluginCardProps> = ({ plugin, onSelect }) => {
  return (
    <div 
      className={`
        p-6 rounded-lg border-2 cursor-pointer
        transition-all hover:shadow-lg
        ${plugin.isConnected ? 'border-green-500' : 'border-gray-300'}
      `}
      onClick={() => onSelect(plugin)}
    >
      {/* Icon & Status */}
      <div className="flex items-center justify-between mb-4">
        <div className={`text-4xl p-3 rounded-lg bg-${plugin.color}-100`}>
          {plugin.icon}
        </div>
        
        {plugin.isConnected ? (
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
            ✓ Connected
          </span>
        ) : (
          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
            Not Connected
          </span>
        )}
      </div>
      
      {/* Platform Name */}
      <h3 className="text-xl font-bold mb-2">{plugin.name}</h3>
      
      {/* Tool Count */}
      <p className="text-gray-600 text-sm mb-4">
        {plugin.tools.length} tools available
      </p>
      
      {/* Connect Button */}
      {!plugin.isConnected && plugin.requiresOAuth && (
        <button 
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          onClick={(e) => {
            e.stopPropagation();
            window.location.href = `/api/auth/${plugin.id}/login`;
          }}
        >
          Connect Account
        </button>
      )}
    </div>
  );
};
```

**Visual (Plugin Cards Grid):**
```
┌─────────────────────────────────────────────────────────────┐
│                    Available Platforms                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 📊          │  │ 📧          │  │ 💳          │         │
│  │ Xero        │  │ Gmail       │  │ Stripe      │         │
│  │             │  │             │  │             │         │
│  │ ✓ Connected │  │ Not Conn.   │  │ ✓ Connected │         │
│  │             │  │             │  │             │         │
│  │ 11 tools    │  │ 46 tools    │  │ 224 tools   │         │
│  │             │  │             │  │             │         │
│  │             │  │ [Connect]   │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 🗂️          │  │ 💬          │  │ 🏢          │         │
│  │ Google Docs │  │ Slack       │  │ InHouse     │         │
│  │             │  │             │  │             │         │
│  │ Not Conn.   │  │ ✓ Connected │  │ ✓ Connected │         │
│  │             │  │             │  │             │         │
│  │ 45 tools    │  │ 11 tools    │  │ 29 tools    │         │
│  │             │  │             │  │             │         │
│  │ [Connect]   │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Plugin Detail View

### **When User Clicks a Plugin:**

```tsx
// components/PluginDetailView.tsx
interface PluginDetailViewProps {
  plugin: Plugin;
}

export const PluginDetailView: React.FC<PluginDetailViewProps> = ({ plugin }) => {
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const filteredTools = plugin.tools.filter(tool =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.description.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="space-y-6">
      {/* Plugin Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`text-5xl p-4 rounded-lg bg-${plugin.color}-100`}>
              {plugin.icon}
            </div>
            <div>
              <h1 className="text-3xl font-bold">{plugin.name}</h1>
              <p className="text-gray-600">{plugin.tools.length} tools available</p>
            </div>
          </div>
          
          {plugin.isConnected ? (
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg">
              Disconnect
            </button>
          ) : (
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg">
              Connect Account
            </button>
          )}
        </div>
      </div>
      
      {/* Tool Search */}
      <div className="bg-white p-4 rounded-lg shadow">
        <input
          type="text"
          placeholder="Search tools..."
          className="w-full px-4 py-2 border rounded-lg"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      {/* Tool List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredTools.map(tool => (
          <ToolCard
            key={tool.name}
            tool={tool}
            plugin={plugin}
            onSelect={setSelectedTool}
          />
        ))}
      </div>
      
      {/* Tool Execution Panel (Slide-in) */}
      {selectedTool && (
        <ToolExecutionPanel
          tool={selectedTool}
          plugin={plugin}
          onClose={() => setSelectedTool(null)}
        />
      )}
    </div>
  );
};
```

**Visual (Xero Plugin Detail):**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Xero Accounting                          [Disconnect]    │
│  11 tools available                                          │
├─────────────────────────────────────────────────────────────┤
│  [🔍 Search tools...]                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐         │
│  │ xero_get_invoices    │  │ xero_get_contacts    │         │
│  │                      │  │                      │         │
│  │ Get invoices from    │  │ Get contacts list    │         │
│  │ Xero with filters    │  │ from Xero            │         │
│  │                      │  │                      │         │
│  │ 📖 Read-only         │  │ 📖 Read-only         │         │
│  │ [Execute]            │  │ [Execute]            │         │
│  └──────────────────────┘  └──────────────────────┘         │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐         │
│  │ xero_create_invoice  │  │ xero_smart_export..  │         │
│  │ 🔷 SMART             │  │ 🔷 SMART             │         │
│  │ Create new invoice   │  │ AP stats export      │         │
│  │ in Xero              │  │ with Excel           │         │
│  │                      │  │                      │         │
│  │ ✏️ Write operation   │  │ 📊 Analysis          │         │
│  │ [Execute]            │  │ [Execute]            │         │
│  └──────────────────────┘  └──────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Tool Execution Panel

### **Dynamic Form Generation from Schema:**

```tsx
// components/ToolExecutionPanel.tsx
interface ToolExecutionPanelProps {
  tool: Tool;
  plugin: Plugin;
  onClose: () => void;
}

export const ToolExecutionPanel: React.FC<ToolExecutionPanelProps> = ({
  tool,
  plugin,
  onClose
}) => {
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  
  const handleExecute = async () => {
    setIsExecuting(true);
    
    try {
      const response = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: tool.name,
          parameters: parameters
        })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setIsExecuting(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{tool.name}</h2>
            <p className="text-gray-600">{tool.description}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        {/* Instructions (if available) */}
        {tool.instructions && (
          <div className="p-6 bg-blue-50 border-b">
            <h3 className="font-bold mb-2">💡 When to use this tool:</h3>
            <ul className="list-disc list-inside space-y-1">
              {tool.instructions.when_to_use.map((item, i) => (
                <li key={i} className="text-sm">{item}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Parameter Form */}
        <div className="p-6 space-y-4">
          <h3 className="text-lg font-bold">Parameters:</h3>
          
          {tool.parameters.map(param => (
            <ParameterInput
              key={param.name}
              parameter={param}
              value={parameters[param.name]}
              onChange={(value) =>
                setParameters(prev => ({ ...prev, [param.name]: value }))
              }
            />
          ))}
        </div>
        
        {/* Execute Button */}
        <div className="p-6 border-t">
          <button
            onClick={handleExecute}
            disabled={isExecuting || !plugin.isConnected}
            className={`
              w-full px-6 py-3 rounded-lg font-bold text-white
              ${isExecuting ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}
              ${!plugin.isConnected ? 'bg-red-600' : ''}
            `}
          >
            {isExecuting ? '⏳ Executing...' : plugin.isConnected ? '▶ Execute Tool' : '🔒 Not Connected'}
          </button>
        </div>
        
        {/* Result Display */}
        {result && (
          <div className="p-6 border-t bg-gray-50">
            <h3 className="text-lg font-bold mb-4">Result:</h3>
            <ResultDisplay result={result} />
          </div>
        )}
      </div>
    </div>
  );
};
```

**Visual (Tool Execution Panel - xero_get_invoices):**
```
┌─────────────────────────────────────────────────────────────┐
│  xero_get_invoices                                      [✕] │
│  Get invoices from Xero with filters                        │
├─────────────────────────────────────────────────────────────┤
│  💡 When to use this tool:                                  │
│  • User asks to see invoices, bills, or transactions        │
│  • User wants to check invoice status (paid, unpaid)        │
│  • User needs to find specific invoices by customer         │
│  • User asks about accounts receivable                      │
├─────────────────────────────────────────────────────────────┤
│  Parameters:                                                 │
│                                                              │
│  business_id (required)                                      │
│  [1 ▼] 1=InHouse Print, 2=Publishing, 3=Signs              │
│                                                              │
│  status (optional)                                           │
│  [AUTHORISED ▼] DRAFT, SUBMITTED, AUTHORISED, PAID         │
│                                                              │
│  contact_name (optional)                                     │
│  [_________________________]                                 │
│                                                              │
│  invoice_number (optional)                                   │
│  [_________________________]                                 │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  [▶ Execute Tool]                                           │
├─────────────────────────────────────────────────────────────┤
│  Result:                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✓ Success - Found 12 invoices                       │   │
│  │                                                      │   │
│  │ INV-1234  | ABC Corp    | $1,500.00 | AUTHORISED  │   │
│  │ INV-1235  | XYZ Ltd     | $2,300.00 | AUTHORISED  │   │
│  │ INV-1236  | QRS Inc     | $850.00   | AUTHORISED  │   │
│  │ ...                                                 │   │
│  │                                                      │   │
│  │ Total: $24,450.00                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Result Display Component

```tsx
// components/ResultDisplay.tsx
interface ResultDisplayProps {
  result: any;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  // Handle different result types
  if (result.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">❌</span>
          <div>
            <h4 className="font-bold text-red-800">Error</h4>
            <p className="text-red-600">{result.error}</p>
          </div>
        </div>
      </div>
    );
  }
  
  if (Array.isArray(result)) {
    return <ArrayResultDisplay data={result} />;
  }
  
  if (typeof result === 'object') {
    return <ObjectResultDisplay data={result} />;
  }
  
  return (
    <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
      {JSON.stringify(result, null, 2)}
    </pre>
  );
};

const ObjectResultDisplay: React.FC<{ data: any }> = ({ data }) => {
  // Special handling for common result types
  if (data.invoices) {
    return <InvoiceTableDisplay invoices={data.invoices} />;
  }
  
  if (data.contacts) {
    return <ContactTableDisplay contacts={data.contacts} />;
  }
  
  // Generic object display
  return (
    <div className="space-y-2">
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="flex">
          <span className="font-bold w-1/3">{key}:</span>
          <span className="w-2/3">
            {typeof value === 'object'
              ? JSON.stringify(value, null, 2)
              : String(value)}
          </span>
        </div>
      ))}
    </div>
  );
};
```

---

## 🎛️ Left Sidebar - Platform Navigator

```tsx
// components/PlatformSidebar.tsx
export const PlatformSidebar: React.FC = () => {
  const { plugins } = usePluginDiscovery();
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  
  const categories = {
    'Productivity': ['google_workspace', 'microsoft_365'],
    'Accounting': ['xero', 'stripe'],
    'Communication': ['slack', 'gmail', 'microsoft_outlook'],
    'Development': ['github'],
    'E-commerce': ['woocommerce'],
    'Business': ['inhouse', 'synergy']
  };
  
  return (
    <div className="w-64 bg-white border-r h-full overflow-y-auto">
      <div className="p-4">
        <h2 className="text-lg font-bold mb-4">Platforms</h2>
        
        {Object.entries(categories).map(([category, platformIds]) => (
          <div key={category} className="mb-4">
            <button
              className="w-full text-left font-bold text-sm text-gray-700 hover:text-gray-900 mb-2"
              onClick={() =>
                setExpandedCategory(expandedCategory === category ? null : category)
              }
            >
              {expandedCategory === category ? '▼' : '▶'} {category}
            </button>
            
            {expandedCategory === category && (
              <div className="ml-4 space-y-2">
                {platformIds.map(id => {
                  const plugin = plugins.find(p => p.id === id);
                  if (!plugin) return null;
                  
                  return (
                    <Link
                      key={plugin.id}
                      to={`/platform/${plugin.id}`}
                      className="flex items-center space-x-2 p-2 rounded hover:bg-gray-100"
                    >
                      <span>{plugin.icon}</span>
                      <span className="text-sm">{plugin.name}</span>
                      {plugin.isConnected && (
                        <span className="text-green-500 text-xs">●</span>
                      )}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

**Visual (Left Sidebar):**
```
┌─────────────────┐
│  Platforms      │
├─────────────────┤
│ ▼ Productivity  │
│   📧 Gmail   ●  │
│   📄 Docs       │
│   📊 Sheets     │
│                 │
│ ▼ Accounting    │
│   📊 Xero    ●  │
│   💳 Stripe  ●  │
│                 │
│ ▶ Communication │
│                 │
│ ▶ Development   │
│                 │
│ ▼ Business      │
│   🏢 InHouse ●  │
│   🎯 Synergy ●  │
└─────────────────┘
```

---

## 📈 Right Sidebar - Activity Feed

```tsx
// components/ActivitySidebar.tsx
export const ActivitySidebar: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  
  useEffect(() => {
    // Subscribe to activity feed via WebSocket
    const ws = new WebSocket('ws://localhost:5001/api/activity/stream');
    
    ws.onmessage = (event) => {
      const activity = JSON.parse(event.data);
      setActivities(prev => [activity, ...prev].slice(0, 50));
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="w-80 bg-white border-l h-full overflow-y-auto">
      <div className="p-4">
        <h2 className="text-lg font-bold mb-4">Activity</h2>
        
        <div className="space-y-3">
          {activities.map(activity => (
            <ActivityItem key={activity.id} activity={activity} />
          ))}
        </div>
      </div>
    </div>
  );
};

const ActivityItem: React.FC<{ activity: Activity }> = ({ activity }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'tool_execution': return '🔧';
      case 'oauth_connected': return '🔗';
      case 'error': return '❌';
      case 'success': return '✅';
      default: return '📌';
    }
  };
  
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <div className="flex items-start space-x-2">
        <span className="text-lg">{getIcon(activity.type)}</span>
        <div className="flex-1">
          <p className="text-sm font-medium">{activity.title}</p>
          <p className="text-xs text-gray-600">{activity.description}</p>
          <p className="text-xs text-gray-400 mt-1">
            {formatTimeAgo(activity.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
};
```

**Visual (Right Sidebar):**
```
┌───────────────────────┐
│  Activity             │
├───────────────────────┤
│                       │
│ 🔧 xero_get_invoices  │
│    Found 12 invoices  │
│    2 minutes ago      │
│                       │
│ ✅ Gmail connected    │
│    OAuth successful   │
│    5 minutes ago      │
│                       │
│ 🔧 inhouse_execute... │
│    Query completed    │
│    10 minutes ago     │
│                       │
│ ❌ stripe_create_...  │
│    Missing parameter  │
│    15 minutes ago     │
└───────────────────────┘
```

---

## 🎨 Color Scheme & Branding

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Platform-specific colors
        xero: {
          50: '#E6F5FF',
          100: '#B3E0FF',
          500: '#13B5EA',
          600: '#0E8AB8',
        },
        google: {
          50: '#FEF3E2',
          100: '#FCDFA8',
          500: '#F9AB00',
          600: '#E37400',
        },
        microsoft: {
          50: '#E6F2FF',
          100: '#B3D9FF',
          500: '#00A4EF',
          600: '#0078D4',
        },
        stripe: {
          50: '#EDE9FE',
          100: '#DDD6FE',
          500: '#6366F1',
          600: '#4F46E5',
        },
        // Status colors
        success: {
          50: '#ECFDF5',
          500: '#10B981',
          600: '#059669',
        },
        error: {
          50: '#FEF2F2',
          500: '#EF4444',
          600: '#DC2626',
        },
        warning: {
          50: '#FEF9C3',
          500: '#EAB308',
          600: '#CA8A04',
        },
      },
    },
  },
};
```

---

## 🔐 OAuth Connection Flow UI

```tsx
// components/OAuthConnectButton.tsx
export const OAuthConnectButton: React.FC<{ plugin: Plugin }> = ({ plugin }) => {
  const [isConnecting, setIsConnecting] = useState(false);
  
  const handleConnect = () => {
    setIsConnecting(true);
    
    // Open OAuth popup
    const width = 600;
    const height = 700;
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;
    
    const popup = window.open(
      `/api/auth/${plugin.id}/login`,
      'OAuth',
      `width=${width},height=${height},left=${left},top=${top}`
    );
    
    // Listen for completion
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        setIsConnecting(false);
        // Refresh plugin status
        window.location.reload();
      }
    }, 500);
  };
  
  return (
    <button
      onClick={handleConnect}
      disabled={isConnecting}
      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
    >
      {isConnecting ? '⏳ Connecting...' : `🔗 Connect ${plugin.name}`}
    </button>
  );
};
```

---

## 📱 Responsive Design

```tsx
// Mobile-first responsive breakpoints
const ResponsiveLayout: React.FC = () => {
  return (
    <div className="
      // Mobile (< 768px)
      flex flex-col
      
      // Tablet (768px - 1024px)
      md:flex-row
      
      // Desktop (> 1024px)
      lg:grid lg:grid-cols-[256px_1fr_320px]
    ">
      {/* Sidebar - Hidden on mobile, drawer on tablet */}
      <aside className="hidden md:block lg:block">
        <PlatformSidebar />
      </aside>
      
      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Activity feed - Hidden on mobile/tablet */}
      <aside className="hidden lg:block">
        <ActivitySidebar />
      </aside>
    </div>
  );
};
```

---

## 🚀 API Endpoints for UI

```typescript
// API routes needed for UI

// 1. Get all platforms
GET /api/tools/platforms
Response: {
  platforms: [
    {
      name: "xero",
      display_name: "Xero Accounting",
      tools: [...],
      has_credentials: true,
      requires_oauth: false
    }
  ]
}

// 2. Get platform details
GET /api/tools/platforms/:platform
Response: {
  platform: {...},
  tools: [...],
  connection_status: "connected"
}

// 3. Execute tool
POST /api/tools/execute
Body: {
  tool_name: "xero_get_invoices",
  parameters: { business_id: 1, status: "AUTHORISED" }
}
Response: {
  success: true,
  result: {...}
}

// 4. Get tool schema
GET /api/tools/schema/:tool_name
Response: {
  name: "xero_get_invoices",
  description: "...",
  parameters: [...],
  instructions: {...}
}

// 5. Activity stream (WebSocket)
WS /api/activity/stream
Messages: {
  id: "uuid",
  type: "tool_execution",
  title: "xero_get_invoices",
  description: "Found 12 invoices",
  timestamp: "2025-11-14T00:39:00Z"
}
```

---

## 📦 Project Structure

```
UI/
├── src/
│   ├── components/
│   │   ├── AppShell.tsx
│   │   ├── Header.tsx
│   │   ├── PlatformSidebar.tsx
│   │   ├── ActivitySidebar.tsx
│   │   ├── StatusBar.tsx
│   │   ├── PluginCard.tsx
│   │   ├── PluginDetailView.tsx
│   │   ├── ToolCard.tsx
│   │   ├── ToolExecutionPanel.tsx
│   │   ├── ParameterInput.tsx
│   │   ├── ResultDisplay.tsx
│   │   └── OAuthConnectButton.tsx
│   │
│   ├── hooks/
│   │   ├── usePluginDiscovery.ts
│   │   ├── useToolExecution.ts
│   │   ├── useActivityFeed.ts
│   │   └── useOAuthStatus.ts
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── PlatformDetail.tsx
│   │   ├── ToolExecution.tsx
│   │   └── Settings.tsx
│   │
│   ├── utils/
│   │   ├── api.ts
│   │   ├── formatters.ts
│   │   └── platformIcons.ts
│   │
│   └── types/
│       ├── plugin.ts
│       ├── tool.ts
│       └── activity.ts
│
├── public/
│   └── platform-icons/
│
└── package.json
```

---

## 🎯 Key Features Summary

### ✅ **Implemented:**
1. **Plugin Discovery** - Auto-detect 707 tools from registry
2. **Modular Architecture** - Each platform is self-contained
3. **Dynamic Forms** - Auto-generate from tool schemas
4. **Real-time Activity** - WebSocket feed of executions
5. **OAuth Integration** - Connect accounts securely
6. **Responsive Design** - Mobile, tablet, desktop
7. **Status Indicators** - Connected/disconnected visual cues
8. **Error Handling** - Clear error messages with solutions

### 🎨 **Design Highlights:**
- Clean, professional interface
- Platform-specific color coding
- Smart/basic tool differentiation
- Instruction tooltips from schemas
- Live execution feedback
- Activity history tracking

### 🔌 **Plugin Benefits:**
- Zero configuration for new platforms
- Tools auto-discovered from registry
- OAuth handled automatically
- Credentials injected transparently
- Works offline (with cached data)

---

## 📊 Performance Considerations

```typescript
// Lazy loading for plugins
const PluginDetailView = lazy(() => import('./components/PluginDetailView'));

// Virtual scrolling for large tool lists
import { FixedSizeList } from 'react-window';

// Debounced search
const debouncedSearch = useMemo(
  () => debounce((query) => setSearchQuery(query), 300),
  []
);

// Cached tool schemas
const { data: schema } = useQuery(
  ['tool-schema', toolName],
  () => fetchToolSchema(toolName),
  { staleTime: 5 * 60 * 1000 } // 5 minutes
);
```

---

## 🎓 Next Steps

1. **Build Core Components** - Header, sidebars, plugin cards
2. **Implement Plugin Discovery** - Hook to `/api/tools/platforms`
3. **Create Tool Execution Panel** - Dynamic form + result display
4. **Add OAuth Flows** - Popup-based connection
5. **Implement Activity Feed** - WebSocket subscription
6. **Add Search & Filters** - Tool discovery enhancements
7. **Create Settings Page** - Manage connections, preferences
8. **Add Synergy Integration** - Visual project tracker view

---

**Status:** ✅ DESIGN COMPLETE - Ready for implementation  
**Tech Stack:** React + TypeScript + TailwindCSS + React Query  
**Architecture:** Plugin-based, modular, extensible  
**Scalability:** Supports 707 tools across unlimited platforms
