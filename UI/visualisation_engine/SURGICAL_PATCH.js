
/**
 * =============================================================================
 * INTEGRATION PATCH FOR streamingTwoRule.js
 * =============================================================================
 * INSTRUCTIONS:
 * 1. Find TwoRuleStreamProcessor class definition
 * 2. Update getStartDelimiter() and getEndDelimiter() methods (see STEP 1)
 * 3. Update renderVisualization() method (see STEP 2)
 * 4. Add all methods from STEP 3 to the class
 * =============================================================================
 * 
 * NOTE: This file is REFERENCE ONLY - not meant to be loaded!
 * These are methods to be copied into streamingTwoRule.js
 * =============================================================================
 */

// Wrap in a class to avoid syntax errors (this is just for documentation)
class VisualizationPatchMethods {

    /**
     * Render SVG-based visualizations
     */
    renderSVGVisualization(type, svgCode, container) {
        console.log(`🎨 TWO-RULE: Rendering ${type} SVG`);

        try {
            const sanitized = this.sanitizeSVG(svgCode);
            const parser = new DOMParser();
            const doc = parser.parseFromString(sanitized, 'image/svg+xml');
            const parseError = doc.querySelector('parsererror');

            if (parseError) {
                throw new Error(`Invalid SVG: ${parseError.textContent}`);
            }

            const svgElement = doc.documentElement;
            this.enhanceSVGElement(svgElement, type);

            const wrapper = document.createElement('div');
            wrapper.className = `svg-visualization-wrapper ${type}-diagram`;
            wrapper.style.cssText = this.getSVGWrapperStyles(type);

            wrapper.appendChild(svgElement);

            const controls = this.createSVGControls(sanitized, type, wrapper);
            wrapper.insertBefore(controls, wrapper.firstChild);

            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log(`✅ TWO-RULE: ${type} SVG rendered`);

        } catch (error) {
            console.error(`❌ TWO-RULE: ${type} SVG error:`, error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>SVG Rendering Error (${type}):</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    /**
     * Render LaTeX equations
     */
    async renderLatexVisualization(latexCode, container) {
        console.log('🔢 TWO-RULE: Rendering LaTeX');

        try {
            if (typeof katex === 'undefined') {
                console.log('📚 Loading KaTeX...');
                await this.loadKaTeX();
            }

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

            katex.render(latexCode.trim(), wrapper, {
                throwOnError: false,
                displayMode: true,
                trust: false,
                strict: 'warn'
            });

            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log('✅ TWO-RULE: LaTeX rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: LaTeX error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>LaTeX Error:</strong><br>
                ${this.escapeHtml(error.message)}
                <pre style="margin-top: 1rem;">${this.escapeHtml(latexCode)}</pre>
            </div>
        `;
        }
    }

    /**
     * Render inline HTML
     */
    async renderHTMLVisualization(htmlCode, container) {
        console.log('🌐 TWO-RULE: Rendering HTML');

        try {
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

            const isolatedHTML = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; overflow: auto; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            padding: 1rem;
            background: transparent;
            color: #000;
            line-height: 1.5;
        }
    </style>
</head>
<body>
${htmlCode}
</body>
</html>`;

            iframe.srcdoc = isolatedHTML;

            wrapper.appendChild(controls);
            wrapper.appendChild(iframe);

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
                    } catch (e) {
                        console.warn('⚠️ Could not auto-resize iframe:', e);
                        iframe.style.height = '400px';
                    }
                }, 100);
            });

            container.innerHTML = '';
            container.appendChild(wrapper);

            console.log('✅ TWO-RULE: HTML rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: HTML error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>HTML Error:</strong><br>
                ${this.escapeHtml(error.message)}
                <pre style="margin-top: 1rem;">${this.escapeHtml(htmlCode)}</pre>
            </div>
        `;
        }
    }

    /**
     * Render Chart.js
     */
    async renderChartJSVisualization(configJSON, container) {
        console.log('📊 TWO-RULE: Rendering Chart.js');

        try {
            if (typeof Chart === 'undefined') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js');
            }

            const config = JSON.parse(configJSON.trim());

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

            const canvas = document.createElement('canvas');
            const controls = document.createElement('div');
            controls.style.cssText = 'display: flex; justify-content: flex-end; margin-bottom: 0.5rem; gap: 0.5rem;';

            const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
                this.openChartPopup('chartjs', configJSON, wrapper);
            });

            controls.appendChild(expandBtn);
            wrapper.appendChild(controls);
            wrapper.appendChild(canvas);

            container.innerHTML = '';
            container.appendChild(wrapper);

            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: config.type,
                data: config.data,
                options: config.options || {}
            });

            console.log('✅ TWO-RULE: Chart.js rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: Chart.js error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>Chart.js Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    /**
     * Render ApexCharts
     */
    async renderApexChartsVisualization(configJSON, container) {
        console.log('📈 TWO-RULE: Rendering ApexCharts');

        try {
            if (typeof ApexCharts === 'undefined') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js');
            }

            const config = JSON.parse(configJSON.trim());

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

            const chartDiv = document.createElement('div');
            wrapper.appendChild(chartDiv);

            container.innerHTML = '';
            container.appendChild(wrapper);

            const chart = new ApexCharts(chartDiv, config);
            chart.render();

            console.log('✅ TWO-RULE: ApexCharts rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: ApexCharts error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>ApexCharts Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    /**
     * Render Three.js
     */
    async renderThreeJSVisualization(configJSON, container) {
        console.log('🎮 TWO-RULE: Rendering Three.js');

        try {
            if (typeof THREE === 'undefined') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js');
            }

            const config = JSON.parse(configJSON.trim());

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

            const renderDiv = document.createElement('div');
            renderDiv.style.cssText = `width: 100%; height: ${config.height || 400}px; position: relative;`;

            wrapper.appendChild(renderDiv);
            container.innerHTML = '';
            container.appendChild(wrapper);

            this.buildThreeJSScene(config, renderDiv);

            console.log('✅ TWO-RULE: Three.js rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: Three.js error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>Three.js Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    buildThreeJSScene(config, container) {
        const scene = new THREE.Scene();
        if (config.scene?.background) {
            scene.background = new THREE.Color(config.scene.background);
        }

        const camera = new THREE.PerspectiveCamera(
            config.scene?.camera?.fov || 75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        const camPos = config.scene?.camera?.position || [0, 0, 5];
        camera.position.set(camPos[0], camPos[1], camPos[2]);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

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

        const objects = [];
        if (config.objects) {
            config.objects.forEach(objConfig => {
                let geometry, material, mesh;

                if (objConfig.type === 'box') {
                    const size = objConfig.size || [1, 1, 1];
                    geometry = new THREE.BoxGeometry(size[0], size[1], size[2]);
                } else if (objConfig.type === 'sphere') {
                    geometry = new THREE.SphereGeometry(objConfig.radius || 0.5, 32, 32);
                }

                material = new THREE.MeshPhongMaterial({ color: objConfig.color || '#3b82f6' });
                mesh = new THREE.Mesh(geometry, material);

                if (objConfig.position) {
                    mesh.position.set(objConfig.position[0], objConfig.position[1], objConfig.position[2]);
                }

                scene.add(mesh);
                objects.push(mesh);
            });
        }

        function animate() {
            requestAnimationFrame(animate);
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
     * Render GSAP
     */
    async renderGSAPVisualization(configJSON, container) {
        console.log('✨ TWO-RULE: Rendering GSAP');

        try {
            if (typeof gsap === 'undefined') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/gsap@3.12.4/dist/gsap.min.js');
            }

            const config = JSON.parse(configJSON.trim());

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

            const demoElement = document.createElement('div');
            demoElement.style.cssText = `
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            margin: 2rem auto;
        `;

            wrapper.appendChild(demoElement);
            container.innerHTML = '';
            container.appendChild(wrapper);

            this.applyGSAPAnimation(config, demoElement);

            console.log('✅ TWO-RULE: GSAP rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: GSAP error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>GSAP Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    applyGSAPAnimation(config, element) {
        if (config.timeline) {
            const tl = gsap.timeline({ repeat: config.repeat || 0, yoyo: config.yoyo || false });
            config.timeline.forEach(step => {
                if (step.to) tl.to(element, step.to);
            });
        } else {
            gsap.to(element, { ...config, ease: config.easing || 'power2.inOut' });
        }
    }

    /**
     * Render Lottie
     */
    async renderLottieVisualization(configJSON, container) {
        console.log('🎬 TWO-RULE: Rendering Lottie');

        try {
            if (typeof lottie === 'undefined') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js');
            }

            const config = JSON.parse(configJSON.trim());

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

            const animDiv = document.createElement('div');
            animDiv.style.cssText = `width: 100%; height: ${config.height || 400}px;`;

            wrapper.appendChild(animDiv);
            container.innerHTML = '';
            container.appendChild(wrapper);

            lottie.loadAnimation({
                container: animDiv,
                renderer: config.renderer || 'svg',
                loop: config.loop !== undefined ? config.loop : true,
                autoplay: config.autoplay !== undefined ? config.autoplay : true,
                animationData: config.animationData || config.path
            });

            console.log('✅ TWO-RULE: Lottie rendered');

        } catch (error) {
            console.error('❌ TWO-RULE: Lottie error:', error);
            container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace; background: #fff0f0; border-radius: 4px;">
                <strong>Lottie Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
        }
    }

    /**
     * POPUP HANDLERS
     */

    openHTMLPopup(htmlCode, originalWrapper) {
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        const popup = document.createElement('div');
        popup.className = 'html-visualization-wrapper popup';

        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = '<i class="fas fa-code"></i> HTML Visualization';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        header.appendChild(title);
        header.appendChild(closeBtn);

        const iframe = document.createElement('iframe');
        iframe.style.cssText = 'width: 100%; height: calc(85vh - 100px); border: none; background: white;';
        iframe.sandbox = 'allow-scripts allow-same-origin';

        popup.appendChild(header);
        popup.appendChild(iframe);

        this.makeDraggable(popup, header);
        document.body.appendChild(popup);

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>${htmlCode}</body></html>`);
        iframeDoc.close();

        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
    }

