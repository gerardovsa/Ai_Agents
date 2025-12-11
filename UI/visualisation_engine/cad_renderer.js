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
 * CDN: https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js
 * Docs: https://threejs.org/
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
        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('CAD: Invalid content area');
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
                // Try JSON first (3D model config)
                try {
                    config = JSON.parse(cleanContent);
                } catch (e) {
                    console.warn('CAD: JSON parse failed, trying JavaScript eval');
                    config = (new Function('return ' + cleanContent))();
                }
            }
        } else {
            config = item.content;
        }

        // If SVG, render as 2D drawing instead of 3D model (NO Three.js needed)
        if (isSVG) {
            return this.renderSVGDrawing(config.svg, contentArea, chartId);
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
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'cad');
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
            camera.position.z = config.cameraDistance || 5;
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
 * Add view controls to action bar
 */
addViewControls(vizContainer, sceneData, chartId) {
    const actionBar = vizContainer.querySelector('.viz-unified-action-bar');
    if (!actionBar) return;

    // Reset view button
    const resetBtn = document.createElement('button');
    resetBtn.className = 'viz-action-btn cad-reset-view';
    resetBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 3V1L4 5l4 4V7c2.2 0 4 1.8 4 4 0 .5-.1 1-.3 1.4l1.5 1.5c.5-.9.8-1.9.8-2.9 0-3.3-2.7-6-6-6z"/>
            </svg>
        `;
    resetBtn.title = 'Reset Camera View';

    resetBtn.addEventListener('click', () => {
        // Reset to initial camera position
        if (sceneData.initialCameraPos) {
            sceneData.camera.position.copy(sceneData.initialCameraPos);
        } else {
            // Fallback to default position
            sceneData.camera.position.set(0, 0, 5);
        }

        // Reset controls target to origin
        if (sceneData.controls) {
            if (sceneData.initialControlsTarget) {
                sceneData.controls.target.copy(sceneData.initialControlsTarget);
            } else {
                sceneData.controls.target.set(0, 0, 0);
            }
            sceneData.controls.update();
        }

        console.log('✅ CAD: Camera reset to initial position');
    });

    // Insert before close button
    const closeBtn = actionBar.querySelector('.viz-action-btn:last-child');
    if (closeBtn) {
        actionBar.insertBefore(resetBtn, closeBtn);
    } else {
        actionBar.appendChild(resetBtn);
    }
}

    /**
     * Load Three.js library dynamically
     * FIXED (Dec 11, 2025): Use UMD builds instead of ES6 modules to avoid import errors
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

        // Load Three.js core from relative path (works on any deployment)
        const threeScript = document.createElement('script');
        threeScript.src = 'js/vendor/three.min.js'; // Relative to site root

        threeScript.onload = () => {
            console.log('✅ [CAD] Three.js core loaded');

            if (window.THREE) {
                // Initialize OrbitControls inline (simplified version)
                this.initOrbitControls();
                clearTimeout(timeoutId);
                resolved = true;
                console.log('✅ [CAD] Three.js fully initialized and ready');
                resolve();
            } else {
                clearTimeout(timeoutId);
                reject(new Error('Three.js loaded but not available'));
            }
        };

        threeScript.onerror = (e) => {
            clearTimeout(timeoutId);
            console.error('❌ [CAD] Failed to load Three.js:', e);
            reject(new Error('Failed to load Three.js from CDN'));
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

    // Insert SVG content
    try {
        svgContainer.innerHTML = cleanSvg;
        console.log('✅ CAD: SVG content inserted into DOM');
    } catch (error) {
        console.error('❌ CAD: Failed to insert SVG:', error);
        svgContainer.innerHTML = '<div style="padding: 20px; color: red;">Error: Failed to render SVG drawing</div>';
    }

    // Make SVG responsive and fix title/desc overlay issues
    const svgElement = svgContainer.querySelector('svg');
    if (svgElement) {
        if (!svgElement.hasAttribute('width')) {
            svgElement.style.width = '100%';
            svgElement.style.height = 'auto';
        }

        // FIXED (Dec 11, 2025): Hide SVG <title> and <desc> elements
        // These are metadata/accessibility elements, not meant to be visually rendered
        // They were overlaying the actual drawing content
        const metadataElements = svgElement.querySelectorAll('title, desc');
        metadataElements.forEach(el => {
            el.style.display = 'none'; // Hide metadata elements
        });

        console.log('✅ CAD: SVG element found and styled');
        if (metadataElements.length > 0) {
            console.log(`✅ CAD: Hidden ${metadataElements.length} metadata elements (title/desc)`);
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
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.CADRenderer = CADRenderer;
}
