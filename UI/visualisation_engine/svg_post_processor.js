/**
 * SVG Post-Processor - Client-Side
 * Fixes browser rendering bugs in SVG visualizations
 * 
 * BOLD TEXT BASELINE BUG:
 * Browsers incorrectly position bold text when using dominant-baseline="middle"
 * because they calculate the bounding box with regular font metrics but render
 * with bold font metrics, causing ~5-7px downward shift.
 * 
 * Solution: Convert dominant-baseline="middle" to manual baseline positioning
 * for all bold text elements.
 */

/**
 * Fix SVG bold text baseline bug
 * @param {string} svgString - Raw SVG XML string
 * @returns {string} Fixed SVG XML string
 */
function fixSVGBoldBaselineBug(svgString) {
    if (!svgString || !svgString.includes('<text')) {
        return svgString;
    }

    try {
        // Parse SVG string to DOM
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svgString, 'image/svg+xml');

        // Check for parsing errors
        const parserError = svgDoc.querySelector('parsererror');
        if (parserError) {
            console.warn('[SVG_POST_PROCESSOR] XML parsing failed, returning original:', parserError.textContent);
            return svgString;
        }

        let fixesApplied = 0;

        // Find all text elements
        const textElements = svgDoc.querySelectorAll('text');

        textElements.forEach(textElem => {
            // Check if this text element needs fixing
            const isBold = isBoldText(textElem);
            const usesMiddleBaseline = usesMiddleBaseline_(textElem);

            if (!isBold || !usesMiddleBaseline) {
                return; // Skip this element
            }

            // Extract font size
            const fontSize = extractFontSize(textElem);

            // Extract current Y position
            const yAttr = textElem.getAttribute('y');
            if (!yAttr) {
                return;
            }

            try {
                const yCenter = parseFloat(yAttr);
                if (isNaN(yCenter)) {
                    return;
                }

                // Calculate correct baseline position
                // Formula: y_baseline = y_center - (font_size × 0.5)
                // This compensates for browser shifting bold text DOWN by ~0.5em
                const yBaseline = yCenter - (fontSize * 0.5);

                // Apply fix
                textElem.setAttribute('y', yBaseline.toFixed(2));

                // Remove dominant-baseline attribute
                textElem.removeAttribute('dominant-baseline');

                fixesApplied++;
                console.debug(`[SVG_POST_PROCESSOR] Fixed bold text: y=${yCenter} → ${yBaseline.toFixed(2)} (font-size=${fontSize})`);
            } catch (e) {
                console.warn('[SVG_POST_PROCESSOR] Error processing text element:', e);
            }
        });

        if (fixesApplied > 0) {
            console.log(`[SVG_POST_PROCESSOR] ✅ Fixed ${fixesApplied} bold text baseline issue(s)`);
        }

        // Convert back to string
        const serializer = new XMLSerializer();
        return serializer.serializeToString(svgDoc.documentElement);

    } catch (error) {
        console.error('[SVG_POST_PROCESSOR] Unexpected error:', error);
        return svgString;
    }
}

/**
 * Check if text element uses bold font-weight
 * @param {Element} elem - SVG text element
 * @returns {boolean}
 */
function isBoldText(elem) {
    // Check font-weight attribute
    if (elem.getAttribute('font-weight') === 'bold') {
        return true;
    }

    // Check style attribute
    const style = elem.getAttribute('style') || '';
    if (style.replace(/\s/g, '').includes('font-weight:bold')) {
        return true;
    }
    if (/font-weight:\s*bold/.test(style)) {
        return true;
    }

    return false;
}

/**
 * Check if element uses dominant-baseline='middle'
 * @param {Element} elem - SVG text element
 * @returns {boolean}
 */
function usesMiddleBaseline_(elem) {
    return elem.getAttribute('dominant-baseline') === 'middle';
}

/**
 * Extract font size from element
 * @param {Element} elem - SVG text element
 * @returns {number} Font size in pixels (default: 14)
 */
function extractFontSize(elem) {
    const defaultSize = 14.0;

    // Check font-size attribute
    const fontSizeAttr = elem.getAttribute('font-size');
    if (fontSizeAttr) {
        const value = parseFloat(fontSizeAttr.replace(/[^\d.]/g, ''));
        if (!isNaN(value)) {
            return value;
        }
    }

    // Check style attribute
    const style = elem.getAttribute('style') || '';
    const fontMatch = style.match(/font-size:\s*(\d+(?:\.\d+)?)/);
    if (fontMatch) {
        const value = parseFloat(fontMatch[1]);
        if (!isNaN(value)) {
            return value;
        }
    }

    return defaultSize;
}

/**
 * Optimize SVG content (main entry point)
 * @param {string} svgString - Raw SVG from AI agent
 * @returns {string} Optimized and fixed SVG
 */
function optimizeSVG(svgString) {
    // Apply bold baseline fix
    svgString = fixSVGBoldBaselineBug(svgString);

    // Add additional optimizations here as needed
    // - Remove duplicate IDs
    // - Optimize path data
    // - Minify if requested

    return svgString;
}

/**
 * Validate SVG syntax
 * @param {string} svgString - SVG to validate
 * @returns {{isValid: boolean, error: string|null}}
 */
function validateSVG(svgString) {
    try {
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svgString, 'image/svg+xml');
        const parserError = svgDoc.querySelector('parsererror');

        if (parserError) {
            return {
                isValid: false,
                error: parserError.textContent
            };
        }

        return {
            isValid: true,
            error: null
        };
    } catch (e) {
        return {
            isValid: false,
            error: e.message
        };
    }
}

// Export functions for use in visualization engine
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fixSVGBoldBaselineBug,
        optimizeSVG,
        validateSVG
    };
}

// Also make available globally for browser use
if (typeof window !== 'undefined') {
    window.SVGPostProcessor = {
        fixSVGBoldBaselineBug,
        optimizeSVG,
        validateSVG
    };
}
