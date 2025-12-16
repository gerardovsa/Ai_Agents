/**
 * Streaming CAD Renderer
 * Real-time partial rendering as AI generates CAD data
 * Based on OpenAI's streaming image generation pattern
 */

class StreamingCADRenderer {
    constructor(scene, camera, renderer) {
        this.scene = scene;
        this.camera = camera;
        this.renderer = renderer;

        // Streaming state
        this.isStreaming = false;
        this.currentMesh = null;
        this.progressIndicator = null;

        // Progress stages
        this.stages = [
            { name: 'profile', label: 'Loading profile...', progress: 0.2 },
            { name: 'dimensions', label: 'Calculating dimensions...', progress: 0.4 },
            { name: 'geometry', label: 'Generating geometry...', progress: 0.6 },
            { name: 'tessellation', label: 'Tessellating mesh...', progress: 0.8 },
            { name: 'rendering', label: 'Rendering visualization...', progress: 1.0 }
        ];

        this.currentStage = 0;

        // Callbacks
        this.onProgress = null;
        this.onComplete = null;
        this.onError = null;
    }

    /**
     * Start streaming CAD generation
     * @param {object} options - { userRequest, progressCallback, completeCallback }
     */
    async startStreaming(options = {}) {
        this.isStreaming = true;
        this.currentStage = 0;

        this.onProgress = options.progressCallback;
        this.onComplete = options.completeCallback;
        this.onError = options.errorCallback;

        try {
            // Show progress indicator
            this.showProgressIndicator();

            // Stream through each stage
            for (let i = 0; i < this.stages.length; i++) {
                const stage = this.stages[i];
                this.currentStage = i;

                // Update progress UI
                this.updateProgress(stage.label, stage.progress);

                // Notify callback
                if (this.onProgress) {
                    this.onProgress({
                        stage: stage.name,
                        label: stage.label,
                        progress: stage.progress
                    });
                }

                // Render partial result
                await this.renderPartialStage(stage.name, options);

                // Delay for visual feedback
                await this.delay(300);
            }

            // Complete
            this.isStreaming = false;
            this.hideProgressIndicator();

            if (this.onComplete) {
                this.onComplete(this.currentMesh);
            }

        } catch (error) {
            this.isStreaming = false;
            this.hideProgressIndicator();

            if (this.onError) {
                this.onError(error);
            }

            console.error('[Streaming] Error:', error);
        }
    }

    /**
     * Render partial stage
     * @param {string} stageName - Stage identifier
     * @param {object} options - Rendering options
     */
    async renderPartialStage(stageName, options) {
        switch (stageName) {
            case 'profile':
                await this.renderProfileStage(options);
                break;

            case 'dimensions':
                await this.renderDimensionsStage(options);
                break;

            case 'geometry':
                await this.renderGeometryStage(options);
                break;

            case 'tessellation':
                await this.renderTessellationStage(options);
                break;

            case 'rendering':
                await this.renderFinalStage(options);
                break;
        }
    }

