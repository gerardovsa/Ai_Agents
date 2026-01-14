/**
 * LOTTIE RENDERER MODULE
 * ======================
 * 
 * Renders Lottie vector animations.
 * Lottie is a library for rendering After Effects animations in real-time.
 * 
 * Features:
 * - Lightweight vector animations
 * - JSON-based animation data
 * - Smooth 60fps playback
 * - Small file sizes
 * 
 * CDN: https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js
 * Animations: https://lottiefiles.com/
 */

class LottieRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.animations = new Map(); // Track animation instances
    }

    /**
     * Render Lottie animation
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // Ensure Lottie library is loaded
        if (!window.lottie) {
            await this.loadLibrary();
        }

        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('Lottie: Invalid content area');
        }

        // Parse configuration - handle both JSON and JS notation
        let config;
        if (typeof item.content === 'string') {
            const cleanContent = item.content.replace(/<\/?LOTTIE>/g, '').trim();
            try {
                config = JSON.parse(cleanContent);
            } catch (e) {
                console.warn('Lottie: JSON parse failed, using JavaScript eval', e.message);
                config = (new Function('return ' + cleanContent))();
            }
        } else {
            config = item.content;
        }

        // Create container
        const lottieContainer = document.createElement('div');
        lottieContainer.id = chartId;
        lottieContainer.style.cssText = `
            width: ${config.width || 400}px;
            height: ${config.height || 400}px;
            margin: 0 auto;
            position: relative;
        `;

        contentArea.appendChild(lottieContainer);

        // Load and play animation
        const animationConfig = {
            container: lottieContainer,
            renderer: config.renderer || 'svg',
            loop: config.loop !== undefined ? config.loop : true,
            autoplay: config.autoplay !== undefined ? config.autoplay : true,
            path: config.path || config.animationData
        };

        // If animationData is provided directly instead of path
        if (config.animationData) {
            delete animationConfig.path;
            animationConfig.animationData = config.animationData;
        }

        const animation = window.lottie.loadAnimation(animationConfig);

        // Store instance
        this.animations.set(chartId, animation);

        // Add action bar with play/pause controls
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'lottie');

            // Add custom play/pause button
            this.addPlaybackControls(vizContainer, animation, chartId);
        }

        return animation;
    }

    /**
     * Add playback controls to action bar
     */
    addPlaybackControls(vizContainer, animation, chartId) {
        const actionBar = vizContainer.querySelector('.viz-unified-action-bar');
        if (!actionBar) return;

        const playPauseBtn = document.createElement('button');
        playPauseBtn.className = 'viz-action-btn lottie-play-pause';
        playPauseBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path class="play-icon" d="M3 2v12l10-6z" style="display: none;"/>
                <path class="pause-icon" d="M3 2h3v12H3zm7 0h3v12h-3z"/>
            </svg>
        `;
        playPauseBtn.title = 'Play/Pause Animation';

        let isPlaying = true;

        playPauseBtn.addEventListener('click', () => {
            if (isPlaying) {
                animation.pause();
                playPauseBtn.querySelector('.play-icon').style.display = 'block';
                playPauseBtn.querySelector('.pause-icon').style.display = 'none';
            } else {
                animation.play();
                playPauseBtn.querySelector('.play-icon').style.display = 'none';
                playPauseBtn.querySelector('.pause-icon').style.display = 'block';
            }
            isPlaying = !isPlaying;
        });

        // Insert before close button
        const closeBtn = actionBar.querySelector('.viz-action-btn:last-child');
        if (closeBtn) {
            actionBar.insertBefore(playPauseBtn, closeBtn);
        } else {
            actionBar.appendChild(playPauseBtn);
        }
    }

    /**
     * Load Lottie library dynamically
     */
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.lottie) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js';
            script.onload = () => {
                console.log('✅ Lottie library loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load Lottie library'));
            document.head.appendChild(script);
        });
    }

    /**
     * Destroy animation instance and cleanup
     */
    destroy(chartId) {
        const animation = this.animations.get(chartId);
        if (animation) {
            animation.destroy();
            this.animations.delete(chartId);
        }
    }

    /**
     * Destroy all animations
     */
    destroyAll() {
        this.animations.forEach((animation, chartId) => {
            animation.destroy();
        });
        this.animations.clear();
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.LottieRenderer = LottieRenderer;
}
