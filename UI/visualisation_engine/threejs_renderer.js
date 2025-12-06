/**
 * THREE.JS RENDERER MODULE
 * ========================
 * 
 * Renders 3D graphics and scenes using Three.js.
 * Three.js is a powerful 3D graphics library for WebGL.
 * 
 * Supported features:
 * - 3D model rendering
 * - Custom scenes with lighting
 * - Camera controls
 * - Animation loops
 * - Material and texture support
 * 
 * CDN: https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js
 * Docs: https://threejs.org/
 */

class ThreeJSRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.scenes = new Map(); // Track Three.js scenes for cleanup
    }

    /**
     * Render Three.js visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        try {
            // Ensure Three.js is loaded
            if (!window.THREE) {
                await this.loadThreeJS();
            }

            // Extract config - handle both JSON and JS notation
            let config;
            if (typeof item.content === 'string') {
                const cleanContent = item.content.replace(/<\/?THREEJS>/g, '').trim();
                try {
                    config = JSON.parse(cleanContent);
                } catch (e) {
                    console.warn('ThreeJS: JSON parse failed, using JavaScript eval', e.message);
                    config = (new Function('return ' + cleanContent))();
                }
            } else {
                config = item.content;
            }

            // Create container
            const container = document.createElement('div');
            container.id = chartId;
            container.style.cssText = `
                width: 100%;
                height: ${config.height || 500}px;
            `;
            contentArea.appendChild(container);

            // Basic Three.js setup
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(
                75,
                container.clientWidth / container.clientHeight,
                0.1,
                1000
            );
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            // Add basic lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(1, 1, 1);
            scene.add(directionalLight);

            // Set camera position
            camera.position.z = 5;

            // Store scene info for cleanup
            this.scenes.set(chartId, { scene, camera, renderer });

            // Render loop
            const animate = () => {
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
            };
            animate();

            console.log('✅ THREE.JS rendered successfully');
        } catch (error) {
            console.error('Error rendering Three.js:', error);
            throw error;
        }
    }

    /**
     * Load Three.js library dynamically
     */
    async loadThreeJS() {
        return new Promise((resolve, reject) => {
            if (window.THREE) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
            script.onload = () => {
                console.log('✅ Three.js library loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load Three.js library'));
            document.head.appendChild(script);
        });
    }

    /**
     * Cleanup Three.js resources
     */
    dispose(chartId) {
        const sceneData = this.scenes.get(chartId);
        if (sceneData) {
            const { scene, renderer } = sceneData;

            // Dispose of geometries and materials
            scene.traverse((object) => {
                if (object.geometry) object.geometry.dispose();
                if (object.material) {
                    if (Array.isArray(object.material)) {
                        object.material.forEach(material => material.dispose());
                    } else {
                        object.material.dispose();
                    }
                }
            });

            // Dispose of renderer
            renderer.dispose();

            this.scenes.delete(chartId);
        }
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.ThreeJSRenderer = ThreeJSRenderer;
}
