/**
 * CAD Chat Renderer - Renders STEP/STL files in chat messages
 * 
 * Detects when AI generates CAD using CadQuery and automatically renders
 * the 3D model inline in the chat.
 * 
 * Usage:
 *   <div class="cad-render" data-step-file="path/to/file.step"></div>
 *   OR
 *   <div class="cad-render" data-stl-file="path/to/file.stl"></div>
 */

class CADChatRenderer {
    constructor() {
        this.viewers = new Map();
        this.occReady = false;
        this.initOpenCascade();
    }

    async initOpenCascade() {
        // Load OpenCascade.js for STEP file support
        if (typeof OpenCascadeInstance === 'undefined') {
            const script = document.createElement('script');
            script.src = '/modules_external/opencascade.js/opencascade.wasm.js';
            script.onload = () => {
                OpenCascadeInstance.then(occ => {
                    window.occ = occ;
                    this.occReady = true;
                    console.log('[CADChatRenderer] OpenCascade.js ready');
                    this.processPendingRenderers();
                });
            };
            document.head.appendChild(script);
        } else {
            this.occReady = true;
        }

        // Load Three.js if not already loaded
        if (typeof THREE === 'undefined') {
            await this.loadScript('/modules_external/three.min.js');
        }

        // Load STL loader
        if (typeof THREE.STLLoader === 'undefined') {
            await this.loadScript('/modules_external/STLLoader.js');
        }
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Render CAD file in a container
     * 
     * @param {HTMLElement} container - Container div with data-step-file or data-stl-file
     */
    async render(container) {
        const stepFile = container.dataset.stepFile;
        const stlFile = container.dataset.stlFile;
        const description = container.dataset.description || 'CAD Model';

        if (!stepFile && !stlFile) {
            console.error('[CADChatRenderer] No file specified');
            return;
        }

        // Create viewer UI
        container.innerHTML = `
            <div class="cad-viewer-container">
                <div class="cad-viewer-header">
                    <span class="cad-title">🔧 ${description}</span>
                    <div class="cad-controls">
                        <button class="cad-btn" data-action="rotate">🔄 Rotate</button>
                        <button class="cad-btn" data-action="zoom-fit">📐 Fit</button>
                        <button class="cad-btn" data-action="fullscreen">⛶ Fullscreen</button>
                    </div>
                </div>
                <div class="cad-viewport" style="width: 100%; height: 400px; background: #2a2a2a;">
                    <div class="cad-loading">Loading 3D model...</div>
                </div>
                <div class="cad-info">
                    <span class="cad-stats"></span>
                </div>
            </div>
        `;

        const viewport = container.querySelector('.cad-viewport');
        const loadingDiv = viewport.querySelector('.cad-loading');
        const statsSpan = container.querySelector('.cad-stats');

        try {
            // Initialize Three.js scene
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x2a2a2a);

            const camera = new THREE.PerspectiveCamera(
                45,
                viewport.clientWidth / viewport.clientHeight,
                0.1,
                10000
            );

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(viewport.clientWidth, viewport.clientHeight);
            viewport.appendChild(renderer.domElement);
            loadingDiv.remove();

            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(1, 1, 1);
            scene.add(directionalLight);

            // Load geometry
            let geometry;
            if (stlFile) {
                geometry = await this.loadSTL(stlFile);
            } else if (stepFile) {
                geometry = await this.loadSTEP(stepFile);
            }

            // Create mesh
            const material = new THREE.MeshPhongMaterial({
                color: 0x4a90e2,
                specular: 0x111111,
                shininess: 30
            });
            const mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);

            // Add wireframe
            const wireframe = new THREE.WireframeGeometry(geometry);
            const line = new THREE.LineSegments(wireframe);
            line.material.color.setHex(0x000000);
            line.material.opacity = 0.1;
            line.material.transparent = true;
            mesh.add(line);

            // Position camera
            const bbox = new THREE.Box3().setFromObject(mesh);
            const center = bbox.getCenter(new THREE.Vector3());
            const size = bbox.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            const cameraDistance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;

            camera.position.set(
                center.x + cameraDistance,
                center.y + cameraDistance,
                center.z + cameraDistance
            );
            camera.lookAt(center);

            // Controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.target.copy(center);
            controls.update();

            // Stats
            const vertexCount = geometry.attributes.position.count;
            const faceCount = geometry.index ? geometry.index.count / 3 : vertexCount / 3;
            statsSpan.textContent = `${vertexCount.toLocaleString()} vertices • ${Math.floor(faceCount).toLocaleString()} faces • ${size.x.toFixed(1)}×${size.y.toFixed(1)}×${size.z.toFixed(1)} mm`;

            // Animation loop
            const animate = () => {
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            };
            animate();

            // Button handlers
            container.querySelector('[data-action="rotate"]').onclick = () => {
                mesh.rotation.y += Math.PI / 4;
            };

            container.querySelector('[data-action="zoom-fit"]').onclick = () => {
                camera.position.set(
                    center.x + cameraDistance,
                    center.y + cameraDistance,
                    center.z + cameraDistance
                );
                camera.lookAt(center);
                controls.target.copy(center);
                controls.update();
            };

            container.querySelector('[data-action="fullscreen"]').onclick = () => {
                if (viewport.requestFullscreen) {
                    viewport.requestFullscreen();
                }
            };

            // Store viewer reference
            this.viewers.set(container, { scene, camera, renderer, controls, mesh });

            console.log('[CADChatRenderer] Model rendered successfully');

        } catch (error) {
            console.error('[CADChatRenderer] Render error:', error);
            viewport.innerHTML = `<div class="cad-error">Failed to load model: ${error.message}</div>`;
        }
    }

    async loadSTL(filePath) {
        return new Promise((resolve, reject) => {
            const loader = new THREE.STLLoader();
            loader.load(
                filePath,
                (geometry) => {
                    geometry.computeVertexNormals();
                    resolve(geometry);
                },
                undefined,
                reject
            );
        });
    }

    async loadSTEP(filePath) {
        if (!this.occReady) {
            throw new Error('OpenCascade.js not ready');
        }

        // Fetch STEP file
        const response = await fetch(filePath);
        const arrayBuffer = await response.arrayBuffer();

        // Read STEP with OpenCascade
        const uint8Array = new Uint8Array(arrayBuffer);
        const stepString = new TextDecoder().decode(uint8Array);

        // Parse STEP (simplified - real implementation would use OCC's STEPControl_Reader)
        // For now, convert to STL on backend and load that
        const stlPath = filePath.replace('.step', '.stl');
        return this.loadSTL(stlPath);
    }

    processPendingRenderers() {
        // Find all unprocessed CAD render containers
        document.querySelectorAll('.cad-render:not(.cad-processed)').forEach(container => {
            container.classList.add('cad-processed');
            this.render(container);
        });
    }

    /**
     * Create CAD renderer from tool result
     * 
     * @param {Object} result - Result from generate_cad_from_code tool
     * @returns {HTMLElement} Container element ready to insert in chat
     */
    static createFromToolResult(result) {
        if (!result.success) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'cad-error';
            errorDiv.innerHTML = `
                <strong>CAD Generation Failed</strong>
                <pre>${result.error}</pre>
            `;
            return errorDiv;
        }

        const container = document.createElement('div');
        container.className = 'cad-render';
        container.dataset.stlFile = result.stl_file;
        container.dataset.stepFile = result.step_file;
        container.dataset.description = result.description || 'CAD Model';

        // Add stats as data attributes
        if (result.vertices) container.dataset.vertices = result.vertices;
        if (result.faces) container.dataset.faces = result.faces;
        if (result.volume) container.dataset.volume = result.volume;

        return container;
    }
}

