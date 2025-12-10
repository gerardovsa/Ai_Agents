/**
 * CAD RENDERER ENGINEERING EXTENSION
 * ==================================
 * 
 * Extends CAD Renderer to support Design Engineering module delimiters:
 * - ```ENGINEERING_CAD
 * - ```3D_MODEL
 * - ```TECHNICAL_DRAWING
 * - ```BOM
 * 
 * Integrates with existing cad_renderer.js
 */

class EngineeringCADRenderer {
    constructor(cadRenderer) {
        this.cadRenderer = cadRenderer;
        this.vizEngine = cadRenderer.vizEngine;
    }

    /**
     * Parse engineering CAD output with delimiters
     * @param {string} content - Raw content with delimiter blocks
     * @returns {Object} Parsed engineering data
     */
    parseEngineeringContent(content) {
        const result = {
            type: 'engineering_cad',
            metadata: null,
            model3D: null,
            technicalDrawing: null,
            bom: null
        };

        // Extract ENGINEERING_CAD metadata
        const metadataMatch = content.match(/```ENGINEERING_CAD\s*\n([\s\S]*?)\n```/);
        if (metadataMatch) {
            try {
                result.metadata = JSON.parse(metadataMatch[1]);
            } catch (e) {
                console.warn('Failed to parse ENGINEERING_CAD metadata:', e);
            }
        }

        // Extract 3D_MODEL
        const modelMatch = content.match(/```3D_MODEL\s*\n([\s\S]*?)\n```/);
        if (modelMatch) {
            try {
                result.model3D = JSON.parse(modelMatch[1]);
            } catch (e) {
                console.warn('Failed to parse 3D_MODEL:', e);
            }
        }

        // Extract TECHNICAL_DRAWING (SVG)
        const drawingMatch = content.match(/```TECHNICAL_DRAWING\s*\n([\s\S]*?)\n```/);
        if (drawingMatch) {
            result.technicalDrawing = drawingMatch[1].trim();
        }

        // Extract BOM
        const bomMatch = content.match(/```BOM\s*\n([\s\S]*?)\n```/);
        if (bomMatch) {
            try {
                result.bom = JSON.parse(bomMatch[1]);
            } catch (e) {
                console.warn('Failed to parse BOM:', e);
            }
        }

        return result;
    }