    /**
     * Stage 1: Show profile wireframe
     */
    async renderProfileStage(options) {
        // Create simple wireframe box representing profile
        const geometry = new THREE.BoxGeometry(0.02, 0.02, 0.1);
        const edges = new THREE.EdgesGeometry(geometry);
        const material = new THREE.LineBasicMaterial({
            color: 0x00ff00,
            linewidth: 2,
            opacity: 0.5,
            transparent: true
        });

        const wireframe = new THREE.LineSegments(edges, material);
        wireframe.name = 'streaming-wireframe';

        // Remove previous mesh
        this.removeStreamingMeshes();

        // Add to scene
        this.scene.add(wireframe);
        this.currentMesh = wireframe;

        // Animate fade in
        this.animateFadeIn(wireframe);

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Stage 2: Update dimensions
     */
    async renderDimensionsStage(options) {
        // Scale existing wireframe to correct dimensions
        if (this.currentMesh && options.dimensions) {
            const dims = options.dimensions;

            // Animate scale change
            await this.animateScale(
                this.currentMesh,
                {
                    x: dims.width / 0.02,
                    y: dims.height / 0.02,
                    z: (dims.depth || options.length || 0.5) / 0.1
                }
            );
        }

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Stage 3: Generate geometry (low-poly preview)
     */
    async renderGeometryStage(options) {
        // Create low-poly preview mesh
        const geometry = new THREE.BoxGeometry(
            options.dimensions?.width || 0.02,
            options.dimensions?.height || 0.02,
            options.dimensions?.depth || options.length || 0.5,
            2, 2, 2  // Low segment count for preview
        );

        const material = new THREE.MeshPhongMaterial({
            color: 0x2196F3,
            opacity: 0.7,
            transparent: true,
            flatShading: true
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = 'streaming-preview';

        // Remove wireframe
        this.removeStreamingMeshes();

        // Add mesh
        this.scene.add(mesh);
        this.currentMesh = mesh;

        // Animate fade in
        this.animateFadeIn(mesh);

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Stage 4: Tessellation (high-poly mesh)
     */
    async renderTessellationStage(options) {
        // Replace with high-poly mesh
        const geometry = new THREE.BoxGeometry(
            options.dimensions?.width || 0.02,
            options.dimensions?.height || 0.02,
            options.dimensions?.depth || options.length || 0.5,
            20, 20, 20  // High segment count
        );

        const material = new THREE.MeshPhongMaterial({
            color: 0x2196F3,
            opacity: 0.9,
            transparent: true,
            flatShading: false
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = 'streaming-hires';

        // Smooth transition from low-poly to high-poly
        const oldMesh = this.currentMesh;

        this.scene.add(mesh);
        this.currentMesh = mesh;

        // Cross-fade
        if (oldMesh) {
            await this.animateCrossFade(oldMesh, mesh);
            this.scene.remove(oldMesh);
        }

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Stage 5: Final rendering (materials, lighting)
     */
    async renderFinalStage(options) {
        // Update to final material
        if (this.currentMesh) {
            const finalMaterial = new THREE.MeshStandardMaterial({
                color: 0x2196F3,
                metalness: 0.8,
                roughness: 0.2,
                opacity: 1.0,
                transparent: false
            });

            this.currentMesh.material = finalMaterial;
            this.currentMesh.name = 'cad-final';

            // Animate material transition
            await this.animateMaterialTransition(this.currentMesh);
        }

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Show progress indicator in scene
     */
    showProgressIndicator() {
        // Create progress bar in 3D space
        const barGeometry = new THREE.PlaneGeometry(2, 0.1);
        const barMaterial = new THREE.MeshBasicMaterial({
            color: 0x4CAF50,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.8
        });

        this.progressIndicator = new THREE.Mesh(barGeometry, barMaterial);
        this.progressIndicator.position.set(0, -1, 0);
        this.progressIndicator.name = 'progress-indicator';
        this.progressIndicator.scale.x = 0;  // Start at 0%

        this.scene.add(this.progressIndicator);
    }

    /**
     * Update progress indicator
     * @param {string} label - Progress label
     * @param {number} progress - Progress (0-1)
     */
    updateProgress(label, progress) {
        console.log(`[Streaming] ${label} (${(progress * 100).toFixed(0)}%)`);

        // Update 3D progress bar
        if (this.progressIndicator) {
            this.progressIndicator.scale.x = progress;
        }

        // Update DOM progress (if exists)
        const progressBar = document.getElementById('cad-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress * 100}%`;
        }

        const progressLabel = document.getElementById('cad-progress-label');
        if (progressLabel) {
            progressLabel.textContent = label;
        }
    }

    /**
     * Hide progress indicator
     */
    hideProgressIndicator() {
        if (this.progressIndicator) {
            this.scene.remove(this.progressIndicator);
            this.progressIndicator = null;
        }
    }

    /**
     * Remove streaming meshes from scene
     */
    removeStreamingMeshes() {
        const toRemove = [];

        this.scene.traverse(obj => {
            if (obj.name && obj.name.startsWith('streaming-')) {
                toRemove.push(obj);
            }
        });

        toRemove.forEach(obj => this.scene.remove(obj));
    }

    /**
     * Animate fade in
     * @param {THREE.Object3D} object - Object to fade in
     */
    async animateFadeIn(object) {
        const duration = 300;
        const startTime = Date.now();

        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                if (object.material) {
                    object.material.opacity = progress;
                }

                this.renderer.render(this.scene, this.camera);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };

            animate();
        });
    }

    /**
     * Animate scale change
     * @param {THREE.Object3D} object - Object to scale
     * @param {object} targetScale - Target scale {x, y, z}
     */
    async animateScale(object, targetScale) {
        const duration = 500;
        const startTime = Date.now();
        const startScale = { ...object.scale };

        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = this.easeInOutCubic(progress);

                object.scale.x = startScale.x + (targetScale.x - startScale.x) * eased;
                object.scale.y = startScale.y + (targetScale.y - startScale.y) * eased;
                object.scale.z = startScale.z + (targetScale.z - startScale.z) * eased;

                this.renderer.render(this.scene, this.camera);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };

            animate();
        });
    }

    /**
     * Animate cross-fade between meshes
     * @param {THREE.Object3D} fromMesh - Mesh to fade out
     * @param {THREE.Object3D} toMesh - Mesh to fade in
     */
    async animateCrossFade(fromMesh, toMesh) {
        const duration = 500;
        const startTime = Date.now();

        // Set initial opacities
        if (fromMesh.material) fromMesh.material.opacity = 1;
        if (toMesh.material) toMesh.material.opacity = 0;

        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                if (fromMesh.material) {
                    fromMesh.material.opacity = 1 - progress;
                }

                if (toMesh.material) {
                    toMesh.material.opacity = progress;
                }

                this.renderer.render(this.scene, this.camera);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };

            animate();
        });
    }

    /**
     * Animate material transition
     * @param {THREE.Object3D} object - Object to transition
     */
    async animateMaterialTransition(object) {
        const duration = 500;
        const startTime = Date.now();

        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Pulse effect
                const pulse = Math.sin(progress * Math.PI);
                if (object.material) {
                    object.material.emissive = new THREE.Color(0x4CAF50);
                    object.material.emissiveIntensity = pulse * 0.5;
                }

                this.renderer.render(this.scene, this.camera);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    if (object.material) {
                        object.material.emissiveIntensity = 0;
                    }
                    resolve();
                }
            };

            animate();
        });
    }

    /**
     * Easing function
     */
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    /**
     * Delay helper
     * @param {number} ms - Milliseconds to delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Stop streaming
     */
    stop() {
        this.isStreaming = false;
        this.hideProgressIndicator();
        this.removeStreamingMeshes();
    }
}

// Export for module use
window.StreamingCADRenderer = StreamingCADRenderer;
