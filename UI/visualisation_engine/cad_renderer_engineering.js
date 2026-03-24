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
     * Parse engineering CAD output - SINGLE <CAD> TAG
     * @param {string} content - Raw content with <CAD> delimiter
     * @returns {Object} Parsed engineering data
     */
    parseEngineeringContent(content) {
        const result = {
            type: 'engineering_cad',
            metadata: null,
            model3D: null,
            technicalDrawing: null,
            bom: null,
            constraintsInfo: null
        };

        console.log('[EngineeringCAD] Parsing content...');

        // Extract single <CAD> block
        const cadMatch = content.match(/<CAD>([\s\S]*?)<\/CAD>/);
        if (cadMatch) {
            console.log('[EngineeringCAD] Found <CAD> delimiter');
            try {
                const cadData = JSON.parse(cadMatch[1]);
                console.log('[EngineeringCAD] JSON parsed successfully');
                console.log('[EngineeringCAD] Type:', cadData.type);

                // Check if it's constrained engineering CAD
                if (cadData.type === 'constrained_engineering_cad') {
                    console.log('✅ [EngineeringCAD] Detected constrained engineering CAD format');
                    // Unpack embedded data
                    result.metadata = {
                        type: cadData.type,
                        profile: cadData.profile,
                        dimensions: cadData.dimensions,
                        solver: cadData.solver
                    };
                    result.model3D = cadData.model3D;
                    result.technicalDrawing = cadData.technical_drawing;
                    result.constraintsInfo = cadData.constraints;

                    console.log('[EngineeringCAD] Components found:', {
                        hasModel3D: !!result.model3D,
                        hasTechnicalDrawing: !!result.technicalDrawing,
                        hasConstraints: !!result.constraintsInfo
                    });
                } else {
                    console.log('⚠️ [EngineeringCAD] Regular CAD format (no type field)');
                    // Regular CAD - just 3D model
                    result.model3D = cadData;
                }
            } catch (e) {
                console.error('❌ [EngineeringCAD] Failed to parse CAD JSON:', e);
                console.error('[EngineeringCAD] Content preview:', cadMatch[1].substring(0, 200));
            }
        } else {
            console.warn('⚠️ [EngineeringCAD] No <CAD> delimiter found in content');
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
            { id: 'bom', label: '📋 Bill of Materials', hasContent: engineeringData.bom },
            { id: 'constraints', label: '✓ Constraints', hasContent: engineeringData.constraintsInfo }
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

        // Constraints Tab (new)
        if (engineeringData.constraintsInfo) {
            const constraintsContent = document.createElement('div');
            constraintsContent.className = 'tab-content';
            constraintsContent.dataset.tabContent = 'constraints';
            constraintsContent.style.display = 'none';
            constraintsContent.style.cssText = `
                padding: 20px;
                background: var(--bg-secondary, #2a2a3e);
                color: var(--text-primary, #e0e0e0);
                overflow: auto;
                max-height: 600px;
            `;

            this.renderConstraintsInfo(engineeringData.constraintsInfo, constraintsContent);

            contentWrapper.appendChild(constraintsContent);
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
        // Default to isometric \"home\" view if no custom position specified
        if (modelConfig.camera?.position) {
            camera.position.set(
                modelConfig.camera.position.x,
                modelConfig.camera.position.y,
                modelConfig.camera.position.z
            );
        } else {
            const distance = 5;
            camera.position.set(distance * 0.7, distance * 0.7, distance * 0.7);
        }

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
            // Render assembly with multiple components or layers (both naming conventions supported)
            const parts = modelConfig.components || modelConfig.layers || [];
            parts.forEach(component => {
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

        // Support both explicit type='box' and layer objects which are implicitly box-shaped
        const isBoxLike = component.type === 'box' || (!component.type && component.dimensions);

        if (isBoxLike) {
            geometry = new THREE.BoxGeometry(
                component.dimensions.width,
                component.dimensions.height,
                component.dimensions.depth
            );
        }

        if (geometry) {
            // Support color as direct integer (layers format) or nested under material
            const colorValue = component.color !== undefined ? component.color
                : (component.material?.color !== undefined ? component.material.color : 0xC0C0C0);
            const opacityValue = component.opacity !== undefined ? component.opacity : 1.0;
            const isTransparent = opacityValue < 1.0;

            const material = new THREE.MeshStandardMaterial({
                color: colorValue,
                metalness: component.material?.metalness || 0.3,
                roughness: component.material?.roughness || 0.7,
                transparent: isTransparent,
                opacity: opacityValue
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

    /**
     * Render constraints information panel
     */
    renderConstraintsInfo(constraintsData, container) {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = `
            background: var(--bg-tertiary, #1a1a2e);
            border-radius: 8px;
            padding: 24px;
        `;

        // Title with badge
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--accent-primary, #4a90e2);
        `;

        const title = document.createElement('h3');
        title.textContent = 'Geometric Constraints';
        title.style.cssText = `
            color: var(--text-primary, #e0e0e0);
            font-size: 20px;
            margin: 0;
        `;

        const badge = document.createElement('span');
        badge.textContent = constraintsData.accuracy;
        badge.style.cssText = `
            background: var(--success-color, #28a745);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        `;

        header.appendChild(title);
        header.appendChild(badge);
        wrapper.appendChild(header);

        // Validation status
        const validationSection = document.createElement('div');
        validationSection.style.marginBottom = '24px';

        const validationTitle = document.createElement('h4');
        validationTitle.textContent = '✓ Validation Results';
        validationTitle.style.cssText = `
            color: var(--text-primary, #e0e0e0);
            font-size: 16px;
            margin: 0 0 12px 0;
        `;
        validationSection.appendChild(validationTitle);

        const validationGrid = document.createElement('div');
        validationGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        `;

        Object.entries(constraintsData.validation || {}).forEach(([key, value]) => {
            const item = document.createElement('div');
            item.style.cssText = `
                background: ${value ? 'rgba(40, 167, 69, 0.1)' : 'rgba(220, 53, 69, 0.1)'};
                border: 1px solid ${value ? '#28a745' : '#dc3545'};
                border-radius: 6px;
                padding: 12px;
            `;

            const label = document.createElement('div');
            label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            label.style.cssText = `
                color: var(--text-secondary, #b0b0b0);
                font-size: 12px;
                margin-bottom: 4px;
            `;

            const status = document.createElement('div');
            status.textContent = value ? '✓ Passed' : '✗ Failed';
            status.style.cssText = `
                color: ${value ? '#28a745' : '#dc3545'};
                font-weight: 600;
                font-size: 14px;
            `;

            item.appendChild(label);
            item.appendChild(status);
            validationGrid.appendChild(item);
        });

        validationSection.appendChild(validationGrid);
        wrapper.appendChild(validationSection);

        // Constraints list
        const constraintsSection = document.createElement('div');

        const constraintsTitle = document.createElement('h4');
        constraintsTitle.textContent = '📏 Applied Constraints';
        constraintsTitle.style.cssText = `
            color: var(--text-primary, #e0e0e0);
            font-size: 16px;
            margin: 0 0 12px 0;
        `;
        constraintsSection.appendChild(constraintsTitle);

        const constraintsList = document.createElement('ul');
        constraintsList.style.cssText = `
            list-style: none;
            padding: 0;
            margin: 0;
        `;

        (constraintsData.constraints || []).forEach(constraint => {
            const item = document.createElement('li');
            item.style.cssText = `
                background: var(--bg-secondary, #2a2a3e);
                border-left: 3px solid var(--accent-primary, #4a90e2);
                padding: 12px 16px;
                margin-bottom: 8px;
                border-radius: 4px;
                color: var(--text-primary, #e0e0e0);
                font-size: 14px;
                font-family: 'Courier New', monospace;
            `;
            item.textContent = constraint;
            constraintsList.appendChild(item);
        });

        constraintsSection.appendChild(constraintsList);
        wrapper.appendChild(constraintsSection);

        container.appendChild(wrapper);
    }
}

// Auto-integrate with existing CAD Renderer
if (typeof CADRenderer !== 'undefined') {
    const originalRender = CADRenderer.prototype.render;

    CADRenderer.prototype.render = async function (item, contentArea, chartId) {
        // Check if content is constrained engineering CAD
        if (typeof item.content === 'string' && item.content.includes('<CAD>')) {
            // Parse to check if it's engineering CAD
            const cadMatch = item.content.match(/<CAD>([\s\S]*?)<\/CAD>/);
            if (cadMatch) {
                try {
                    const cadData = JSON.parse(cadMatch[1]);
                    if (cadData.type === 'constrained_engineering_cad') {
                        console.log('✅ Constrained Engineering CAD detected, using EngineeringCADRenderer');
                        const engRenderer = new EngineeringCADRenderer(this);
                        return await engRenderer.render(item, contentArea, chartId);
                    }
                } catch (e) {
                    console.warn('CAD parse failed, using standard renderer:', e);
                }
            }
        }

        // Fall back to original renderer for standard CAD content
        return await originalRender.call(this, item, contentArea, chartId);
    };

    console.log('✅ EngineeringCADRenderer integrated with CADRenderer');
}