    /**
     * Render complete engineering CAD visualization
     * @param {Object} item - Visualization item
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // Parse engineering content
        const engineeringData = this.parseEngineeringContent(item.content);

        // Create tabbed interface for 3D/2D/BOM views
        const container = document.createElement('div');
        container.id = chartId;
        container.className = 'engineering-cad-container';
        container.style.cssText = `
            width: 100%;
            min-height: 600px;
            background: var(--bg-secondary, #2a2a3e);
            border-radius: 8px;
            overflow: hidden;
        `;

        // Create tab navigation
        const tabNav = document.createElement('div');
        tabNav.className = 'engineering-tabs';
        tabNav.style.cssText = `
            display: flex;
            gap: 8px;
            padding: 12px;
            background: var(--bg-primary, #1a1a2e);
            border-bottom: 2px solid var(--border-color, #3a3a4e);
        `;

        const tabs = [
            { id: '3d', label: '🎨 3D Model', hasContent: engineeringData.model3D },
            { id: 'drawing', label: '📐 Technical Drawing', hasContent: engineeringData.technicalDrawing },
            { id: 'bom', label: '📋 Bill of Materials', hasContent: engineeringData.bom }
        ];

        tabs.forEach(tab => {
            if (tab.hasContent) {
                const tabBtn = document.createElement('button');
                tabBtn.className = 'engineering-tab-btn';
                tabBtn.dataset.tab = tab.id;
                tabBtn.textContent = tab.label;
                tabBtn.style.cssText = `
                    padding: 8px 16px;
                    background: var(--bg-tertiary, #2a2a3e);
                    color: var(--text-primary, #e0e0e0);
                    border: 1px solid var(--border-color, #3a3a4e);
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.2s;
                `;

                tabBtn.addEventListener('click', () => {
                    // Update active state
                    tabNav.querySelectorAll('.engineering-tab-btn').forEach(btn => {
                        btn.style.background = 'var(--bg-tertiary, #2a2a3e)';
                        btn.style.borderColor = 'var(--border-color, #3a3a4e)';
                    });
                    tabBtn.style.background = 'var(--accent-primary, #4a90e2)';
                    tabBtn.style.borderColor = 'var(--accent-primary, #4a90e2)';

                    // Show selected tab content
                    container.querySelectorAll('.tab-content').forEach(content => {
                        content.style.display = 'none';
                    });
                    const targetContent = container.querySelector(`[data-tab-content="${tab.id}"]`);
                    if (targetContent) targetContent.style.display = 'block';
                });

                tabNav.appendChild(tabBtn);
            }
        });

        container.appendChild(tabNav);

        // Create tab content areas
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'engineering-content-wrapper';
        contentWrapper.style.padding = '16px';

        // 3D Model Tab
        if (engineeringData.model3D) {
            const model3DContent = document.createElement('div');
            model3DContent.className = 'tab-content';
            model3DContent.dataset.tabContent = '3d';
            model3DContent.style.display = 'block'; // Show first tab by default

            // Render 3D model using existing CAD renderer
            await this.render3DModel(engineeringData.model3D, model3DContent, `${chartId}_3d`);

            contentWrapper.appendChild(model3DContent);
        }

        // Technical Drawing Tab
        if (engineeringData.technicalDrawing) {
            const drawingContent = document.createElement('div');
            drawingContent.className = 'tab-content';
            drawingContent.dataset.tabContent = 'drawing';
            drawingContent.style.display = 'none';
            drawingContent.style.cssText = `
                width: 100%;
                height: 600px;
                overflow: auto;
                background: var(--bg-secondary, #2a2a3e);
                display: flex;
                justify-content: center;
                align-items: center;
            `;

            // Render SVG drawing
            const svgContainer = document.createElement('div');
            svgContainer.innerHTML = engineeringData.technicalDrawing;
            svgContainer.style.cssText = `
                max-width: 100%;
                max-height: 100%;
            `;
            drawingContent.appendChild(svgContainer);

            contentWrapper.appendChild(drawingContent);
        }

        // BOM Tab
        if (engineeringData.bom) {
            const bomContent = document.createElement('div');
            bomContent.className = 'tab-content';
            bomContent.dataset.tabContent = 'bom';
            bomContent.style.display = 'none';

            this.renderBOM(engineeringData.bom, bomContent);

            contentWrapper.appendChild(bomContent);
        }

        container.appendChild(contentWrapper);
        contentArea.appendChild(container);

        // Activate first tab
        const firstTab = tabNav.querySelector('.engineering-tab-btn');
        if (firstTab) firstTab.click();

        return container;
    }

    /**
     * Render 3D model using existing CAD renderer
     */
    async render3DModel(modelConfig, container, chartId) {
        // Ensure Three.js is loaded
        if (!window.THREE) {
            await this.cadRenderer.loadLibrary();
        }

        const width = container.clientWidth || 800;
        const height = 600;

        // Create Three.js scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);

        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.set(
            modelConfig.camera?.position?.x || 0,
            modelConfig.camera?.position?.y || 0,
            modelConfig.camera?.position?.z || 5
        );

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 7.5);
        scene.add(directionalLight);

        // Grid helper
        const gridSize = Math.max(
            modelConfig.dimensions?.width || 10,
            modelConfig.dimensions?.depth || 10
        ) * 2;
        const gridHelper = new THREE.GridHelper(gridSize, 20, 0x444444, 0x222222);
        scene.add(gridHelper);

        // Axes helper
        const axesHelper = new THREE.AxesHelper(gridSize / 4);
        scene.add(axesHelper);

        // Create geometry based on model type
        let geometry, material, mesh;

        if (modelConfig.type === 'box') {
            geometry = new THREE.BoxGeometry(
                modelConfig.dimensions.width,
                modelConfig.dimensions.height,
                modelConfig.dimensions.depth
            );
        } else if (modelConfig.type === 'assembly') {
            // Render assembly with multiple components
            modelConfig.components?.forEach(component => {
                this.createComponent(scene, component);
            });
        }