    openSVGPopup(content, type, originalWrapper) {
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        const popup = document.createElement('div');
        popup.className = `svg-visualization-wrapper ${type}-diagram popup`;

        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = `<i class="fas fa-cube"></i> ${type.toUpperCase()}`;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        header.appendChild(title);
        header.appendChild(closeBtn);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'viz-popup-content';

        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(content, 'image/svg+xml');
            const svgElement = doc.documentElement;
            this.enhanceSVGElement(svgElement, type);
            contentDiv.appendChild(svgElement);
        } catch (error) {
            contentDiv.innerHTML = '<p style="color: red;">Error rendering</p>';
        }

        popup.appendChild(header);
        popup.appendChild(contentDiv);

        this.makeDraggable(popup, header);
        document.body.appendChild(popup);

        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
    }

    openChartPopup(type, configJSON, originalWrapper) {
        const backdrop = document.createElement('div');
        backdrop.className = 'viz-popup-backdrop';
        document.body.appendChild(backdrop);

        const popup = document.createElement('div');
        popup.className = `${type}-visualization-wrapper popup`;

        const header = document.createElement('div');
        header.className = 'viz-popup-header';

        const title = document.createElement('div');
        title.className = 'viz-popup-header-title';
        title.innerHTML = `<i class="fas fa-chart-bar"></i> ${type.toUpperCase()}`;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'viz-popup-header-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.onclick = () => {
            popup.remove();
            backdrop.remove();
        };

        header.appendChild(title);
        header.appendChild(closeBtn);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'viz-popup-content';

        popup.appendChild(header);
        popup.appendChild(contentDiv);

        document.body.appendChild(popup);

        if (type === 'chartjs') {
            this.renderChartJSVisualization(configJSON, contentDiv);
        } else if (type === 'apexcharts') {
            this.renderApexChartsVisualization(configJSON, contentDiv);
        } else if (type === 'threejs') {
            this.renderThreeJSVisualization(configJSON, contentDiv);
        }

        this.makeDraggable(popup, header);

        backdrop.onclick = () => {
            popup.remove();
            backdrop.remove();
        };
    }

    /**
     * SECURITY HELPERS
     */

    sanitizeSVG(svgCode) {
        let sanitized = svgCode;
        const dangerousTags = ['script', 'iframe', 'object', 'embed', 'link', 'style', 'foreignObject'];
        dangerousTags.forEach(tag => {
            const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>`, 'gis');
            sanitized = sanitized.replace(regex, '');
            const selfClosing = new RegExp(`<${tag}[^>]*/>`, 'gi');
            sanitized = sanitized.replace(selfClosing, '');
        });
        sanitized = sanitized.replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '');
        sanitized = sanitized.replace(/javascript:/gi, '');
        sanitized = sanitized.replace(/data:text\/html/gi, '');
        return sanitized;
    }

    enhanceSVGElement(svgElement, type) {
        if (!svgElement.hasAttribute('viewBox')) {
            const width = svgElement.getAttribute('width') || '800';
            const height = svgElement.getAttribute('height') || '600';
            svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
        }
        svgElement.removeAttribute('width');
        svgElement.removeAttribute('height');
        svgElement.style.cssText = 'width: 100%; height: auto; display: block; max-width: 100%;';
        if (!svgElement.querySelector('title')) {
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${type.toUpperCase()} Visualization`;
            svgElement.insertBefore(title, svgElement.firstChild);
        }
        svgElement.setAttribute('role', 'img');
        svgElement.setAttribute('aria-label', `${type} diagram`);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * UI HELPERS
     */

    createSVGControls(svgContent, type, wrapper) {
        const controls = document.createElement('div');
        controls.className = 'svg-control-bar';
        controls.style.cssText = 'display: flex; gap: 0.5rem; margin-bottom: 0.5rem; justify-content: flex-end;';

        const expandBtn = this.createControlButton('🔍 Expand', 'Open in popup', () => {
            this.openSVGPopup(svgContent, type, wrapper);
        });

        controls.appendChild(expandBtn);
        return controls;
    }

    createControlButton(text, tooltip, onClick) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.title = tooltip;
        btn.style.cssText = `
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s ease;
    `;
        btn.addEventListener('mouseenter', () => {
            btn.style.background = '#4CAF50';
            btn.style.color = 'white';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.background = 'rgba(255, 255, 255, 0.95)';
            btn.style.color = 'inherit';
        });
        btn.onclick = onClick;
        return btn;
    }

    makeDraggable(element, handle) {
        let isDragging = false;
        let currentX, currentY, initialX, initialY;

        handle.addEventListener('mousedown', (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'I') return;
            isDragging = true;
            initialX = e.clientX - (parseFloat(element.style.left) || 0);
            initialY = e.clientY - (parseFloat(element.style.top) || 0);
            element.style.transform = 'none';
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
            isDragging = false;
        });
    }

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
        font-size: 14px;
    `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    getSVGWrapperStyles(type) {
        const themes = {
            'cad': 'padding: 1.5rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border: 2px solid #8e9eab; border-radius: 8px;',
            'schematic': 'padding: 1.5rem; background: #fffff0; border: 2px solid #ffd700; border-radius: 8px;',
            'blueprint': 'padding: 1.5rem; background: #001f3f; border: 2px solid #0074D9; border-radius: 8px;',
            'molecule': 'padding: 1.5rem; background: #f0f8ff; border: 2px solid #4682b4; border-radius: 8px;',
            'svg': 'padding: 1.5rem; background: white; border: 1px solid #ddd; border-radius: 8px;'
        };
        return themes[type] || themes['svg'];
    }

    /**
     * LIBRARY LOADERS
     */

    loadKaTeX() {
        return new Promise((resolve, reject) => {
            if (!document.querySelector('link[href*="katex.min.css"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
                link.crossOrigin = 'anonymous';
                document.head.appendChild(link);
            }
            if (!document.querySelector('script[src*="katex.min.js"]')) {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
                script.crossOrigin = 'anonymous';
                script.onload = () => resolve();
                script.onerror = (error) => reject(error);
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    loadScript(url) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${url}"]`)) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = url;
            script.onload = () => resolve();
            script.onerror = (error) => reject(error);
            document.head.appendChild(script);
        });
    }

} // End of VisualizationPatchMethods class

// ============================================================================
// END OF INTEGRATION PATCH
// ============================================================================
// This file is REFERENCE ONLY - copy methods into streamingTwoRule.js