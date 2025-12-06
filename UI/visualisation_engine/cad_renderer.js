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
        // Ensure Three.js library is loaded
        if (!window.THREE) {
            await this.loadLibrary();
        }

        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('CAD: Invalid content area');
        }

        // Parse configuration
        let config = typeof item.content === 'string' 
            ? JSON.parse(item.content.replace(/<\/?CAD>/g, '').trim())
            : item.content;

        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;
        const defaultBg = colors ? colors.background : '#1a1a2e';

        // Create container
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

        // Scene setup with dynamic background
        const scene = new THREE.Scene();
        const bgColor = config.background || (colors ? colors.background : '#1a1a2e');
        scene.background = new THREE.Color(bgColor);

        // Camera setup
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = config.cameraDistance || 5;

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

        // Grid helper
        if (config.showGrid !== false) {
            const gridHelper = new THREE.GridHelper(10, 10);
            scene.add(gridHelper);
        }

        // Axes helper
        if (config.showAxes !== false) {
            const axesHelper = new THREE.AxesHelper(5);
            scene.add(axesHelper);
        }

        // Load CAD model
        if (config.geometry) {
            await this.loadGeometry(scene, config.geometry, config);
        }

        // Controls (orbit)
        let controls = null;
        if (window.THREE.OrbitControls) {
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
        }

        // Handle window resize
        const handleResize = () => {
            const newWidth = container.clientWidth;
            const newHeight = container.clientHeight;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
        };
        window.addEventListener('resize', handleResize);

        return {
            scene,
            camera,
            renderer,
            controls,
            container,
            handleResize
        };
    }

    /**
     * Load CAD geometry
     */
    async loadGeometry(scene, geometryConfig, config) {
        // For now, create a simple geometric shape as placeholder
        // TODO: Add loaders for STEP, IGES, STL, OBJ formats
        
        const geometry = new THREE.BoxGeometry(
            geometryConfig.width || 1,
            geometryConfig.height || 1,
            geometryConfig.depth || 1
        );

        const material = new THREE.MeshStandardMaterial({
            color: geometryConfig.color || 0x00ff00,
            metalness: geometryConfig.metalness || 0.3,
            roughness: geometryConfig.roughness || 0.7
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

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
            sceneData.camera.position.set(0, 0, 5);
            if (sceneData.controls) {
                sceneData.controls.reset();
            }
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
     */
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.THREE) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
            script.onload = async () => {
                // Load OrbitControls
                const controlsScript = document.createElement('script');
                controlsScript.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js';
                controlsScript.onload = () => {
                    console.log('✅ Three.js and OrbitControls loaded');
                    resolve();
                };
                document.head.appendChild(controlsScript);
            };
            script.onerror = () => reject(new Error('Failed to load Three.js library'));
            document.head.appendChild(script);
        });
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
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.CADRenderer = CADRenderer;
}
