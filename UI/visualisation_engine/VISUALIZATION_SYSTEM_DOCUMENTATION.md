# Visualization System Architecture Documentation

**Date:** November 15, 2025  
**Purpose:** Complete guide to understanding how streamingTwoRule.js and visualisation_copy.js work together  
**Use Case:** Integrating visualization rendering into Tiptap document containers

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Pattern](#architecture-pattern)
3. [File Responsibilities](#file-responsibilities)
4. [Integration Flow](#integration-flow)
5. [Tiptap Integration Guide](#tiptap-integration-guide)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)

---

## System Overview

The visualization system consists of **two complementary files** that work together to render mixed content (text + visualizations) in real-time streaming scenarios:

### streamingTwoRule.js (107 KB, 2,545 lines)
**Role:** Content Parser & Stream Controller  
**Responsibility:** Parse incoming AI content streams, classify content as markdown or visualization, manage rendering lifecycle

### visualisation_copy.js (404 KB, 9,641 lines)
**Role:** Visualization Rendering Engine  
**Responsibility:** Actually render visualizations (Mermaid, Plotly, etc.) with proper styling, export, and interactive features

### Relationship
```
AI Stream → streamingTwoRule.js → visualisation_copy.js → Rendered Output
           (Parser/Controller)      (Rendering Engine)
```

---

## Architecture Pattern

### Two-Rule Streaming System (streamingTwoRule.js)

**Core Principle:** BLACK AND WHITE content classification

#### Rule 1: Content Cannot Belong to Both Groups
Any buffered content is EITHER:
- **Type 1 (Markdown):** Regular text, headings, lists, tables, formatted text
- **Type 2 (Visual):** Mermaid diagrams, Plotly charts, code blocks with visualization delimiters

#### Rule 2: Once Delimiter Detected, ALL Content is Visual Until END Delimiter
When `<visualization>` or similar delimiter is found, everything until `</visualization>` is treated as visual content.

### Flow Diagram
```
Stream Input
    ↓
Raw Buffer (append-only)
    ↓
Content Parser (state machine)
    ↓
Package Creation (markdown or visual)
    ↓
Controlled Release (ordered rendering)
    ↓
UI Append (never re-render existing content)
```

### State Machine
```javascript
States:
- NORMAL: Parsing regular markdown content
- BUFFERING_VISUAL: Accumulating visual content between delimiters

Transitions:
NORMAL → BUFFERING_VISUAL: When delimiter detected
BUFFERING_VISUAL → NORMAL: When end delimiter found
```

---

## File Responsibilities

### streamingTwoRule.js

#### Primary Classes

**1. TwoRuleStreamProcessor**
```javascript
class TwoRuleStreamProcessor {
    constructor(container)  // Initialize with target DOM container
    
    // Core Methods
    async processChunk(newContent)       // Process incoming stream chunks
    forceFlush()                         // Force release buffered content
    async releaseReadyPackages()         // Release completed packages
    async renderPackage(pkg)             // Render individual package
    async renderVisualization(type, content, container)  // Route to viz engine
    
    // Package Management
    packageMarkdownContent(content, startPosition)
    packageVisualContent(content, type)
    
    // State Management
    parseNormalState()
    parseBufferingState()
}
```

**Key Features:**
- **Delimiter Detection:** Recognizes `<visualization>`, `<mermaid>`, `<plotly>`, etc.
- **Position Tracking:** Maintains stream position for ordered rendering
- **Deduplication:** Uses content hashing to prevent duplicate renders
- **Code Fence Safety:** Won't flush incomplete code blocks
- **Markdown Container Management:** Creates/reuses containers for text content
- **Append-Only Rendering:** Never re-renders existing content

#### Global State
```javascript
let globalTwoRuleProcessor = null;        // Singleton instance
let streamingMessageElement = null;        // Current message container
let streamingState = {
    isFirstContent: true,
    lastProcessedLength: 0,
    renderedComponents: [],
    lastActivityTs: 0
};
```

#### Helper Functions
```javascript
removeAllThinkingIndicators(container)    // Clean up loading indicators
cleanMarkdownHTML(html)                   // Legacy HTML cleaning
```

---

### visualisation_copy.js

#### Primary Classes

**1. MermaidFontController**
```javascript
class MermaidFontController {
    constructor()
    
    // Font Size Management
    setFontSize(container, sizeName)      // Apply font size preset
    increaseFontSize(container)           // Increase by one step
    decreaseFontSize(container)           // Decrease by one step
    getCurrentSize(container)             // Get current size name
    
    // User Preferences
    saveUserPreference(sizeName)
    loadUserPreference()
    applyUserPreference(container)
}
```

**Available Font Sizes:**
- tiny (10px, scale 0.8)
- small (12px, scale 0.9)
- normal (14px, scale 1.0) - default
- medium (16px, scale 1.1)
- large (18px, scale 1.2)
- huge (22px, scale 1.4)
- giant (26px, scale 1.6)

**2. VisualizationEngine**
```javascript
class VisualizationEngine {
    constructor()
    async init()                          // Initialize libraries (Mermaid, Plotly)
    
    // Rendering Methods
    async renderVisualizationDirectly(item, container, chartId)
    async renderVisualization(item, container, chartId)
    async renderMermaidDirectly(item, container, chartId)
    async renderPlotlyDirectly(item, container, chartId)
    
    // Container Management
    createVisualizationContainer(type)    // Create styled wrapper
    
    // Export Functions
    async exportToSVG(containerId)
    async exportToPNG(containerId)
    async exportToHTML(containerId)
    async exportToMarkdown(containerId)
    
    // Theme Management
    getMermaidTheme()
    applyTheme(theme)
}
```

**Key Features:**
- **Mermaid Rendering:** Flowcharts, sequence diagrams, Gantt charts, etc.
- **Plotly Rendering:** Interactive charts with zoom, pan, hover
- **Export Support:** SVG, PNG, HTML, Markdown formats
- **Theme Support:** Light/dark mode integration
- **Font Control:** Per-diagram font size adjustment
- **Responsive Design:** Auto-resize on window changes
- **HTML Formatting:** Support for bold, italic, code in Mermaid labels

#### Export Utilities
```javascript
window.MermaidExportCSS()                 // Get export-specific CSS
embedStyleIntoSvg(svgEl, cssText)        // Embed CSS in SVG for export
stripBreaksAroundBullets(root)           // Clean up bullet formatting
hardenSvgForExport(svgEl, options)       // Normalize SVG for export
```

---

## Integration Flow

### Step-by-Step Process

#### 1. Initialization
```javascript
// Create processor instance
const processor = new TwoRuleStreamProcessor(containerElement);

// Initialize visualization engine (if not already global)
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}
```

#### 2. Stream Processing
```javascript
// As AI content arrives in chunks
processor.processChunk(newContentChunk);

// On stream complete
processor.forceFlush();
```

#### 3. Content Classification
**streamingTwoRule.js automatically:**
- Detects delimiters (`<mermaid>`, `<plotly>`, etc.)
- Classifies content as markdown or visual
- Creates packages with metadata (position, type, content)
- Queues packages for ordered release

#### 4. Package Release
**streamingTwoRule.js:**
- Releases packages in stream order
- Creates visualization containers with proper structure
- Routes visual packages to visualization engine

#### 5. Visualization Rendering
**visualisation_copy.js:**
- Receives visualization request with type, content, container
- Applies font preferences
- Renders using appropriate library (Mermaid/Plotly)
- Adds interactive controls (export, font size, etc.)
- Returns rendered visualization in container

---

## Tiptap Integration Guide

### Overview
To render AI-generated content (markdown + visualizations) inside a Tiptap editor, you need to:
1. Extract content from Tiptap editor
2. Process through streamingTwoRule.js
3. Render visualizations via visualisation_copy.js
4. Insert results back into Tiptap

### Integration Pattern

#### Option 1: Real-Time Streaming (AI Response)

```javascript
// 1. Create processor for Tiptap content area
const tiptapContainer = document.querySelector('.tiptap-content-area');
const processor = new TwoRuleStreamProcessor(tiptapContainer);

// 2. Initialize viz engine
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}

// 3. Process AI stream as it arrives
aiStream.on('data', (chunk) => {
    processor.processChunk(chunk);
});

aiStream.on('end', () => {
    processor.forceFlush();
});
```

#### Option 2: Static Content Rendering (Existing Document)

```javascript
// 1. Extract content from Tiptap
const tiptapContent = editor.getHTML(); // or editor.getText()

// 2. Create temporary container
const tempContainer = document.createElement('div');
const processor = new TwoRuleStreamProcessor(tempContainer);

// 3. Process entire content at once
await processor.processChunk(tiptapContent);
await processor.forceFlush();

// 4. Wait for all rendering to complete
await new Promise(resolve => setTimeout(resolve, 500));

// 5. Extract rendered visualizations
const visualizations = tempContainer.querySelectorAll('.viz-container');

// 6. Insert into Tiptap at appropriate positions
visualizations.forEach(viz => {
    const position = parseInt(viz.getAttribute('data-stream-position'));
    editor.commands.insertContentAt(position, viz.outerHTML);
});
```

#### Option 3: Custom Node Extension (Recommended)

Create a custom Tiptap node for visualizations:

```javascript
import { Node } from '@tiptap/core';
import { VueNodeViewRenderer } from '@tiptap/vue-3';
import VisualizationNodeView from './VisualizationNodeView.vue';

export const VisualizationNode = Node.create({
    name: 'visualization',
    
    group: 'block',
    
    atom: true, // Don't allow editing
    
    addAttributes() {
        return {
            type: { default: 'mermaid' },
            content: { default: '' },
            chartId: { default: null }
        };
    },
    
    parseHTML() {
        return [{ tag: 'div.viz-container' }];
    },
    
    renderHTML({ node, HTMLAttributes }) {
        return ['div', { class: 'viz-container', ...HTMLAttributes }];
    },
    
    addNodeView() {
        return VueNodeViewRenderer(VisualizationNodeView);
    }
});
```

**VisualizationNodeView.vue:**
```vue
<template>
    <div ref="vizContainer" class="viz-node-wrapper">
        <!-- Visualization renders here -->
    </div>
</template>

<script>
export default {
    props: ['node'],
    
    async mounted() {
        // Initialize viz engine if needed
        if (!window.vizEngine) {
            window.vizEngine = new VisualizationEngine();
            await window.vizEngine.init();
        }
        
        // Render visualization
        const item = {
            type: this.node.attrs.type,
            content: this.node.attrs.content
        };
        
        await window.vizEngine.renderVisualizationDirectly(
            item,
            this.$refs.vizContainer,
            this.node.attrs.chartId || `viz-${Date.now()}`
        );
    }
};
</script>
```

**Using the extension:**
```javascript
import { Editor } from '@tiptap/core';
import { VisualizationNode } from './VisualizationNode';

const editor = new Editor({
    extensions: [
        // ... other extensions
        VisualizationNode
    ],
    content: `
        <p>Here's a diagram:</p>
        <div class="viz-container" 
             data-type="mermaid" 
             data-content="graph LR\nA-->B">
        </div>
    `
});
```

### Content Extraction Patterns

#### From AI Stream to Tiptap

```javascript
class TiptapStreamIntegration {
    constructor(editor) {
        this.editor = editor;
        this.processor = null;
        this.currentPosition = 0;
    }
    
    async startStream() {
        // Create processor with temp container
        const tempContainer = document.createElement('div');
        this.processor = new TwoRuleStreamProcessor(tempContainer);
        
        // Store reference to editor position
        this.currentPosition = this.editor.state.doc.content.size;
    }
    
    async processChunk(chunk) {
        await this.processor.processChunk(chunk);
        
        // Extract newly rendered content
        const renderedContent = this.extractNewContent();
        
        // Insert into Tiptap at current position
        if (renderedContent) {
            this.editor.commands.insertContentAt(
                this.currentPosition,
                renderedContent
            );
            this.currentPosition += renderedContent.length;
        }
    }
    
    async endStream() {
        await this.processor.forceFlush();
        
        // Final content extraction
        const finalContent = this.extractNewContent();
        if (finalContent) {
            this.editor.commands.insertContentAt(
                this.currentPosition,
                finalContent
            );
        }
    }
    
    extractNewContent() {
        // Extract HTML from processor container
        const container = this.processor.container;
        
        // Get markdown content
        const markdownElements = container.querySelectorAll('.two-rule-markdown-content');
        
        // Get visualization containers
        const vizElements = container.querySelectorAll('.viz-container');
        
        // Build ordered content array
        const allElements = [...markdownElements, ...vizElements]
            .sort((a, b) => {
                const posA = parseInt(a.getAttribute('data-stream-position') || '0');
                const posB = parseInt(b.getAttribute('data-stream-position') || '0');
                return posA - posB;
            });
        
        // Convert to Tiptap JSON or HTML
        return allElements.map(el => el.outerHTML).join('');
    }
}

// Usage
const integration = new TiptapStreamIntegration(editor);
await integration.startStream();

aiStream.on('data', chunk => integration.processChunk(chunk));
aiStream.on('end', () => integration.endStream());
```

---

## API Reference

### streamingTwoRule.js API

#### TwoRuleStreamProcessor

**Constructor:**
```javascript
new TwoRuleStreamProcessor(container: HTMLElement)
```

**Methods:**

```javascript
// Process incoming stream chunk
async processChunk(newContent: string): Promise<void>

// Force flush buffered content
forceFlush(): void

// Release packages that are ready to render
async releaseReadyPackages(): Promise<void>

// Render a specific package
async renderPackage(pkg: Package): Promise<void>

// Route visualization to engine
async renderVisualization(
    type: string,           // 'mermaid', 'plotly', etc.
    content: string,        // Visualization code/data
    container: HTMLElement  // Target container
): Promise<void>

// Get processing statistics
getStats(): {
    chunksProcessed: number,
    totalProcessingTime: number,
    markdownPackages: number,
    visualPackages: number,
    packagesReleased: number
}
```

**Package Structure:**
```javascript
{
    id: number,               // Unique package ID
    type: 'markdown' | 'visual',
    subType?: string,         // For visual: 'mermaid', 'plotly'
    content: string,          // Actual content
    contentHash: string,      // Deduplication hash
    position: number,         // Stream position
    ready: boolean,           // Ready to render?
    timestamp: number         // Creation time
}
```

---

### visualisation_copy.js API

#### VisualizationEngine

**Constructor:**
```javascript
new VisualizationEngine()
```

**Initialization:**
```javascript
async init(): Promise<void>  // Initialize Mermaid, Plotly, etc.
```

**Rendering Methods:**
```javascript
// Main rendering method
async renderVisualizationDirectly(
    item: {
        type: string,      // 'mermaid', 'plotly', etc.
        content: string    // Visualization code
    },
    container: HTMLElement,
    chartId: string
): Promise<void>

// Mermaid-specific
async renderMermaidDirectly(
    item: { type: string, content: string },
    container: HTMLElement,
    chartId: string
): Promise<void>

// Plotly-specific
async renderPlotlyDirectly(
    item: { type: string, content: string },
    container: HTMLElement,
    chartId: string
): Promise<void>
```

**Container Creation:**
```javascript
createVisualizationContainer(type: string): HTMLElement
// Returns a styled container with:
// - .viz-container wrapper
// - .viz-header with title/controls
// - .viz-content-area for actual rendering
// - .viz-footer with metadata
```

**Export Methods:**
```javascript
async exportToSVG(containerId: string): Promise<void>
async exportToPNG(containerId: string): Promise<void>
async exportToHTML(containerId: string): Promise<void>
async exportToMarkdown(containerId: string): Promise<void>
```

**Theme Management:**
```javascript
getMermaidTheme(): string  // 'default' or 'dark'
applyTheme(theme: 'light' | 'dark'): void
```

#### MermaidFontController

```javascript
const fontController = new MermaidFontController();

// Set specific size
fontController.setFontSize(container, 'large');

// Adjust incrementally
fontController.increaseFontSize(container);
fontController.decreaseFontSize(container);

// Get current
const currentSize = fontController.getCurrentSize(container);

// Preferences
fontController.saveUserPreference('large');
const preferred = fontController.loadUserPreference();
fontController.applyUserPreference(container);
```

---

## Usage Examples

### Example 1: Simple Streaming Setup

```javascript
// Initialize
const container = document.getElementById('chat-messages');
const processor = new TwoRuleStreamProcessor(container);

// Ensure viz engine exists
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}

// Process stream
async function handleAIStream(streamSource) {
    for await (const chunk of streamSource) {
        await processor.processChunk(chunk);
    }
    processor.forceFlush();
}
```

### Example 2: Mixed Content Rendering

```javascript
const mixedContent = `
# Project Overview

Here's our system architecture:

<mermaid>
graph TD
    A[Client] --> B[Server]
    B --> C[Database]
    B --> D[Cache]
</mermaid>

## Performance Metrics

<plotly>
{
    "data": [{
        "x": ["Jan", "Feb", "Mar"],
        "y": [10, 15, 13],
        "type": "bar"
    }],
    "layout": {"title": "Monthly Sales"}
}
</plotly>

That's the complete picture.
`;

// Process all at once
const processor = new TwoRuleStreamProcessor(container);
await processor.processChunk(mixedContent);
processor.forceFlush();
```

### Example 3: Tiptap Document with Visualizations

```javascript
// Create Tiptap editor with visualization support
const editor = new Editor({
    element: document.querySelector('#editor'),
    extensions: [
        StarterKit,
        VisualizationNode.configure({
            renderFunction: async (node, container) => {
                if (!window.vizEngine) {
                    window.vizEngine = new VisualizationEngine();
                    await window.vizEngine.init();
                }
                
                await window.vizEngine.renderVisualizationDirectly(
                    { type: node.attrs.type, content: node.attrs.content },
                    container,
                    node.attrs.chartId
                );
            }
        })
    ],
    content: `
        <p>System architecture:</p>
        <visualization type="mermaid" content="graph LR\nA-->B"></visualization>
    `
});

// Insert new visualization
editor.chain()
    .focus()
    .insertContent({
        type: 'visualization',
        attrs: {
            type: 'mermaid',
            content: 'graph TD\nA-->B',
            chartId: `viz-${Date.now()}`
        }
    })
    .run();
```

### Example 4: Export Visualization from Tiptap

```javascript
// Find visualization node in Tiptap
const vizNodes = editor.state.doc.descendants((node, pos) => {
    if (node.type.name === 'visualization') {
        return { node, pos };
    }
});

// Export first visualization as SVG
if (vizNodes.length > 0) {
    const { node } = vizNodes[0];
    const chartId = node.attrs.chartId;
    
    await window.vizEngine.exportToSVG(chartId);
}
```

### Example 5: Font Size Control

```javascript
// Initialize font controller
const fontController = new MermaidFontController();

// Apply to all visualizations
document.querySelectorAll('.viz-container').forEach(container => {
    fontController.applyUserPreference(container);
});

// Add UI controls
document.getElementById('increase-font').addEventListener('click', () => {
    const activeViz = document.querySelector('.viz-container.active');
    if (activeViz) {
        fontController.increaseFontSize(activeViz);
    }
});

document.getElementById('decrease-font').addEventListener('click', () => {
    const activeViz = document.querySelector('.viz-container.active');
    if (activeViz) {
        fontController.decreaseFontSize(activeViz);
    }
});
```

---

## Key Concepts Summary

### Content Types
- **Type 1 (Markdown):** Text that flows and concatenates
- **Type 2 (Visual):** Discrete visualization blocks

### Delimiters
Recognized patterns:
- `<mermaid>...</mermaid>`
- `<plotly>...</plotly>`
- `<visualization type="...">...</visualization>`
- `\`\`\`mermaid ... \`\`\``
- `\`\`\`plotly ... \`\`\``

### Rendering Order
1. Parse → 2. Package → 3. Queue → 4. Release → 5. Render

### Container Structure
```html
<div class="viz-container" data-package-id="123" data-stream-position="456">
    <div class="viz-header">
        <span class="viz-title">Mermaid Diagram</span>
        <div class="viz-controls">
            <!-- Export, font controls -->
        </div>
    </div>
    <div class="viz-content-area">
        <!-- Actual Mermaid/Plotly render -->
    </div>
    <div class="viz-footer">
        <span class="viz-metadata">Created: ...</span>
    </div>
</div>
```

### Deduplication
Uses SHA-256 hash of content to prevent duplicate renders during streaming.

### Error Handling
- Container validation before rendering
- Retry logic for Plotly (up to 3 attempts)
- Graceful fallback to error display
- Loading indicators during processing

---

## Best Practices

### 1. Always Initialize Engine
```javascript
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}
```

### 2. Wait for DOM Attachment
```javascript
await new Promise(resolve => requestAnimationFrame(resolve));
if (!document.contains(container)) {
    throw new Error('Container not in DOM');
}
```

### 3. Use Ordered Positioning
Always respect `data-stream-position` attributes for insertion order.

### 4. Don't Re-Render Existing Content
Check for existing containers before rendering:
```javascript
const existing = container.querySelector(`[data-package-id="${pkg.id}"]`);
if (existing) {
    console.log('Already rendered, skipping');
    return;
}
```

### 5. Handle Async Properly
Always await rendering:
```javascript
await processor.processChunk(chunk);
await processor.forceFlush();
```

### 6. Clean Up Resources
```javascript
// Remove observers when destroying
plotlyResizeObservers.delete(element);
```

---

## Troubleshooting

### Visualization Not Rendering

**Check:**
1. Is `window.vizEngine` initialized?
2. Is container attached to DOM?
3. Are libraries loaded (Mermaid, Plotly)?
4. Check console for errors

```javascript
console.log('VizEngine exists:', !!window.vizEngine);
console.log('Container in DOM:', document.contains(container));
console.log('Mermaid loaded:', !!window.mermaid);
console.log('Plotly loaded:', !!window.Plotly);
```

### Duplicate Visualizations

**Solution:** Enable deduplication
```javascript
// Content hashing is enabled by default
// Check package contentHash matches
```

### Incorrect Rendering Order

**Solution:** Verify position attributes
```javascript
const elements = container.querySelectorAll('[data-stream-position]');
elements.forEach(el => {
    console.log('Position:', el.getAttribute('data-stream-position'));
});
```

### Tiptap Integration Issues

**Check:**
1. Custom node extension properly registered?
2. Node view component mounted?
3. Content format matches node schema?

```javascript
// Verify extension loaded
console.log('Extensions:', editor.extensionManager.extensions.map(e => e.name));

// Check node exists in schema
console.log('Has visualization node:', !!editor.schema.nodes.visualization);
```

---

## Performance Considerations

### Streaming Performance
- Chunks processed in <10ms typically
- DOM operations batched in `requestAnimationFrame`
- Duplicate detection via content hashing

### Memory Management
- WeakMaps for resize observers (auto garbage collection)
- Package cleanup after rendering
- Temp container cleanup after Tiptap insertion

### Rendering Optimization
- Mermaid renders asynchronously
- Plotly uses responsive config (no manual resize)
- CSS isolation prevents style conflicts

---

## Related Documentation

- `streamingTwoRule.js` - Two-Rule streaming processor source
- `visualisation_copy.js` - Visualization engine source
- Tiptap Documentation: https://tiptap.dev/
- Mermaid Documentation: https://mermaid.js.org/
- Plotly Documentation: https://plotly.com/javascript/

---

**Last Updated:** November 15, 2025  
**Version:** 1.0  
**Maintainers:** AI Agents Platform Team
