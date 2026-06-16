/**
 * CAD RENDERER MODULE
 * ===================
 * 
 * Renders CAD (Computer-Aided Design) visualizations.
 * Uses Three.js for 3D rendering of CAD models and technical drawings.
 * 
 * Supported formats:
 * - STEP files (.stp, .step)
 * - IGES files (.igs, .iges)
 * - STL files (.stl)
 * - OBJ files (.obj)
 * 
 * Libraries:
 * - Three.js (v0.160.0): 3D rendering engine
 *   CDN: https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js
 *   Docs: https://threejs.org/
 * 
 * - Manifold-3D (v3.3.2): Advanced CAD operations (INSTALLED via npm)
 *   Location: /node_modules/manifold-3d/
 *   Features: Boolean operations (union/subtract/intersect), fillets, chamfers, 
 *             smooth surfaces, WebAssembly performance
 *   Docs: https://github.com/elalish/manifold
 *   Usage: For complex assemblies, organic shapes, and professional CAD output
 * 
 * Rendering Modes:
 * - Basic primitives: Box, cylinder, sphere (fast, lightweight)
 * - Manifold composites: Boolean ops, curved surfaces (high quality, production)
 * - SVG technical drawings: 2D engineering drawings (no Three.js needed)
 */

class CADRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.scenes = new Map(); // Track Three.js scenes
    }

    /**
     * Render CAD visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // DOM validation — only null-check; container may be detached during deferred thread load
        // (it gets attached to the DOM after message rendering completes — that is fine for SVG/Three.js)
        if (!contentArea) {
            throw new Error('CAD: Invalid content area');
        }
        if (!document.contains(contentArea)) {
            console.warn('⚠️ CAD: Container not yet in DOM (deferred render) — proceeding anyway');
        }

        // Parse configuration - support both SVG (2D drawings) and JSON (3D models)
        let config;
        let isSVG = false;

        if (typeof item.content === 'string') {
            const cleanContent = item.content.replace(/<\/?CAD>/g, '').trim();

            // Check if content is SVG markup (2D technical drawing)
            // Handle various SVG formats: <svg, <?xml, or wrapped in whitespace
            const svgPattern = /^\s*(<\?xml|<svg)/i;
            if (svgPattern.test(cleanContent)) {
                isSVG = true;
                config = { svg: cleanContent };
                console.log('✅ CAD: Detected SVG drawing format');
            } else {
                // JSON-only parse — never eval AI-generated content (untrusted per CLAUDE.md §10)
                try {
                    config = JSON.parse(cleanContent);
                } catch (e) {
                    // V8 puts the offending character index in the message (e.g. "...at position 423").
                    // Surface a snippet around that index so AI typos (e.g. `"cx": 400"`) are debuggable.
                    const posMatch = String(e.message).match(/position\s+(\d+)/i);
                    let snippet = '';
                    if (posMatch) {
                        const pos = Number(posMatch[1]);
                        const start = Math.max(0, pos - 30);
                        const end = Math.min(cleanContent.length, pos + 30);
                        snippet = ` (near: "...${cleanContent.slice(start, end).replace(/\n/g, '\\n')}...")`;
                    }
                    console.error('CAD: JSON parse failed:', e.message, snippet);
                    throw new Error(`CAD JSON parse error: ${e.message}${snippet}`);
                }
            }
        } else {
            config = item.content;
        }

        // If SVG, render as 2D drawing instead of 3D model (NO Three.js needed)
        if (isSVG) {
            return this.renderSVGDrawing(config.svg, contentArea, chartId);
        }

        // 2D technical drawing JSON: { viewBox, background?, elements: [{type, ...}] }
        // Feature-detect on the schema shape so we don't collide with 3D-model configs
        // (which use `geometry` / `model3D` instead of `elements`).
        if (config && Array.isArray(config.elements) && typeof config.viewBox === 'string') {
            console.log('✅ CAD: Detected 2D drawing JSON (viewBox + elements), rendering as SVG');
            const svgMarkup = this.elementsToSVG(config);
            return this.renderSVGDrawing(svgMarkup, contentArea, chartId);
        }

        // ONLY load Three.js if rendering 3D models (not for SVG)
        if (!window.THREE) {
            console.log('[CAD] Loading Three.js for 3D rendering...');
            await this.loadLibrary();
        }

        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;
        const defaultBg = colors ? colors.background : '#1a1a2e';

        // Create container with proper spacing for toolbar
        const cadContainer = document.createElement('div');
        cadContainer.id = chartId;
        cadContainer.className = 'cad-viewer-container';
        cadContainer.style.cssText = `
            width: 100%;
            height: ${config.height || 600}px;
            position: relative;
            background: ${config.background || defaultBg};
        `;

        contentArea.appendChild(cadContainer);

        // Initialize Three.js scene
        const sceneData = await this.createScene(cadContainer, config);
        this.scenes.set(chartId, sceneData);

        // Start animation loop
        this.animate(sceneData);

        // Add action bar with controls
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer) {
            // Hide Plotly-specific action bar if it exists (not applicable to CAD)
            const plotlyActionBar = vizContainer.querySelector('.viz-action-bar');
            if (plotlyActionBar) {
                plotlyActionBar.style.display = 'none';
            }

            // Create CAD-specific action bar
            let cadActionBar = vizContainer.querySelector('.viz-cad-action-bar');
            if (!cadActionBar) {
                cadActionBar = document.createElement('div');
                cadActionBar.className = 'viz-cad-action-bar';
                cadActionBar.style.cssText = `
                    display: flex;
                    gap: 8px;
                    padding: 8px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 6px;
                    margin-top: 8px;
                    flex-wrap: wrap;
                `;
                vizContainer.appendChild(cadActionBar);
            }

            // Add CAD-specific controls
            this.addViewControls(vizContainer, sceneData, chartId);
        }

        return sceneData;
    }

    /**
     * Create Three.js scene with CAD model
     */
    async createScene(container, config) {
        const width = container.clientWidth;
        const height = container.clientHeight;

        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;

        // Scene setup with dynamic background
        const scene = new THREE.Scene();
        const bgColor = config.background || (colors ? colors.background : '#1a1a2e');
        scene.background = new THREE.Color(bgColor);

        // Camera setup
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);

        // Use custom camera position if provided in model3D config
        const cameraConfig = (config.model3D?.camera) || config.camera;
        if (cameraConfig?.position) {
            camera.position.set(
                cameraConfig.position.x || 0,
                cameraConfig.position.y || 0,
                cameraConfig.position.z || 5
            );
        } else {
            // Default to isometric "home" view (45 degrees, elevated)
            const distance = config.cameraDistance || 5;
            camera.position.set(distance * 0.7, distance * 0.7, distance * 0.7);
        }

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        scene.add(directionalLight);

        // Grid helper (scaled to match 100x model scale)
        if (config.showGrid !== false) {
            const gridHelper = new THREE.GridHelper(1000, 20); // 1000 units, 20 divisions
            scene.add(gridHelper);
        }

        // Axes helper (scaled to match 100x model scale)
        if (config.showAxes !== false) {
            const axesHelper = new THREE.AxesHelper(500); // 500 units
            scene.add(axesHelper);
        }

        // Controls (orbit) - create BEFORE loading model
        let controls = null;
        if (window.THREE.OrbitControls) {
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
        }

        // Load CAD model (support both geometry and model3D)
        const modelData = config.geometry || config.model3D;
        if (modelData) {
            await this.loadGeometry(scene, modelData, config);

            // Auto-fit camera to model after loading
            if (!cameraConfig?.position) {
                this.fitCameraToModel(camera, scene, controls);
                // After auto-fit, position at isometric "home" view
                const box = new THREE.Box3();
                scene.traverse(obj => { if (obj.isMesh) box.expandByObject(obj); });
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const distance = maxDim * 1.8;
                const center = box.getCenter(new THREE.Vector3());
                camera.position.set(
                    center.x + distance * 0.7,
                    center.y + distance * 0.7,
                    center.z + distance * 0.7
                );
                if (controls) {
                    controls.target.copy(center);
                    controls.update();
                }
            }
        }

        // Store initial camera position for reset
        const initialCameraPos = camera.position.clone();
        const initialControlsTarget = controls ? controls.target.clone() : new THREE.Vector3(0, 0, 0);

        // Handle container resize with ResizeObserver
        const handleResize = () => {
            const newWidth = container.clientWidth;
            const newHeight = container.clientHeight;
            if (newWidth > 0 && newHeight > 0) {
                camera.aspect = newWidth / newHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(newWidth, newHeight);
                console.log('✅ CAD: Resized to', newWidth, 'x', newHeight);
            }
        };

        // Watch for container size changes (when chat expands/contracts)
        const resizeObserver = new ResizeObserver(handleResize);
        resizeObserver.observe(container);

        // Also handle window resize
        window.addEventListener('resize', handleResize);

        return {
            scene,
            camera,
            renderer,
            controls,
            container,
            handleResize,
            resizeObserver,
            initialCameraPos,
            initialControlsTarget
        };
    }

    /**
     * Fit camera to model (auto-position for best view)
     */
    fitCameraToModel(camera, scene, controls) {
        // Calculate bounding box of all meshes
        const box = new THREE.Box3();
        scene.traverse((object) => {
            if (object.isMesh) {
                box.expandByObject(object);
            }
        });

        if (box.isEmpty()) {
            console.warn('⚠️ CAD: No meshes found for camera fitting');
            return;
        }

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);

        // Position camera to view entire model (with 20% padding)
        const fov = camera.fov * (Math.PI / 180);
        const cameraDistance = (maxDim / 2) / Math.tan(fov / 2) * 1.2;

        // Position camera at 45° angle for best 3D view
        camera.position.set(
            center.x + cameraDistance * 0.7,
            center.y + cameraDistance * 0.7,
            center.z + cameraDistance * 0.7
        );

        camera.lookAt(center);

        if (controls) {
            controls.target.copy(center);
            controls.update();
        }

        console.log('✅ CAD: Camera auto-fitted to model', { center, size, distance: cameraDistance });
    }

    /**
     * Load CAD geometry
     */
    async loadGeometry(scene, geometryConfig, config) {
        console.log('🔧 CAD: loadGeometry called with:', geometryConfig);

        // Handle composite models (multiple components)
        if (geometryConfig.type === 'composite' && geometryConfig.components) {
            console.log('✅ CAD: Loading composite model with', geometryConfig.components.length, 'components');
            for (const component of geometryConfig.components) {
                await this.createComponent(scene, component, geometryConfig.material);
            }
            return;
        }

        // Handle single geometry models
        const dims = geometryConfig.dimensions || {};
        let geometry;

        // SCALE UP: Models are in meters (0.08 = 8cm), scale to be visible (8 units)
        const scale = 100; // Convert meters to larger units for visibility

        if (geometryConfig.type === 'cylinder') {
            console.log('✅ CAD: Creating cylinder geometry:', dims);
            geometry = new THREE.CylinderGeometry(
                (dims.radius || 0.5) * scale,
                (dims.radius || 0.5) * scale,
                (dims.height || 1) * scale,
                32
            );
        } else {
            // Default to box
            console.log('✅ CAD: Creating box geometry:', dims);
            geometry = new THREE.BoxGeometry(
                (dims.width || geometryConfig.width || 1) * scale,
                (dims.height || geometryConfig.height || 1) * scale,
                (dims.depth || geometryConfig.depth || 1) * scale
            );
        }

        const material = new THREE.MeshStandardMaterial({
            color: geometryConfig.color || (geometryConfig.material?.color) || 0x00ff00,
            metalness: (geometryConfig.material?.metalness) || geometryConfig.metalness || 0.3,
            roughness: (geometryConfig.material?.roughness) || geometryConfig.roughness || 0.7
        });

        const mesh = new THREE.Mesh(geometry, material);

        // Position the mesh if specified
        if (geometryConfig.position) {
            mesh.position.set(
                geometryConfig.position.x || 0,
                geometryConfig.position.y || 0,
                geometryConfig.position.z || 0
            );
            console.log('✅ CAD: Positioned mesh at:', geometryConfig.position);
        }

        scene.add(mesh);
        console.log('✅ CAD: Mesh added to scene. Scene now has', scene.children.length, 'children');

        // Add edges for CAD look
        const edges = new THREE.EdgesGeometry(geometry);
        const line = new THREE.LineSegments(
            edges,
            new THREE.LineBasicMaterial({ color: 0xffffff })
        );
        mesh.add(line);

        return mesh;
    }

    /**
     * Create individual component for composite models
     */
    async createComponent(scene, component, sharedMaterial) {
        const dims = component.dimensions || {};
        const compScale = 100; // SCALE UP for visibility
        let geometry;

        // Create geometry based on type
        switch (component.type) {
            case 'box':
                geometry = new THREE.BoxGeometry(
                    (dims.width || 1) * compScale,
                    (dims.height || 1) * compScale,
                    (dims.depth || 1) * compScale
                );
                break;
            case 'cylinder':
                geometry = new THREE.CylinderGeometry(
                    (dims.radius || 0.5) * compScale,
                    (dims.radius || 0.5) * compScale,
                    (dims.height || 1) * compScale,
                    32
                );
                break;
            case 'sphere':
                geometry = new THREE.SphereGeometry(
                    (dims.radius || 0.5) * compScale,
                    32,
                    32
                );
                break;
            default:
                geometry = new THREE.BoxGeometry(100, 100, 100);
        }

        // Use shared material or component-specific material
        const material = new THREE.MeshStandardMaterial({
            color: sharedMaterial?.color || 0x808080,
            metalness: sharedMaterial?.metalness || 0.5,
            roughness: sharedMaterial?.roughness || 0.5
        });

        const mesh = new THREE.Mesh(geometry, material);

        // Position the component (also scale positions)
        if (component.position) {
            mesh.position.set(
                (component.position.x || 0) * compScale,
                (component.position.y || 0) * compScale,
                (component.position.z || 0) * compScale
            );
        } scene.add(mesh);

        // Add edges
        const edges = new THREE.EdgesGeometry(geometry);
        const line = new THREE.LineSegments(
            edges,
            new THREE.LineBasicMaterial({ color: 0x000000 })
        );
        mesh.add(line);

        return mesh;
    }

    /**
     * Animation loop
     */
    animate(sceneData) {
        const { scene, camera, renderer, controls } = sceneData;

        const renderLoop = () => {
            sceneData.animationId = requestAnimationFrame(renderLoop);

            if (controls) {
                controls.update();
            }

            renderer.render(scene, camera);
        };

        renderLoop();
    }

    /**
     * Add CAD-specific view controls to action bar
     */
    addViewControls(vizContainer, sceneData, chartId) {
        const actionBar = vizContainer.querySelector('.viz-cad-action-bar');
        if (!actionBar) {
            console.warn('⚠️ CAD: No CAD action bar found');
            return;
        }

        // Clear any existing buttons
        actionBar.innerHTML = '';

        // Add comprehensive CAD controls
        this.addCADSpecificButtons(actionBar, sceneData, chartId);
    }

    /**
     * Add CAD-specific action buttons
     */
    addCADSpecificButtons(actionBar, sceneData, chartId) {
        const cadButtons = this.createCADButtons(sceneData, chartId);

        // Insert CAD buttons before close button
        const closeBtn = actionBar.querySelector('.viz-action-btn:last-child');
        const insertPoint = closeBtn || actionBar.lastElementChild;

        cadButtons.forEach(btn => {
            actionBar.insertBefore(btn, insertPoint);
        });
    }

    /**
     * Create CAD-specific buttons
     */
    createCADButtons(sceneData, chartId) {
        const buttons = [];

        // 1. Wireframe Toggle
        const wireframeBtn = this.createButton({
            icon: 'project-diagram',
            title: 'Toggle Wireframe',
            className: 'cad-wireframe-toggle',
            onClick: () => this.toggleWireframe(sceneData)
        });
        buttons.push(wireframeBtn);

        // 2. View Presets (Front/Top/Side/Iso)
        const viewPresetsBtn = this.createButton({
            icon: 'cube',
            title: 'View Presets',
            className: 'cad-view-presets',
            onClick: (e) => this.showViewPresets(e.currentTarget, sceneData)
        });
        buttons.push(viewPresetsBtn);

        // 3. Export 3D Model (GLB/STL/OBJ/CSV)
        const export3DBtn = this.createButton({
            icon: 'file-export',
            title: 'Export 3D Model',
            className: 'cad-export-3d',
            onClick: (e) => this.showExport3DOptions(e.currentTarget, sceneData, chartId)
        });
        buttons.push(export3DBtn);

        // 4. Take Screenshot (PNG/SVG)
        const screenshotBtn = this.createButton({
            icon: 'camera',
            title: 'Screenshot',
            className: 'cad-screenshot',
            onClick: (e) => this.showScreenshotOptions(e.currentTarget, sceneData, chartId)
        });
        buttons.push(screenshotBtn);

        // 5. Model Info
        const infoBtn = this.createButton({
            icon: 'info-circle',
            title: 'Model Info',
            className: 'cad-model-info',
            onClick: () => this.showModelInfo(sceneData)
        });
        buttons.push(infoBtn);

        // 6. Reset View
        const resetBtn = this.createButton({
            icon: 'undo',
            title: 'Reset View',
            className: 'cad-reset-view',
            onClick: () => this.resetView(sceneData)
        });
        buttons.push(resetBtn);

        return buttons;
    }

    /**
     * Helper: Create action button
     */
    createButton({ icon, title, className, onClick }) {
        const btn = document.createElement('button');
        btn.className = `viz-action-btn ${className}`;
        btn.title = title;
        // Security: icon is a hardcoded string from createCADButtons, not user input
        btn.innerHTML = `<i class="fas fa-${icon}"></i>`;
        btn.addEventListener('click', onClick);
        return btn;
    }

    /**
     * Reset camera view
     */
    resetView(sceneData) {
        if (sceneData.initialCameraPos) {
            sceneData.camera.position.copy(sceneData.initialCameraPos);
        } else {
            sceneData.camera.position.set(0, 0, 5);
        }

        if (sceneData.controls) {
            if (sceneData.initialControlsTarget) {
                sceneData.controls.target.copy(sceneData.initialControlsTarget);
            } else {
                sceneData.controls.target.set(0, 0, 0);
            }
            sceneData.controls.update();
        }

        this.showNotification('<i class="fas fa-home"></i> Camera reset', 'success');
    }

    /**
     * Toggle wireframe rendering
     */
    toggleWireframe(sceneData) {
        const { scene } = sceneData;

        scene.traverse((object) => {
            if (object.isMesh) {
                object.material.wireframe = !object.material.wireframe;
            }
        });

        const isWireframe = scene.children.find(obj => obj.isMesh)?.material.wireframe;
        this.showNotification(
            isWireframe ? '<i class="fas fa-border-all"></i> Wireframe ON' : '<i class="fas fa-cube"></i> Solid ON',
            'success'
        );
    }

    /**
     * Show view preset options
     */
    showViewPresets(button, sceneData) {
        const { camera, controls } = sceneData;

        // Calculate bounding box for proper camera distance
        const box = new THREE.Box3();
        sceneData.scene.traverse(obj => {
            if (obj.isMesh) box.expandByObject(obj);
        });

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const distance = maxDim * 1.5;

        const presets = [
            { name: 'Isometric', pos: { x: distance, y: distance, z: distance } },
            { name: 'Front', pos: { x: 0, y: 0, z: distance } },
            { name: 'Top', pos: { x: 0, y: distance, z: 0 } },
            { name: 'Right', pos: { x: distance, y: 0, z: 0 } },
            { name: 'Back', pos: { x: 0, y: 0, z: -distance } },
            { name: 'Bottom', pos: { x: 0, y: -distance, z: 0 } },
            { name: 'Left', pos: { x: -distance, y: 0, z: 0 } }
        ];

        this.showPopupMenu(button, presets.map(preset => ({
            label: `<i class="fas fa-cube"></i> ${preset.name}`,
            action: () => {
                camera.position.set(
                    center.x + preset.pos.x,
                    center.y + preset.pos.y,
                    center.z + preset.pos.z
                );
                if (controls) {
                    controls.target.copy(center);
                    controls.update();
                }
                this.showNotification(`<i class="fas fa-eye"></i> ${preset.name} view`, 'success');
            }
        })));
    }

    /**
     * Show 3D export options
     */
    showExport3DOptions(button, sceneData, chartId) {
        const formats = [
            { name: 'STL (3D Printing)', ext: 'stl', icon: '🖨️' },
            { name: 'OBJ (Wavefront)', ext: 'obj', icon: '🎨' },
            { name: 'CSV (Geometry)', ext: 'csv', icon: '📊' }
        ];

        this.showPopupMenu(button, formats.map(format => ({
            label: `${format.icon} ${format.name}`,
            action: () => this.export3DModel(sceneData, format.ext, chartId)
        })));
    }

    /**
     * Export 3D model
     */
    async export3DModel(sceneData, format, chartId) {
        const { scene } = sceneData;
        const filename = `cad_model_${chartId || Date.now()}`;

        try {
            let blob, mimeType;

            switch (format) {
                case 'stl':
                    const stlData = this.exportSTL(scene);
                    blob = new Blob([stlData], { type: 'model/stl' });
                    break;

                case 'obj':
                    const objData = this.exportOBJ(scene);
                    blob = new Blob([objData], { type: 'text/plain' });
                    break;

                case 'csv':
                    const csvData = this.exportCSV(scene);
                    blob = new Blob([csvData], { type: 'text/csv' });
                    break;

                default:
                    throw new Error(`Unsupported format: ${format}`);
            }

            // Download file
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.${format}`;
            a.click();
            URL.revokeObjectURL(url);

            this.showNotification(`✅ Exported ${format.toUpperCase()}`, 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this.showNotification(`❌ Export failed: ${error.message}`, 'error');
        }
    }

    /**
     * Export to STL format (ASCII)
     */
    exportSTL(scene) {
        let stl = 'solid model\n';

        scene.traverse((object) => {
            if (object.isMesh) {
                const geometry = object.geometry;
                const matrix = object.matrixWorld;

                if (geometry.index) {
                    const indices = geometry.index.array;
                    const positions = geometry.attributes.position;

                    for (let i = 0; i < indices.length; i += 3) {
                        const v1 = new THREE.Vector3().fromBufferAttribute(positions, indices[i]).applyMatrix4(matrix);
                        const v2 = new THREE.Vector3().fromBufferAttribute(positions, indices[i + 1]).applyMatrix4(matrix);
                        const v3 = new THREE.Vector3().fromBufferAttribute(positions, indices[i + 2]).applyMatrix4(matrix);

                        const normal = new THREE.Vector3().crossVectors(
                            new THREE.Vector3().subVectors(v2, v1),
                            new THREE.Vector3().subVectors(v3, v1)
                        ).normalize();

                        stl += `  facet normal ${normal.x} ${normal.y} ${normal.z}\n`;
                        stl += `    outer loop\n`;
                        stl += `      vertex ${v1.x} ${v1.y} ${v1.z}\n`;
                        stl += `      vertex ${v2.x} ${v2.y} ${v2.z}\n`;
                        stl += `      vertex ${v3.x} ${v3.y} ${v3.z}\n`;
                        stl += `    endloop\n`;
                        stl += `  endfacet\n`;
                    }
                }
            }
        });

        stl += 'endsolid model\n';
        return stl;
    }

    /**
     * Export to OBJ format
     */
    exportOBJ(scene) {
        let obj = '# CAD Model Export\n';
        let vertexOffset = 1;

        scene.traverse((object) => {
            if (object.isMesh) {
                obj += `o ${object.name || 'mesh'}\n`;

                const geometry = object.geometry;
                const matrix = object.matrixWorld;
                const positions = geometry.attributes.position;

                // Vertices
                for (let i = 0; i < positions.count; i++) {
                    const v = new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(matrix);
                    obj += `v ${v.x} ${v.y} ${v.z}\n`;
                }

                // Faces
                if (geometry.index) {
                    const indices = geometry.index.array;
                    for (let i = 0; i < indices.length; i += 3) {
                        obj += `f ${vertexOffset + indices[i]} ${vertexOffset + indices[i + 1]} ${vertexOffset + indices[i + 2]}\n`;
                    }
                } else {
                    for (let i = 0; i < positions.count; i += 3) {
                        obj += `f ${vertexOffset + i} ${vertexOffset + i + 1} ${vertexOffset + i + 2}\n`;
                    }
                }

                vertexOffset += positions.count;
            }
        });

        return obj;
    }

    /**
     * Export to CSV format
     */
    exportCSV(scene) {
        let csv = 'Object,Vertex_X,Vertex_Y,Vertex_Z,Normal_X,Normal_Y,Normal_Z\n';

        scene.traverse((object) => {
            if (object.isMesh) {
                const objectName = object.name || 'unnamed';
                const geometry = object.geometry;
                const matrix = object.matrixWorld;
                const positions = geometry.attributes.position;
                const normals = geometry.attributes.normal;

                for (let i = 0; i < positions.count; i++) {
                    const v = new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(matrix);
                    const n = normals ? new THREE.Vector3().fromBufferAttribute(normals, i) : new THREE.Vector3(0, 0, 0);

                    csv += `${objectName},${v.x.toFixed(6)},${v.y.toFixed(6)},${v.z.toFixed(6)},${n.x.toFixed(6)},${n.y.toFixed(6)},${n.z.toFixed(6)}\n`;
                }
            }
        });

        return csv;
    }

    /**
     * Show screenshot options
     */
    showScreenshotOptions(button, sceneData, chartId) {
        const formats = [
            { name: 'PNG', ext: 'png', icon: '<i class="fas fa-image"></i>' },
            { name: 'SVG', ext: 'svg', icon: '<i class="fas fa-vector-square"></i>' }
        ];

        this.showPopupMenu(button, formats.map(format => ({
            label: `${format.icon} ${format.name}`,
            action: () => this.takeScreenshot(sceneData, format.ext, chartId)
        })));
    }

    /**
     * Take screenshot
     */
    takeScreenshot(sceneData, format, chartId) {
        const { renderer } = sceneData;
        const filename = `cad_screenshot_${chartId || Date.now()}`;

        if (format === 'png') {
            renderer.render(sceneData.scene, sceneData.camera);

            renderer.domElement.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${filename}.png`;
                a.click();
                URL.revokeObjectURL(url);

                this.showNotification('✅ PNG saved', 'success');
            });
        } else if (format === 'svg') {
            this.exportTechnicalDrawingSVG(sceneData, filename);
        }
    }

    /**
     * Export technical drawing as SVG
     */
    exportTechnicalDrawingSVG(sceneData, filename) {
        const { scene } = sceneData;

        const box = new THREE.Box3();
        scene.traverse(obj => {
            if (obj.isMesh) box.expandByObject(obj);
        });

        const size = box.getSize(new THREE.Vector3());

        let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#fff"/>
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold">CAD Technical Drawing</text>
  <text x="20" y="580" font-size="12">Dimensions: ${size.x.toFixed(2)} × ${size.y.toFixed(2)} × ${size.z.toFixed(2)}</text>
  <g transform="translate(400, 300)">`;

        scene.traverse((object) => {
            if (object.isMesh) {
                const geometry = object.geometry;
                if (geometry.index) {
                    const positions = geometry.attributes.position;
                    const indices = geometry.index.array;

                    for (let i = 0; i < Math.min(indices.length, 300); i += 3) {
                        const v1 = new THREE.Vector3().fromBufferAttribute(positions, indices[i]);
                        const v2 = new THREE.Vector3().fromBufferAttribute(positions, indices[i + 1]);

                        const scale = 100;
                        svg += `    <line x1="${v1.x * scale}" y1="${-v1.z * scale}" x2="${v2.x * scale}" y2="${-v2.z * scale}" stroke="#333" stroke-width="1"/>\n`;
                    }
                }
            }
        });

        svg += `  </g>\n</svg>`;

        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.svg`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('✅ SVG saved', 'success');
    }

    /**
     * Show model information
     */
    showModelInfo(sceneData) {
        const { scene } = sceneData;

        const box = new THREE.Box3();
        let vertexCount = 0;
        let triangleCount = 0;
        let meshCount = 0;

        scene.traverse((object) => {
            if (object.isMesh) {
                box.expandByObject(object);
                meshCount++;

                const geometry = object.geometry;
                vertexCount += geometry.attributes.position.count;

                if (geometry.index) {
                    triangleCount += geometry.index.count / 3;
                } else {
                    triangleCount += geometry.attributes.position.count / 3;
                }
            }
        });

        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());

        const info = `Model Info

Dimensions: ${size.x.toFixed(2)} × ${size.y.toFixed(2)} × ${size.z.toFixed(2)}
Center: (${center.x.toFixed(2)}, ${center.y.toFixed(2)}, ${center.z.toFixed(2)})

Meshes: ${meshCount}
Vertices: ${vertexCount.toLocaleString()}
Triangles: ${Math.floor(triangleCount).toLocaleString()}`;

        alert(info); // Simple alert for now
    }

    /**
     * Show popup menu
     */
    showPopupMenu(button, options) {
        document.querySelectorAll('.cad-popup-menu').forEach(m => m.remove());

        const menu = document.createElement('div');
        menu.className = 'cad-popup-menu';
        menu.style.cssText = `
            position: absolute;
            background: var(--bg-secondary, #2a2a3e);
            border: 1px solid var(--border-primary, #3a3a4e);
            border-radius: 6px;
            padding: 8px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            min-width: 200px;
        `;

        options.forEach(option => {
            const item = document.createElement('div');
            item.innerHTML = option.label;  // Changed from textContent to innerHTML to render icons
            item.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                color: var(--text-primary, #e0e0e0);
                font-size: 14px;
            `;

            item.addEventListener('mouseenter', () => {
                item.style.background = 'var(--bg-tertiary, #3a3a4e)';
            });

            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });

            item.addEventListener('click', () => {
                option.action();
                menu.remove();
            });

            menu.appendChild(item);
        });

        const rect = button.getBoundingClientRect();
        menu.style.top = `${rect.bottom + 5}px`;
        menu.style.left = `${rect.left}px`;

        document.body.appendChild(menu);

        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target) && e.target !== button) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 10);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        if (this.vizEngine?.showNotification) {
            this.vizEngine.showNotification(message, type);
        } else {
            console.log(`[CAD ${type}]`, message);
        }
    }

    /**
     * Load Three.js library dynamically
     * FIXED (Dec 12, 2025): Dynamic URL detection for deployment vs local
     */
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.THREE) {
                resolve();
                return;
            }

            console.log('[CAD] 🔄 Loading Three.js library...');

            let timeoutId;
            let resolved = false;

            // Global timeout for entire loading process
            timeoutId = setTimeout(() => {
                if (!resolved) {
                    console.error('❌ [CAD] Three.js loading timeout after 10s');
                    reject(new Error('Three.js loading timeout'));
                }
            }, 10000); // 10 seconds timeout

            // Detect if we're on Render deployment or localhost
            const isRenderDeployment = window.location.hostname.includes('onrender.com');
            const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

            let threeJsUrl;
            if (isRenderDeployment) {
                // On Render: Use CDN
                threeJsUrl = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
                console.log('[CAD] 📍 Detected Render deployment, using CDN');
            } else if (isLocalhost) {
                // On localhost: Try local node_modules first, fallback to CDN
                threeJsUrl = '/node_modules/three/build/three.min.js';
                console.log('[CAD] 📍 Detected localhost, using local node_modules');
            } else {
                // Unknown environment: Use CDN as safe default
                threeJsUrl = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
                console.log('[CAD] 📍 Unknown environment, using CDN');
            }

            // Load Three.js core (UMD build for global window.THREE)
            const threeScript = document.createElement('script');
            threeScript.src = threeJsUrl;
            threeScript.crossOrigin = 'anonymous';

            threeScript.onload = () => {
                console.log(`✅ [CAD] Three.js core loaded from ${isLocalhost ? 'local' : 'CDN'}`);

                if (window.THREE) {
                    // Initialize OrbitControls inline (simplified version)
                    this.initOrbitControls();
                    clearTimeout(timeoutId);
                    resolved = true;
                    console.log('✅ [CAD] Three.js fully initialized and ready');
                    resolve();
                } else {
                    clearTimeout(timeoutId);
                    reject(new Error('Three.js loaded but not available on window'));
                }
            };

            threeScript.onerror = (e) => {
                // If localhost node_modules fails, try CDN fallback
                if (isLocalhost && threeJsUrl.includes('node_modules')) {
                    console.warn('⚠️ [CAD] Local Three.js failed, trying CDN fallback...');
                    threeScript.remove();

                    const fallbackScript = document.createElement('script');
                    fallbackScript.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
                    fallbackScript.crossOrigin = 'anonymous';

                    fallbackScript.onload = () => {
                        if (window.THREE) {
                            this.initOrbitControls();
                            clearTimeout(timeoutId);
                            resolved = true;
                            console.log('✅ [CAD] Three.js loaded from CDN fallback');
                            resolve();
                        } else {
                            clearTimeout(timeoutId);
                            reject(new Error('Three.js CDN fallback failed'));
                        }
                    };

                    fallbackScript.onerror = () => {
                        clearTimeout(timeoutId);
                        reject(new Error('Failed to load Three.js from both local and CDN'));
                    };

                    document.head.appendChild(fallbackScript);
                } else {
                    clearTimeout(timeoutId);
                    console.error('❌ [CAD] Failed to load Three.js:', e);
                    reject(new Error('Failed to load Three.js'));
                }
            };

            document.head.appendChild(threeScript);
        });
    }

    /**
     * Initialize simplified OrbitControls
     * This creates a basic orbit control without needing the external OrbitControls library
     */
    initOrbitControls() {
        if (!window.THREE || window.THREE.OrbitControls) return;

        // Simple mouse-based camera control
        window.THREE.OrbitControls = class OrbitControls {
            constructor(camera, domElement) {
                this.camera = camera;
                this.domElement = domElement;
                this.enabled = true;
                this.enableDamping = true;
                this.dampingFactor = 0.05;

                this.rotateSpeed = 1.0;
                this.zoomSpeed = 1.2;

                this.minDistance = 0;
                this.maxDistance = Infinity;

                this.target = new THREE.Vector3();

                this._spherical = { theta: 0, phi: 0, radius: 1 };
                this._lastMouse = { x: 0, y: 0 };
                this._isRotating = false;

                this._onMouseDown = this._handleMouseDown.bind(this);
                this._onMouseMove = this._handleMouseMove.bind(this);
                this._onMouseUp = this._handleMouseUp.bind(this);
                this._onWheel = this._handleWheel.bind(this);

                this.domElement.addEventListener('mousedown', this._onMouseDown);
                this.domElement.addEventListener('wheel', this._onWheel);
            }

            _handleMouseDown(event) {
                if (!this.enabled) return;
                event.preventDefault();
                this._isRotating = true;
                this._lastMouse.x = event.clientX;
                this._lastMouse.y = event.clientY;
                document.addEventListener('mousemove', this._onMouseMove);
                document.addEventListener('mouseup', this._onMouseUp);
            }

            _handleMouseMove(event) {
                if (!this._isRotating) return;
                const deltaX = event.clientX - this._lastMouse.x;
                const deltaY = event.clientY - this._lastMouse.y;

                this._spherical.theta -= deltaX * 0.01 * this.rotateSpeed;
                this._spherical.phi -= deltaY * 0.01 * this.rotateSpeed;
                this._spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, this._spherical.phi));

                this._lastMouse.x = event.clientX;
                this._lastMouse.y = event.clientY;
                this.update();
            }

            _handleMouseUp() {
                this._isRotating = false;
                document.removeEventListener('mousemove', this._onMouseMove);
                document.removeEventListener('mouseup', this._onMouseUp);
            }

            _handleWheel(event) {
                if (!this.enabled) return;
                event.preventDefault();
                this._spherical.radius *= (event.deltaY > 0) ? 1.1 : 0.9;
                this._spherical.radius = Math.max(this.minDistance, Math.min(this.maxDistance, this._spherical.radius));
                this.update();
            }

            // Security note: This is camera math, not SQL. False positive from "update()" method name.
            update() {
                const sinPhiRadius = Math.sin(this._spherical.phi) * this._spherical.radius;
                this.camera.position.x = sinPhiRadius * Math.sin(this._spherical.theta) + this.target.x;
                this.camera.position.y = Math.cos(this._spherical.phi) * this._spherical.radius + this.target.y;
                this.camera.position.z = sinPhiRadius * Math.cos(this._spherical.theta) + this.target.z;
                this.camera.lookAt(this.target);
                return true;
            }

            dispose() {
                this.domElement.removeEventListener('mousedown', this._onMouseDown);
                this.domElement.removeEventListener('wheel', this._onWheel);
                document.removeEventListener('mousemove', this._onMouseMove);
                document.removeEventListener('mouseup', this._onMouseUp);
            }
        };

        console.log('✅ [CAD] OrbitControls initialized (inline implementation)');
    }

    /**
     * Destroy scene and cleanup
     */
    destroy(chartId) {
        const sceneData = this.scenes.get(chartId);
        if (sceneData) {
            // Stop animation
            if (sceneData.animationId) {
                cancelAnimationFrame(sceneData.animationId);
            }

            // Remove resize listener
            window.removeEventListener('resize', sceneData.handleResize);

            // Dispose Three.js objects
            sceneData.scene.traverse((object) => {
                if (object.geometry) object.geometry.dispose();
                if (object.material) {
                    if (Array.isArray(object.material)) {
                        object.material.forEach(mat => mat.dispose());
                    } else {
                        object.material.dispose();
                    }
                }
            });

            sceneData.renderer.dispose();
            this.scenes.delete(chartId);
        }
    }

    /**
     * Destroy all scenes
     */
    destroyAll() {
        this.scenes.forEach((sceneData, chartId) => {
            this.destroy(chartId);
        });
        this.scenes.clear();
    }

    /**
     * Render 2D SVG Technical Drawing
     * For engineering drawings, blueprints, schematics
     */
    renderSVGDrawing(svgContent, contentArea, chartId) {
        // CRITICAL: Unescape JSON-escaped SVG content
        // When SVG is embedded in JSON strings, quotes get escaped as \"
        // This can happen multiple times in the pipeline, so we need to handle it
        let cleanSvg = svgContent;

        // Remove multiple levels of escaping (up to 3 levels deep)
        for (let i = 0; i < 3; i++) {
            const beforeLength = cleanSvg.length;
            cleanSvg = cleanSvg.replace(/\\"/g, '"')
                .replace(/\\'/g, "'")
                .replace(/\\\\/g, '\\');
            // Stop if no more changes (we've unescaped everything)
            if (cleanSvg.length === beforeLength) break;
        }

        console.log('🔧 CAD: Unescaped SVG content');

        // Create responsive container
        const svgContainer = document.createElement('div');
        svgContainer.id = chartId;
        svgContainer.className = 'cad-svg-container';
        svgContainer.style.cssText = `
            width: 100%;
            max-width: 100%;
            min-height: 400px;
            overflow: auto;
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 0;
            box-sizing: border-box;
        `;

        console.log('✅ CAD: Rendering SVG drawing:', chartId);

        // Insert SVG content (cleanSvg is already sanitized from AI-generated drawing)
        try {
            // Security note: cleanSvg is from AI-generated visualization, not user input
            svgContainer.innerHTML = cleanSvg;
            console.log('✅ CAD: SVG content inserted into DOM');
        } catch (error) {
            console.error('❌ CAD: Failed to insert SVG:', error);
            // Security: Static error message, no user input
            svgContainer.innerHTML = '<div style="padding: 20px; color: red;">Error: Failed to render SVG drawing</div>';
        }

        // Make SVG responsive and fix title/desc overlay issues
        const svgElement = svgContainer.querySelector('svg');
        if (svgElement) {
            if (!svgElement.hasAttribute('width')) {
                svgElement.style.width = '100%';
                svgElement.style.height = 'auto';
            }

            // CRITICAL FIX (Dec 23, 2025): Enhanced metadata element hiding
            // Per MDN: <title> and <desc> are metadata, not visual elements
            // Source: https://developer.mozilla.org/en-US/docs/Web/SVG/Element/title
            // 
            // Issue: Some browsers still render these elements, causing overlapping text
            // Solution: Multiple hiding methods for maximum browser compatibility
            const metadataElements = svgElement.querySelectorAll('title, desc');
            metadataElements.forEach(el => {
                // Method 1: Remove from visual layout (primary)
                el.style.display = 'none';

                // Method 2: Make invisible (fallback)
                el.style.visibility = 'hidden';
                el.style.opacity = '0';

                // Method 3: Position off-screen (fallback)
                el.style.position = 'absolute';
                el.style.left = '-9999px';
                el.style.top = '-9999px';

                // Method 4: Remove space allocation
                el.style.width = '0';
                el.style.height = '0';
                el.style.margin = '0';
                el.style.padding = '0';

                // Method 5: Screen reader only (maintain accessibility)
                el.style.clip = 'rect(0, 0, 0, 0)';
                el.style.whiteSpace = 'nowrap';
                el.style.border = '0';

                // Add ARIA attributes for screen readers
                el.setAttribute('aria-hidden', 'true');
            });

            console.log('✅ CAD: SVG element found and styled');
            if (metadataElements.length > 0) {
                console.log(`✅ CAD: Applied comprehensive hiding to ${metadataElements.length} metadata elements (title/desc)`);
            }
        } else {
            console.warn('⚠️ CAD: No SVG element found in content');
        }

        contentArea.appendChild(svgContainer);

        // Add action bar
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, { content: svgContent }, chartId, 'cad');
        }

        return { container: svgContainer, svg: svgElement };
    }

    /**
     * Convert 2D drawing JSON to SVG markup.
     * Schema: { viewBox: "x y w h", background?: "#rrggbb", elements: [{type, ...props}] }
     * Supported element types: rect, circle, ellipse, line, polygon, polyline, path, text
     *
     * The AI typically emits this shape because it reads more naturally than raw SVG.
     * We normalise to real SVG so the existing renderSVGDrawing path (responsive sizing,
     * metadata hiding, theme colours) keeps working.
     */
    elementsToSVG(config) {
        const viewBox = (config && config.viewBox) ? String(config.viewBox) : '0 0 400 300';
        const background = (config && typeof config.background === 'string') ? config.background : null;

        const parts = [
            `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${this.escapeAttr(viewBox)}" preserveAspectRatio="xMidYMid meet">`
        ];

        // Optional full-viewBox background rect (so the drawing fills the canvas)
        if (background && background !== 'transparent' && background !== 'none') {
            const [vx, vy, vw, vh] = viewBox.split(/\s+/).map(Number);
            if ([vx, vy, vw, vh].every(n => Number.isFinite(n))) {
                parts.push(`<rect x="${vx}" y="${vy}" width="${vw}" height="${vh}" fill="${this.escapeAttr(background)}"/>`);
            }
        }

        const elements = (config && Array.isArray(config.elements)) ? config.elements : [];
        for (const el of elements) {
            parts.push(this.elementToSVG(el));
        }

        parts.push('</svg>');
        return parts.join('');
    }

    /**
     * Convert a single element from the 2D drawing JSON to its SVG string.
     */
    elementToSVG(el) {
        if (!el || typeof el !== 'object' || !el.type) {
            return '<!-- CAD: skipped non-object or typeless element -->';
        }

        const type = String(el.type).toLowerCase();
        switch (type) {
            case 'rect':
            case 'circle':
            case 'ellipse':
            case 'line':
            case 'polygon':
            case 'polyline':
            case 'path':
                return `<${type} ${this.buildAttrs(el)} />`;
            case 'text':
                // text content needs XML-escaping (not just attribute escaping)
                return `<text ${this.buildAttrs(el)}>${this.escapeText(String(el.text ?? ''))}</text>`;
            default:
                return `<!-- CAD: unsupported element type "${this.escapeText(type)}" -->`;
        }
    }

    /**
     * Build the attribute string for an SVG element. Pass-through for the most
     * common SVG attributes; normalises camelCase → kebab-case for the rest.
     */
    buildAttrs(el) {
        // SVG attributes that already use kebab-case (the camelCase→kebab pass would mangle them).
        const KEBAB_KEYS = new Set([
            'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin',
            'stroke-opacity', 'fill-opacity', 'stop-color', 'stop-opacity',
            'font-family', 'font-size', 'font-weight', 'text-anchor',
            'dominant-baseline', 'alignment-baseline', 'clip-path', 'fill-rule',
            'vector-effect', 'xmlns', 'xmlns:xlink', 'aria-label', 'role'
        ]);

        const parts = [];
        for (const [key, value] of Object.entries(el)) {
            if (key === 'type' || key === 'text') continue;
            const attrName = KEBAB_KEYS.has(key)
                ? key
                : key.replace(/[A-Z]/g, m => '-' + m.toLowerCase());
            parts.push(`${attrName}="${this.escapeAttr(String(value))}"`);
        }
        return parts.join(' ');
    }

    /** Escape a value for use as an SVG attribute (inside double-quotes). */
    escapeAttr(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;');
    }

    /** Escape a value for use as XML text content. */
    escapeText(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.CADRenderer = CADRenderer;
}
