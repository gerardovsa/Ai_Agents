/**
 * =============================================================================
 * SVG & ADVANCED VISUALIZATION RENDERING ENHANCEMENT
 * =============================================================================
 * Purpose: Extend Two-Rule streaming system to support inline SVG, LaTeX, 
 *          HTML, Chart.js, ApexCharts, Three.js, GSAP, and Lottie rendering
 * Date: December 5, 2025
 * Author: AI Infrastructure Team
 * 
 * This module adds comprehensive visualization capabilities without breaking
 * current Plotly/Mermaid support.
 * 
 * Integration: Can be used standalone or merged into streamingTwoRule.js class
 * =============================================================================
 */

class SVGVisualizationEnhancement {
    constructor() {
        console.log('✅ SVG Visualization Enhancement initialized');
        this.loadFontAwesome();
    }

    /**
     * =====================================================================
     * SECTION 1: DELIMITER SYSTEM
     * =====================================================================
     */

    /**
     * Get start delimiter for visualization type
     */
    getStartDelimiter(type) {
        const delimiters = {
            // Existing
            'mermaid': '<MERMAID>',
            'plotly': '<PLOTLY>',

            // ✨ SVG/Technical Diagrams
            'svg': '<SVG_VISUAL>',
            'cad': '<CAD>',
            'schematic': '<SCHEMATIC>',
            'blueprint': '<BLUEPRINT>',
            'molecule': '<MOLECULE>',

            // ✨ Math & Interactive
            'latex': '<LATEX>',
            'html': '<EXECUTE_HTML>',

            // ✨ Chart Libraries
            'chartjs': '<CHARTJS>',
            'apexcharts': '<APEXCHARTS>',

            // ✨ 3D & Animation
            'threejs': '<THREEJS>',
            'gsap': '<GSAP>',
            'lottie': '<LOTTIE>'
        };
        return delimiters[type.toLowerCase()] || '';
    }

    /**
     * Get end delimiter for visualization type
     */
    getEndDelimiter(type) {
        const delimiters = {
            // Existing
            'mermaid': '</MERMAID>',
            'plotly': '</PLOTLY>',

            // ✨ SVG/Technical Diagrams
            'svg': '</SVG_VISUAL>',
            'cad': '</CAD>',
            'schematic': '</SCHEMATIC>',
            'blueprint': '</BLUEPRINT>',
            'molecule': '</MOLECULE>',

            // ✨ Math & Interactive
            'latex': '</LATEX>',
            'html': '</EXECUTE_HTML>',

            // ✨ Chart Libraries
            'chartjs': '</CHARTJS>',
            'apexcharts': '</APEXCHARTS>',

            // ✨ 3D & Animation
            'threejs': '</THREEJS>',
            'gsap': '</GSAP>',
            'lottie': '</LOTTIE>'
        };
        return delimiters[type.toLowerCase()] || '';
    }

    /**
     * =====================================================================
     * SECTION 2: SVG RENDERING
     * =====================================================================
     */

