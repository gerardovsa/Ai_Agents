/**
 * GSAP RENDERER MODULE
 * ====================
 * 
 * Renders GSAP (GreenSock Animation Platform) animations.
 * GSAP is a professional-grade animation library for complex animations.
 * 
 * Features:
 * - High-performance animations
 * - Timeline-based sequencing
 * - Advanced easing functions
 * - SVG morphing and transformations
 * 
 * CDN: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
 * Docs: https://greensock.com/gsap/
 */

class GSAPRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.timelines = new Map(); // Track timeline instances
    }

    /**
     * Render GSAP animation
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // Ensure GSAP library is loaded
        if (!window.gsap) {
            await this.loadLibrary();
        }

        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('GSAP: Invalid content area');
        }

        // Parse configuration - handle both JSON and JS notation
        let config;
        if (typeof item.content === 'string') {
            const cleanContent = item.content.replace(/<\/?GSAP>/g, '').trim();
            try {
                config = JSON.parse(cleanContent);
            } catch (e) {
                console.warn('GSAP: JSON parse failed, using JavaScript eval', e.message);
                config = (new Function('return ' + cleanContent))();
            }
        } else {
            config = item.content;
        }

        // Create container
        const gsapContainer = document.createElement('div');
        gsapContainer.id = chartId;
        gsapContainer.className = 'gsap-animation-container';
        gsapContainer.style.cssText = `
            width: ${config.width || '100%'};
            height: ${config.height || '400px'};
            position: relative;
            overflow: hidden;
        `;

        // Add HTML content if provided
        if (config.html) {
            gsapContainer.innerHTML = config.html;
        }

        contentArea.appendChild(gsapContainer);

        // Wait for DOM to settle
        await new Promise(resolve => requestAnimationFrame(resolve));

        // Create and execute animation timeline
        const timeline = this.createTimeline(gsapContainer, config);

        // Store timeline instance
        this.timelines.set(chartId, timeline);

        // Add action bar with playback controls
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'gsap');
            this.addPlaybackControls(vizContainer, timeline, chartId);
        }

        return timeline;
    }

    /**
     * Create GSAP timeline from configuration
     */
    createTimeline(container, config) {
        const timeline = window.gsap.timeline({
            repeat: config.repeat !== undefined ? config.repeat : -1,
            repeatDelay: config.repeatDelay || 0,
            yoyo: config.yoyo || false,
            paused: config.paused || false
        });

        // Add animations from config
        if (config.animations && Array.isArray(config.animations)) {
            config.animations.forEach(anim => {
                const targets = container.querySelectorAll(anim.targets || anim.selector);
                const vars = { ...anim.vars };
                const position = anim.position || '+=0';

                if (anim.method === 'from') {
                    timeline.from(targets, vars, position);
                } else if (anim.method === 'fromTo') {
                    timeline.fromTo(targets, anim.fromVars, vars, position);
                } else {
                    timeline.to(targets, vars, position);
                }
            });
        }

        return timeline;
    }

    /**
     * Add playback controls to action bar
     */
    addPlaybackControls(vizContainer, timeline, chartId) {
        const actionBar = vizContainer.querySelector('.viz-unified-action-bar');
        if (!actionBar) return;

        // Play/Pause button
        const playPauseBtn = document.createElement('button');
        playPauseBtn.className = 'viz-action-btn gsap-play-pause';
        playPauseBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path class="play-icon" d="M3 2v12l10-6z" style="display: none;"/>
                <path class="pause-icon" d="M3 2h3v12H3zm7 0h3v12h-3z"/>
            </svg>
        `;
        playPauseBtn.title = 'Play/Pause Animation';

        playPauseBtn.addEventListener('click', () => {
            if (timeline.paused()) {
                timeline.play();
                playPauseBtn.querySelector('.play-icon').style.display = 'none';
                playPauseBtn.querySelector('.pause-icon').style.display = 'block';
            } else {
                timeline.pause();
                playPauseBtn.querySelector('.play-icon').style.display = 'block';
                playPauseBtn.querySelector('.pause-icon').style.display = 'none';
            }
        });

        // Restart button
        const restartBtn = document.createElement('button');
        restartBtn.className = 'viz-action-btn gsap-restart';
        restartBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 3V1L4 5l4 4V7c2.2 0 4 1.8 4 4 0 .5-.1 1-.3 1.4l1.5 1.5c.5-.9.8-1.9.8-2.9 0-3.3-2.7-6-6-6zm0 10c-2.2 0-4-1.8-4-4 0-.5.1-1 .3-1.4L2.8 6.1C2.3 7 2 8 2 9c0 3.3 2.7 6 6 6v2l4-4-4-4v2z"/>
            </svg>
        `;
        restartBtn.title = 'Restart Animation';

        restartBtn.addEventListener('click', () => {
            timeline.restart();
            playPauseBtn.querySelector('.play-icon').style.display = 'none';
            playPauseBtn.querySelector('.pause-icon').style.display = 'block';
        });

        // Insert before close button
        const closeBtn = actionBar.querySelector('.viz-action-btn:last-child');
        if (closeBtn) {
            actionBar.insertBefore(playPauseBtn, closeBtn);
            actionBar.insertBefore(restartBtn, closeBtn);
        } else {
            actionBar.appendChild(playPauseBtn);
            actionBar.appendChild(restartBtn);
        }
    }

    /**
     * Load GSAP library dynamically
     */
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.gsap) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
            script.onload = () => {
                console.log('✅ GSAP library loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load GSAP library'));
            document.head.appendChild(script);
        });
    }

    /**
     * Destroy timeline and cleanup
     */
    destroy(chartId) {
        const timeline = this.timelines.get(chartId);
        if (timeline) {
            timeline.kill();
            this.timelines.delete(chartId);
        }
    }

    /**
     * Destroy all timelines
     */
    destroyAll() {
        this.timelines.forEach((timeline, chartId) => {
            timeline.kill();
        });
        this.timelines.clear();
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.GSAPRenderer = GSAPRenderer;
}