        if (geometry) {
            material = new THREE.MeshStandardMaterial({
                color: modelConfig.material?.color || 0xC0C0C0,
                metalness: modelConfig.material?.metalness || 0.7,
                roughness: modelConfig.material?.roughness || 0.3
            });

            mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                modelConfig.position?.x || 0,
                modelConfig.position?.y || 0,
                modelConfig.position?.z || 0
            );
            mesh.rotation.set(
                (modelConfig.rotation?.x || 0) * Math.PI / 180,
                (modelConfig.rotation?.y || 0) * Math.PI / 180,
                (modelConfig.rotation?.z || 0) * Math.PI / 180
            );

            scene.add(mesh);

            // Add label
            if (modelConfig.label) {
                console.log(`[3D Model] ${modelConfig.label}`);
            }
        }

        // Controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 1;
        controls.maxDistance = 50;

        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        // Handle resize
        const handleResize = () => {
            const newWidth = container.clientWidth;
            const newHeight = 600;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
        };
        window.addEventListener('resize', handleResize);
    }

    /**
     * Create individual component for assembly
     */
    createComponent(scene, component) {
        let geometry;

        if (component.type === 'box') {
            geometry = new THREE.BoxGeometry(
                component.dimensions.width,
                component.dimensions.height,
                component.dimensions.depth
            );
        }

        if (geometry) {
            const material = new THREE.MeshStandardMaterial({
                color: component.material?.color || 0xC0C0C0,
                metalness: component.material?.metalness || 0.7,
                roughness: component.material?.roughness || 0.3
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                component.position?.x || 0,
                component.position?.y || 0,
                component.position?.z || 0
            );
            mesh.rotation.set(
                (component.rotation?.x || 0) * Math.PI / 180,
                (component.rotation?.y || 0) * Math.PI / 180,
                (component.rotation?.z || 0) * Math.PI / 180
            );

            scene.add(mesh);
        }
    }

    /**
     * Render Bill of Materials table
     */
    renderBOM(bomData, container) {
        const bomWrapper = document.createElement('div');
        bomWrapper.style.cssText = `
            background: var(--bg-primary, #1a1a2e);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
        `;

        const title = document.createElement('h3');
        title.textContent = bomData.description || 'Bill of Materials';
        title.style.cssText = `
            color: var(--text-primary, #e0e0e0);
            margin-bottom: 16px;
            font-size: 18px;
        `;
        bomWrapper.appendChild(title);

        const table = document.createElement('table');
        table.style.cssText = `
            width: 100%;
            border-collapse: collapse;
            color: var(--text-primary, #e0e0e0);
        `;

        // Table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr style="border-bottom: 2px solid var(--border-color, #3a3a4e);">
                <th style="padding: 12px; text-align: left;">Qty</th>
                <th style="padding: 12px; text-align: left;">Part</th>
                <th style="padding: 12px; text-align: left;">Length/Size</th>
                <th style="padding: 12px; text-align: left;">Purpose</th>
            </tr>
        `;
        table.appendChild(thead);

        // Table body
        const tbody = document.createElement('tbody');
        bomData.items?.forEach((item, index) => {
            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid var(--border-color, #2a2a3e)';

            row.innerHTML = `
                <td style="padding: 12px;">${item.qty}</td>
                <td style="padding: 12px; font-weight: 500;">${item.part}</td>
                <td style="padding: 12px;">${item.length_mm ? item.length_mm + 'mm' : '-'}</td>
                <td style="padding: 12px; color: var(--text-secondary, #b0b0b0);">${item.purpose || '-'}</td>
            `;

            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        bomWrapper.appendChild(table);
        container.appendChild(bomWrapper);
    }
}

// Auto-integrate with existing CAD Renderer
if (typeof CADRenderer !== 'undefined') {
    const originalRender = CADRenderer.prototype.render;

    CADRenderer.prototype.render = async function (item, contentArea, chartId) {
        // Check if content contains engineering delimiters
        if (typeof item.content === 'string' &&
            (item.content.includes('```ENGINEERING_CAD') ||
                item.content.includes('```3D_MODEL') ||
                item.content.includes('```TECHNICAL_DRAWING'))) {

            console.log('✅ Engineering CAD content detected, using EngineeringCADRenderer');
            const engRenderer = new EngineeringCADRenderer(this);
            return await engRenderer.render(item, contentArea, chartId);
        }

        // Fall back to original renderer for standard CAD content
        return await originalRender.call(this, item, contentArea, chartId);
    };

    console.log('✅ EngineeringCADRenderer integrated with CADRenderer');
}