    /**
     * Render SVG-based visualizations (CAD, schematics, blueprints, molecules)
     */
    async renderSVGVisualization(type, svgCode, container) {
        console.log(`🎨 TWO-RULE: Rendering ${type} SVG into container`);

        try {
            // 1. Sanitize SVG (remove scripts, dangerous attributes)
            const sanitized = this.sanitizeSVG(svgCode);

            // 2. Parse and validate XML structure
            const parser = new DOMParser();
            const doc = parser.parseFromString(sanitized, 'image/svg+xml');
            const parseError = doc.querySelector('parsererror');

            if (parseError) {
                throw new Error(`Invalid SVG: ${parseError.textContent}`);
            }

            const svgElement = doc.documentElement;

            // 3. Enhance SVG (viewBox, responsive, accessibility)
            this.enhanceSVGElement(svgElement, type);

            // 4. Create wrapper with type-specific styling
            const wrapper = document.createElement('div');
            wrapper.className = `svg-visualization-wrapper ${type}-diagram`;
            wrapper.style.cssText = this.getSVGWrapperStyles(type);

            // 5. Add SVG element first
            wrapper.appendChild(svgElement);

            // 6. Add control buttons
            const controls = this.createSVGControls(sanitized, type, wrapper);
            wrapper.insertBefore(controls, wrapper.firstChild);

            // 7. Clear container and insert
            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log(`✅ TWO-RULE: ${type} SVG rendered successfully`);

        } catch (error) {
            console.error(`❌ TWO-RULE: Error rendering ${type} SVG:`, error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>SVG Rendering Error (${type}):</strong><br>
                    ${this.escapeHtml(error.message)}
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 3: LATEX RENDERING
     * =====================================================================
     */

    /**
     * Render LaTeX mathematical equations using KaTeX
     */
    async renderLatexVisualization(latexCode, container) {
        console.log('🔢 TWO-RULE: Rendering LaTeX equation');

        try {
            // 1. Load KaTeX library if not already loaded
            if (typeof katex === 'undefined') {
                console.log('📚 Loading KaTeX library...');
                await this.loadKaTeX();
            }

            // 2. Create wrapper with professional styling
            const wrapper = document.createElement('div');
            wrapper.className = 'latex-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: 800px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);
                border-left: 4px solid #4CAF50;
                border-radius: 8px;
                text-align: center;
                font-size: 1.2em;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 3. Render equation with KaTeX
            katex.render(latexCode.trim(), wrapper, {
                throwOnError: false,
                displayMode: true,
                trust: false,
                strict: 'warn'
            });

            // 4. Clear container and insert
            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log('✅ TWO-RULE: LaTeX rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: LaTeX rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>LaTeX Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(latexCode)}</pre>
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 4: HTML RENDERING
     * =====================================================================
     */

    /**
     * Render inline executable HTML (interactive widgets, demos, visualizations)
     */
    async renderHTMLVisualization(htmlCode, container) {
        console.log('🌐 TWO-RULE: Rendering inline HTML');

        try {
            // 1. Create sandboxed wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'html-visualization-wrapper';
            wrapper.style.cssText = `
                all: initial;
                display: block;
                width: 100%;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                overflow: auto;
                contain: layout style paint;
                isolation: isolate;
            `;

            // 2. Create sandboxed iframe
            const iframe = document.createElement('iframe');
            iframe.style.cssText = `
                width: 100%;
                border: none;
                background: transparent;
                display: block;
                isolation: isolate;
            `;
            iframe.sandbox = 'allow-scripts allow-same-origin';
            iframe.setAttribute('referrerpolicy', 'no-referrer');
            iframe.setAttribute('loading', 'eager');

            // 3. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: flex-end;
                margin-bottom: 0.5rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openHTMLPopup(htmlCode, wrapper);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy HTML code', () => {
                try {
                    navigator.clipboard.writeText(htmlCode);
                    this.showNotification('✅ HTML copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(copyBtn);

            // 4. Build isolated HTML document
            const isolatedHTML = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            width: 100%;
            height: 100%;
            overflow: auto;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            padding: 1rem;
            background: transparent;
            color: #000;
            line-height: 1.5;
        }
        * { all: revert; }
        body * { all: revert; }
    </style>
</head>
<body>
${htmlCode}
</body>
</html>`;

            // 5. Inject via srcdoc
            iframe.srcdoc = isolatedHTML;

            // 6. Assemble wrapper
            wrapper.appendChild(controls);
            wrapper.appendChild(iframe);

            // 7. Auto-resize iframe
            iframe.addEventListener('load', () => {
                setTimeout(() => {
                    try {
                        const iframeBody = iframe.contentWindow.document.body;
                        const iframeHtml = iframe.contentWindow.document.documentElement;
                        const height = Math.max(
                            iframeBody.scrollHeight,
                            iframeBody.offsetHeight,
                            iframeHtml.scrollHeight,
                            iframeHtml.offsetHeight
                        );
                        iframe.style.height = (height + 20) + 'px';
                        console.log(`📏 Iframe auto-resized to ${height + 20}px`);
                    } catch (e) {
                        console.warn('⚠️ Could not auto-resize iframe:', e);
                        iframe.style.height = '400px';
                    }
                }, 100);
            });

            // 8. Clear container and insert
            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log('✅ TWO-RULE: HTML rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: HTML rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>HTML Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(htmlCode)}</pre>
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 5: CHART.JS RENDERING
     * =====================================================================
     */

    /**
     * Render Chart.js visualization from JSON config
     */
    async renderChartJSVisualization(configJSON, container) {
        console.log('📊 TWO-RULE: Rendering Chart.js');

        try {
            // 1. Load Chart.js library
            if (typeof Chart === 'undefined') {
                console.log('📚 Loading Chart.js library...');
                await this.loadScript('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js');
            }

            // 2. Parse JSON config
            const config = JSON.parse(configJSON.trim());

            // 3. Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'chartjs-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: ${config.width || 800}px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 4. Create canvas
            const canvas = document.createElement('canvas');
            canvas.width = config.width || 800;
            canvas.height = config.height || 400;

            // 5. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: flex-end;
                margin-bottom: 0.5rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('chartjs', configJSON, wrapper);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy config', () => {
                try {
                    navigator.clipboard.writeText(configJSON);
                    this.showNotification('✅ Config copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(copyBtn);

            // 6. Assemble and render
            wrapper.appendChild(controls);
            wrapper.appendChild(canvas);

            container.innerHTML = '';
            container.appendChild(wrapper);

            // 7. Create Chart.js instance
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: config.type,
                data: config.data,
                options: config.options || {}
            });

            console.log('✅ TWO-RULE: Chart.js rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: Chart.js rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>Chart.js Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(configJSON)}</pre>
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 6: APEXCHARTS RENDERING
     * =====================================================================
     */

    /**
     * Render ApexCharts visualization from JSON config
     */
    async renderApexChartsVisualization(configJSON, container) {
        console.log('📈 TWO-RULE: Rendering ApexCharts');

        try {
            // 1. Load ApexCharts library
            if (typeof ApexCharts === 'undefined') {
                console.log('📚 Loading ApexCharts library...');
                await this.loadScript('https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js');
            }

            // 2. Parse JSON config
            const config = JSON.parse(configJSON.trim());

            // 3. Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'apexcharts-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: ${config.chart?.width || 800}px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 4. Create chart container
            const chartDiv = document.createElement('div');

            // 5. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: flex-end;
                margin-bottom: 0.5rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('apexcharts', configJSON, wrapper);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy config', () => {
                try {
                    navigator.clipboard.writeText(configJSON);
                    this.showNotification('✅ Config copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(copyBtn);

            // 6. Assemble and render
            wrapper.appendChild(controls);
            wrapper.appendChild(chartDiv);

            container.innerHTML = '';
            container.appendChild(wrapper);

            // 7. Create ApexCharts instance
            const chart = new ApexCharts(chartDiv, config);
            chart.render();

            console.log('✅ TWO-RULE: ApexCharts rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: ApexCharts rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>ApexCharts Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(configJSON)}</pre>
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 7: THREE.JS RENDERING
     * =====================================================================
     */

    /**
     * Render Three.js 3D scene from JSON config
     */
    async renderThreeJSVisualization(configJSON, container) {
        console.log('🎮 TWO-RULE: Rendering Three.js');

        try {
            // 1. Load Three.js library
            if (typeof THREE === 'undefined') {
                console.log('📚 Loading Three.js library...');
                await this.loadScript('https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js');
            }

            // 2. Parse JSON config
            const config = JSON.parse(configJSON.trim());

            // 3. Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'threejs-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: ${config.width || 800}px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: ${config.scene?.background || '#1a1a2e'};
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 4. Create render container
            const renderDiv = document.createElement('div');
            renderDiv.style.cssText = `width: 100%; height: ${config.height || 400}px; position: relative;`;

            // 5. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: flex-end;
                margin-bottom: 0.5rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('threejs', configJSON, wrapper);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy config', () => {
                try {
                    navigator.clipboard.writeText(configJSON);
                    this.showNotification('✅ Config copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(copyBtn);

            // 6. Assemble
            wrapper.appendChild(controls);
            wrapper.appendChild(renderDiv);

            container.innerHTML = '';
            container.appendChild(wrapper);

            // 7. Build Three.js scene
            this.buildThreeJSScene(config, renderDiv);

            console.log('✅ TWO-RULE: Three.js rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: Three.js rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>Three.js Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(configJSON)}</pre>
                </div>
            `;
        }
    }

    /**
     * Build Three.js scene from JSON configuration
     */
    buildThreeJSScene(config, container) {
        // Create scene
        const scene = new THREE.Scene();
        if (config.scene?.background) {
            scene.background = new THREE.Color(config.scene.background);
        }

        // Create camera
        const camera = new THREE.PerspectiveCamera(
            config.scene?.camera?.fov || 75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        const camPos = config.scene?.camera?.position || [0, 0, 5];
        camera.position.set(camPos[0], camPos[1], camPos[2]);

        // Create renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // Add lights
        if (config.lights) {
            config.lights.forEach(lightConfig => {
                let light;
                if (lightConfig.type === 'ambient') {
                    light = new THREE.AmbientLight(0xffffff, lightConfig.intensity || 0.5);
                } else if (lightConfig.type === 'directional') {
                    light = new THREE.DirectionalLight(0xffffff, lightConfig.intensity || 1);
                    if (lightConfig.position) {
                        light.position.set(lightConfig.position[0], lightConfig.position[1], lightConfig.position[2]);
                    }
                }
                if (light) scene.add(light);
            });
        }

        // Add objects
        const objects = [];
        if (config.objects) {
            config.objects.forEach(objConfig => {
                let geometry, material, mesh;

                // Create geometry
                if (objConfig.type === 'box') {
                    const size = objConfig.size || [1, 1, 1];
                    geometry = new THREE.BoxGeometry(size[0], size[1], size[2]);
                } else if (objConfig.type === 'sphere') {
                    geometry = new THREE.SphereGeometry(objConfig.radius || 0.5, 32, 32);
                }

                // Create material
                material = new THREE.MeshPhongMaterial({ color: objConfig.color || '#3b82f6' });

                // Create mesh
                mesh = new THREE.Mesh(geometry, material);
                if (objConfig.position) {
                    mesh.position.set(objConfig.position[0], objConfig.position[1], objConfig.position[2]);
                }
                if (objConfig.rotation) {
                    mesh.rotation.set(
                        objConfig.rotation[0] * Math.PI / 180,
                        objConfig.rotation[1] * Math.PI / 180,
                        objConfig.rotation[2] * Math.PI / 180
                    );
                }

                scene.add(mesh);
                objects.push(mesh);
            });
        }

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);

            // Apply animations
            if (config.animation) {
                objects.forEach(obj => {
                    if (config.animation.rotate) {
                        obj.rotation.x += config.animation.speed || 0.01;
                        obj.rotation.y += config.animation.speed || 0.01;
                    }
                });
            }

            renderer.render(scene, camera);
        }
        animate();
    }

    /**
     * =====================================================================
     * SECTION 8: GSAP RENDERING
     * =====================================================================
     */

    /**
     * Render GSAP animation from JSON config
     */
    async renderGSAPVisualization(configJSON, container) {
        console.log('✨ TWO-RULE: Rendering GSAP animation');

        try {
            // 1. Load GSAP library
            if (typeof gsap === 'undefined') {
                console.log('📚 Loading GSAP library...');
                await this.loadScript('https://cdn.jsdelivr.net/npm/gsap@3.12.4/dist/gsap.min.js');
            }

            // 2. Parse JSON config
            const config = JSON.parse(configJSON.trim());

            // 3. Create wrapper with demo element
            const wrapper = document.createElement('div');
            wrapper.className = 'gsap-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: 800px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 4. Create demo element to animate
            const demoElement = document.createElement('div');
            demoElement.id = 'gsapDemo';
            demoElement.style.cssText = `
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                margin: 2rem auto;
            `;

            // 5. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: center;
                margin-top: 1rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('gsap', configJSON, wrapper);
            });

            const playBtn = this.createControlButton('▶ Play', 'Play animation', () => {
                this.applyGSAPAnimation(config, demoElement);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy config', () => {
                try {
                    navigator.clipboard.writeText(configJSON);
                    this.showNotification('✅ Config copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(playBtn);
            controls.appendChild(copyBtn);

            // 6. Assemble
            wrapper.appendChild(demoElement);
            wrapper.appendChild(controls);

            container.innerHTML = '';
            container.appendChild(wrapper);

            // 7. Apply animation
            this.applyGSAPAnimation(config, demoElement);

            console.log('✅ TWO-RULE: GSAP animation rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: GSAP rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>GSAP Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(configJSON)}</pre>
                </div>
            `;
        }
    }

    /**
     * Apply GSAP animation from config
     */
    applyGSAPAnimation(config, element) {
        if (config.timeline) {
            const tl = gsap.timeline({ repeat: config.repeat || 0, yoyo: config.yoyo || false });
            config.timeline.forEach(step => {
                if (step.to) {
                    tl.to(element, step.to);
                }
            });
        } else {
            gsap.to(element, {
                ...config,
                ease: config.easing || 'power2.inOut'
            });
        }
    }

    /**
     * =====================================================================
     * SECTION 9: LOTTIE RENDERING
     * =====================================================================
     */

    /**
     * Render Lottie animation from JSON config
     */
    async renderLottieVisualization(configJSON, container) {
        console.log('🎬 TWO-RULE: Rendering Lottie animation');

        try {
            // 1. Load Lottie library
            if (typeof lottie === 'undefined') {
                console.log('📚 Loading Lottie library...');
                await this.loadScript('https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js');
            }

            // 2. Parse JSON config
            const config = JSON.parse(configJSON.trim());

            // 3. Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'lottie-visualization-wrapper';
            wrapper.style.cssText = `
                width: 100%;
                max-width: 600px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;

            // 4. Create animation container
            const animDiv = document.createElement('div');
            animDiv.style.cssText = `width: 100%; height: ${config.height || 400}px;`;

            // 5. Add controls
            const controls = document.createElement('div');
            controls.style.cssText = `
                display: flex;
                justify-content: center;
                margin-top: 1rem;
                gap: 0.5rem;
            `;

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('lottie', configJSON, wrapper);
            });

            const copyBtn = this.createControlButton('📋 Copy', 'Copy config', () => {
                try {
                    navigator.clipboard.writeText(configJSON);
                    this.showNotification('✅ Config copied!', 'success');
                } catch (error) {
                    this.showNotification('❌ Copy failed', 'error');
                }
            });

            controls.appendChild(expandBtn);
            controls.appendChild(copyBtn);

            // 6. Assemble
            wrapper.appendChild(animDiv);
            wrapper.appendChild(controls);

            container.innerHTML = '';
            container.appendChild(wrapper);

            // 7. Load Lottie animation
            lottie.loadAnimation({
                container: animDiv,
                renderer: config.renderer || 'svg',
                loop: config.loop !== undefined ? config.loop : true,
                autoplay: config.autoplay !== undefined ? config.autoplay : true,
                animationData: config.animationData || config.path
            });

            console.log('✅ TWO-RULE: Lottie animation rendered successfully');

        } catch (error) {
            console.error('❌ TWO-RULE: Lottie rendering error:', error);
            container.innerHTML = `
                <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                    <strong>Lottie Rendering Error:</strong><br>
                    ${this.escapeHtml(error.message)}
                    <pre style="margin-top: 1rem; white-space: pre-wrap;">${this.escapeHtml(configJSON)}</pre>
                </div>
            `;
        }
    }

    /**
     * =====================================================================
     * SECTION 10: POPUP HANDLERS
     * =====================================================================
     */

    /**
     * Open HTML in popup with larger view
     */
    openHTMLPopup(htmlCode, originalWrapper) {
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        // Create popup
        const popup = document.createElement('div');
        popup.className = 'html-visualization-wrapper popup';

        // Header
        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = '<i class="fas fa-code"></i> HTML Visualization';

        const headerControls = document.createElement('div');
        headerControls.className = 'viz-popup-header-controls';

        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'viz-popup-header-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy HTML';
        copyBtn.onclick = () => {
            try {
                navigator.clipboard.writeText(htmlCode);
                this.showNotification('✅ HTML copied!', 'success');
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i>', 1500);
            } catch (error) {
                this.showNotification('❌ Copy failed', 'error');
            }
        };

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.title = 'Close';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        headerControls.appendChild(copyBtn);
        headerControls.appendChild(closeBtn);
        header.appendChild(title);
        header.appendChild(headerControls);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'viz-popup-content';

        // Create larger iframe for popup
        const iframe = document.createElement('iframe');
        iframe.style.cssText = `
            width: 100%;
            height: calc(85vh - 100px);
            border: none;
            background: white;
        `;
        iframe.sandbox = 'allow-scripts allow-same-origin';

        contentDiv.appendChild(iframe);

        // Assemble popup
        popup.appendChild(header);
        popup.appendChild(contentDiv);

        // Make draggable
        this.makeDraggable(popup, header);

        // Add to document
        document.body.appendChild(popup);

        // Inject HTML
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                        padding: 2rem;
                        background: white;
                    }
                </style>
            </head>
            <body>
                ${htmlCode}
            </body>
            </html>
        `);
        iframeDoc.close();

        // Close handlers
        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
        popup.onclick = (e) => e.stopPropagation();
    }

    /**
     * Open SVG in draggable popup modal
     */
    openSVGPopup(content, type, originalWrapper) {
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        // Create popup
        const popup = document.createElement('div');
        popup.className = `svg-visualization-wrapper ${type}-diagram popup`;

        // Header
        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        // Title
        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = `<i class="fas fa-cube"></i> ${type.toUpperCase()} Visualization`;

        // Header controls
        const headerControls = document.createElement('div');
        headerControls.className = 'viz-popup-header-controls';

        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'viz-popup-header-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy SVG';
        copyBtn.onclick = () => {
            try {
                navigator.clipboard.writeText(content);
                this.showNotification('✅ Copied to clipboard!', 'success');
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i>', 1500);
            } catch (error) {
                this.showNotification('❌ Copy failed', 'error');
            }
        };

        // Download button
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'viz-popup-header-btn';
        downloadBtn.innerHTML = '<i class="fas fa-download"></i>';
        downloadBtn.title = 'Download';
        downloadBtn.onclick = () => {
            try {
                const blob = new Blob([content], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_diagram_${Date.now()}.svg`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                this.showNotification('✅ Downloaded!', 'success');
            } catch (error) {
                this.showNotification('❌ Download failed', 'error');
            }
        };

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.title = 'Close';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        // Assemble header
        headerControls.appendChild(copyBtn);
        headerControls.appendChild(downloadBtn);
        headerControls.appendChild(closeBtn);
        header.appendChild(title);
        header.appendChild(headerControls);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'viz-popup-content';

        // Re-parse and render SVG
        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(content, 'image/svg+xml');
            const svgElement = doc.documentElement;

            this.enhanceSVGElement(svgElement, type);
            contentDiv.appendChild(svgElement);
        } catch (error) {
            console.error('Error rendering SVG in popup:', error);
            contentDiv.innerHTML = '<p style="color: red;">Error rendering visualization</p>';
        }

        // Assemble popup
        popup.appendChild(header);
        popup.appendChild(contentDiv);

        // Make draggable
        this.makeDraggable(popup, header);

        // Add to document
        document.body.appendChild(popup);

        // Close handlers
        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
        popup.onclick = (e) => e.stopPropagation();
    }

    /**
     * Generic chart popup handler
     */
    openChartPopup(type, configJSON, originalWrapper) {
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        // Create popup
        const popup = document.createElement('div');
        popup.className = `${type}-visualization-wrapper popup`;

        // Header
        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = `<i class="fas fa-chart-bar"></i> ${type.toUpperCase()} Visualization`;

        const headerControls = document.createElement('div');
        headerControls.className = 'viz-popup-header-controls';

        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'viz-popup-header-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy config';
        copyBtn.onclick = () => {
            try {
                navigator.clipboard.writeText(configJSON);
                this.showNotification('✅ Config copied!', 'success');
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => copyBtn.innerHTML = '<i class="fas fa-copy"></i>', 1500);
            } catch (error) {
                this.showNotification('❌ Copy failed', 'error');
            }
        };

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.title = 'Close';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        headerControls.appendChild(copyBtn);
        headerControls.appendChild(closeBtn);
        header.appendChild(title);
        header.appendChild(headerControls);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'viz-popup-content';

        // Re-render based on type
        if (type === 'chartjs') {
            this.renderChartJSVisualization(configJSON, contentDiv);
        } else if (type === 'apexcharts') {
            this.renderApexChartsVisualization(configJSON, contentDiv);
        } else if (type === 'threejs') {
            this.renderThreeJSVisualization(configJSON, contentDiv);
        } else if (type === 'gsap') {
            this.renderGSAPVisualization(configJSON, contentDiv);
        } else if (type === 'lottie') {
            this.renderLottieVisualization(configJSON, contentDiv);
        }

        popup.appendChild(header);
        popup.appendChild(contentDiv);

        // Make draggable
        this.makeDraggable(popup, header);

        // Add to document
        document.body.appendChild(popup);

        // Close handlers
        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
        popup.onclick = (e) => e.stopPropagation();
    }

    /**
     * =====================================================================
     * SECTION 11: SECURITY HELPERS
     * =====================================================================
     */

    /**
     * Sanitize SVG code to prevent XSS attacks
     */
    sanitizeSVG(svgCode) {
        let sanitized = svgCode;

        // Remove dangerous tags
        const dangerousTags = ['script', 'iframe', 'object', 'embed', 'link', 'style', 'foreignObject'];
        dangerousTags.forEach(tag => {
            const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>`, 'gis');
            sanitized = sanitized.replace(regex, '');
            const selfClosing = new RegExp(`<${tag}[^>]*/>`, 'gi');
            sanitized = sanitized.replace(selfClosing, '');
        });

        // Remove event handlers
        sanitized = sanitized.replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '');

        // Remove javascript: protocols
        sanitized = sanitized.replace(/javascript:/gi, '');

        // Remove data: URLs
        sanitized = sanitized.replace(/data:text\/html/gi, '');

        return sanitized;
    }

    /**
     * Enhance SVG element with responsive attributes
     */
    enhanceSVGElement(svgElement, type) {
        // Ensure viewBox exists
        if (!svgElement.hasAttribute('viewBox')) {
            const width = svgElement.getAttribute('width') || '800';
            const height = svgElement.getAttribute('height') || '600';
            svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
        }

        // Remove fixed dimensions
        svgElement.removeAttribute('width');
        svgElement.removeAttribute('height');

        // Apply responsive styling
        svgElement.style.cssText = 'width: 100%; height: auto; display: block; max-width: 100%;';

        // Add accessibility
        if (!svgElement.querySelector('title')) {
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${type.toUpperCase()} Visualization`;
            svgElement.insertBefore(title, svgElement.firstChild);
        }

        svgElement.setAttribute('role', 'img');
        svgElement.setAttribute('aria-label', `${type} diagram`);
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * =====================================================================
     * SECTION 12: UI HELPERS
     * =====================================================================
     */

    /**
     * Create SVG controls
     */
    createSVGControls(svgContent, type, wrapper) {
        const controls = document.createElement('div');
        controls.className = 'svg-control-bar';
        controls.style.cssText = `
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            justify-content: flex-end;
            flex-wrap: wrap;
        `;

        const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup window', () => {
            this.openSVGPopup(svgContent, type, wrapper);
        });

        controls.appendChild(expandBtn);
        return controls;
    }

    /**
     * Create a styled control button
     */
    createControlButton(text, tooltip, onClick) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.title = tooltip;
        btn.className = 'svg-control-btn';
        btn.style.cssText = `
            padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-family: -apple-system, system-ui, sans-serif;
            transition: all 0.2s ease;
            white-space: nowrap;
        `;

        btn.addEventListener('mouseenter', () => {
            btn.style.background = '#4CAF50';
            btn.style.color = 'white';
            btn.style.transform = 'translateY(-2px)';
            btn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.background = 'rgba(255, 255, 255, 0.95)';
            btn.style.color = 'inherit';
            btn.style.transform = 'translateY(0)';
            btn.style.boxShadow = 'none';
        });

        btn.onclick = onClick;
        return btn;
    }

    /**
     * Make element draggable
     */
    makeDraggable(element, handle) {
        let isDragging = false;
        let currentX, currentY, initialX, initialY;

        handle.addEventListener('mousedown', (e) => {
            if (e.target !== handle && !handle.contains(e.target)) return;
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'I') return;

            isDragging = true;
            initialX = e.clientX - (parseFloat(element.style.left) || 0);
            initialY = e.clientY - (parseFloat(element.style.top) || 0);

            element.style.transform = 'none';
            handle.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;

            element.style.left = currentX + 'px';
            element.style.top = currentY + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                handle.style.cursor = 'move';
            }
        });
    }

    /**
     * Show temporary notification
     */
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            font-family: -apple-system, system-ui, sans-serif;
            font-size: 14px;
            animation: slideInRight 0.3s ease, slideOutRight 0.3s ease 2.7s;
            pointer-events: none;
        `;

        if (!document.querySelector('#svg-notification-animations')) {
            const style = document.createElement('style');
            style.id = 'svg-notification-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    /**
     * Get type-specific wrapper styles
     */
    getSVGWrapperStyles(type) {
        const themes = {
            'cad': `
                padding: 1.5rem;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border: 2px solid #8e9eab;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `,
            'schematic': `
                padding: 1.5rem;
                background: #fffff0;
                border: 2px solid #ffd700;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `,
            'blueprint': `
                padding: 1.5rem;
                background: #001f3f;
                border: 2px solid #0074D9;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `,
            'molecule': `
                padding: 1.5rem;
                background: #f0f8ff;
                border: 2px solid #4682b4;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `,
            'svg': `
                padding: 1.5rem;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            `
        };

        return themes[type] || themes['svg'];
    }

    /**
     * =====================================================================
     * SECTION 13: LIBRARY LOADERS
     * =====================================================================
     */

    /**
     * Load KaTeX library
     */
    async loadKaTeX() {
        return new Promise((resolve, reject) => {
            // Load CSS
            if (!document.querySelector('link[href*="katex.min.css"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
                link.integrity = 'sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV';
                link.crossOrigin = 'anonymous';
                document.head.appendChild(link);
            }

            // Load JavaScript
            if (!document.querySelector('script[src*="katex.min.js"]')) {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
                script.integrity = 'sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8';
                script.crossOrigin = 'anonymous';
                script.onload = () => {
                    console.log('✅ KaTeX loaded');
                    resolve();
                };
                script.onerror = (error) => {
                    console.error('❌ Failed to load KaTeX:', error);
                    reject(new Error('Failed to load KaTeX'));
                };
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    /**
     * Load JavaScript library from CDN
     */
    async loadScript(url) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${url}"]`)) {
                console.log(`✅ Library already loaded: ${url}`);
                resolve();
                return;
            }

            console.log(`📚 Loading library: ${url}`);
            const script = document.createElement('script');
            script.src = url;
            script.onload = () => {
                console.log(`✅ Library loaded: ${url}`);
                resolve();
            };
            script.onerror = (error) => {
                console.error(`❌ Failed to load: ${url}`, error);
                reject(new Error(`Failed to load: ${url}`));
            };
            document.head.appendChild(script);
        });
    }

    /**
     * Load Font Awesome
     */
    loadFontAwesome() {
        if (!document.querySelector('link[href*="font-awesome"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css';
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SVGVisualizationEnhancement;
} else {
    window.SVGVisualizationEnhancement = SVGVisualizationEnhancement;
}

console.log('✅ SVG Visualization Enhancement Module Loaded');