// Auto-initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.cadChatRenderer = new CADChatRenderer();
    });
} else {
    window.cadChatRenderer = new CADChatRenderer();
}

// Add CSS
const style = document.createElement('style');
style.textContent = `
.cad-viewer-container {
    border: 1px solid #444;
    border-radius: 8px;
    overflow: hidden;
    margin: 10px 0;
    background: #1a1a1a;
}

.cad-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background: #2d2d2d;
    border-bottom: 1px solid #444;
}

.cad-title {
    font-weight: 600;
    color: #fff;
}

.cad-controls {
    display: flex;
    gap: 8px;
}

.cad-btn {
    padding: 5px 10px;
    background: #3a3a3a;
    border: 1px solid #555;
    border-radius: 4px;
    color: #fff;
    cursor: pointer;
    font-size: 12px;
}

.cad-btn:hover {
    background: #4a4a4a;
}

.cad-viewport {
    position: relative;
}

.cad-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #888;
    font-size: 14px;
}

.cad-info {
    padding: 8px 15px;
    background: #2d2d2d;
    border-top: 1px solid #444;
    font-size: 12px;
    color: #aaa;
}

.cad-error {
    padding: 15px;
    background: #3a1a1a;
    border: 1px solid #6a2a2a;
    border-radius: 4px;
    color: #ff6b6b;
}

.cad-error strong {
    display: block;
    margin-bottom: 8px;
}

.cad-error pre {
    background: #2a1a1a;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
}
`;
document.head.appendChild(style);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CADChatRenderer;
}
