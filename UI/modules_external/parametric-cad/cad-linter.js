/**
 * CAD Visualization Linter
 * Validates CAD JSON before rendering to catch AI errors
 * Based on Plotly, OpenAI, and Jupyter best practices
 */

class CADLinter {
    constructor() {
        this.errors = [];
        this.warnings = [];
    }

    /**
     * Lint CAD visualization JSON
     * @param {object} cadJson - CAD visualization data
     * @returns {object} { valid: boolean, errors: string[], warnings: string[] }
     */
    lint(cadJson) {
        this.errors = [];
        this.warnings = [];

        if (!cadJson || typeof cadJson !== 'object') {
            this.errors.push('CAD data must be a valid JSON object');
            return this.getResult();
        }

        // Validate required fields
        this.validateRequiredFields(cadJson);

        // Validate model3D structure
        if (cadJson.model3D) {
            this.validateModel3D(cadJson.model3D);
        }

        // Validate camera position
        if (cadJson.camera) {
            this.validateCamera(cadJson.camera);
        }

        // Validate technical drawing (SVG)
        if (cadJson.technical_drawing) {
            this.validateSVG(cadJson.technical_drawing);
        }

        // Validate constraints
        if (cadJson.constraints) {
            this.validateConstraints(cadJson.constraints);
        }

        return this.getResult();
    }

    validateRequiredFields(cadJson) {
        const required = ['type', 'model3D'];

        for (const field of required) {
            if (!cadJson[field]) {
                this.errors.push(`Missing required field: ${field}`);
            }
        }

        // Validate type enum
        const validTypes = ['constrained_engineering_cad', 'parametric_cad', 'concept_sketch'];
        if (cadJson.type && !validTypes.includes(cadJson.type)) {
            this.errors.push(`Invalid type: ${cadJson.type}. Must be one of: ${validTypes.join(', ')}`);
        }
    }

    validateModel3D(model3D) {
        // Validate type
        const validTypes = ['box', 'extrusion', 'parametric'];
        if (!model3D.type) {
            this.errors.push('model3D.type is required');
        } else if (!validTypes.includes(model3D.type)) {
            this.errors.push(`Invalid model3D.type: ${model3D.type}. Must be one of: ${validTypes.join(', ')}`);
        }

        // Validate dimensions (if present)
        if (model3D.dimensions) {
            this.validateDimensions(model3D.dimensions);
        } else if (model3D.type === 'box') {
            this.errors.push('Box type requires dimensions');
        }

        // Validate length for extrusions
        if (model3D.type === 'extrusion') {
            if (!model3D.length) {
                this.errors.push('Extrusion type requires length parameter');
            } else if (model3D.length <= 0) {
                this.errors.push(`Length must be positive, got ${model3D.length}`);
            } else if (model3D.length < 0.001) {
                this.warnings.push(`Length ${model3D.length}m is very small (< 1mm)`);
            } else if (model3D.length > 100) {
                this.warnings.push(`Length ${model3D.length}m is very large (> 100m)`);
            }
        }

        // Validate profile for parametric
        if (model3D.type === 'parametric' && !model3D.profile) {
            this.errors.push('Parametric type requires profile specification');
        }

        // Validate position
        if (model3D.position) {
            this.validateVector3(model3D.position, 'model3D.position');
        }

        // Validate rotation
        if (model3D.rotation) {
            this.validateVector3(model3D.rotation, 'model3D.rotation');
        }
    }

    validateDimensions(dimensions) {
        const requiredDims = ['width', 'height', 'depth'];

        for (const dim of requiredDims) {
            if (dimensions[dim] === undefined) {
                this.errors.push(`Missing dimension: ${dim}`);
            } else if (typeof dimensions[dim] !== 'number') {
                this.errors.push(`Dimension ${dim} must be a number, got ${typeof dimensions[dim]}`);
            } else if (dimensions[dim] <= 0) {
                this.errors.push(`Dimension ${dim} must be positive, got ${dimensions[dim]}`);
            } else if (dimensions[dim] < 0.001) {
                this.warnings.push(`Dimension ${dim} is very small: ${dimensions[dim]}m (< 1mm)`);
            } else if (dimensions[dim] > 100) {
                this.warnings.push(`Dimension ${dim} is very large: ${dimensions[dim]}m (> 100m)`);
            }
        }

        // Check for reasonable aspect ratios
        if (dimensions.width && dimensions.height && dimensions.depth) {
            const ratios = [
                dimensions.width / dimensions.height,
                dimensions.width / dimensions.depth,
                dimensions.height / dimensions.depth
            ];

            for (const ratio of ratios) {
                if (ratio > 1000 || ratio < 0.001) {
                    this.warnings.push(`Extreme aspect ratio detected (${ratio.toFixed(2)}:1) - check dimensions`);
                }
            }
        }
    }

    validateVector3(vector, fieldName) {
        const coords = ['x', 'y', 'z'];

        for (const coord of coords) {
            if (vector[coord] === undefined) {
                this.errors.push(`${fieldName} missing coordinate: ${coord}`);
            } else if (typeof vector[coord] !== 'number') {
                this.errors.push(`${fieldName}.${coord} must be a number, got ${typeof vector[coord]}`);
            } else if (!isFinite(vector[coord])) {
                this.errors.push(`${fieldName}.${coord} must be finite, got ${vector[coord]}`);
            }
        }
    }

    validateCamera(camera) {
        // Validate position
        if (!camera.position) {
            this.errors.push('camera.position is required');
        } else {
            this.validateVector3(camera.position, 'camera.position');

            // Check if camera is at origin (common AI mistake)
            const pos = camera.position;
            if (pos.x === 0 && pos.y === 0 && pos.z === 0) {
                this.errors.push('Camera at origin (0,0,0) - set isometric view (e.g., x:1.5, y:1.5, z:1.5)');
            }

            // Check for very close camera (too zoomed in)
            const distance = Math.sqrt(pos.x ** 2 + pos.y ** 2 + pos.z ** 2);
            if (distance < 0.1) {
                this.warnings.push(`Camera very close to origin (${distance.toFixed(3)}m) - may be too zoomed in`);
            }
        }

        // Validate target
        if (camera.target) {
            this.validateVector3(camera.target, 'camera.target');
        }

        // Check if camera and target are the same (invalid)
        if (camera.position && camera.target) {
            const samePosition =
                camera.position.x === camera.target.x &&
                camera.position.y === camera.target.y &&
                camera.position.z === camera.target.z;

            if (samePosition) {
                this.errors.push('Camera position and target cannot be the same');
            }
        }
    }

    validateSVG(technicalDrawing) {
        let svgContent;

        // Handle both string and object formats
        if (typeof technicalDrawing === 'string') {
            svgContent = technicalDrawing;
        } else if (technicalDrawing.content) {
            svgContent = technicalDrawing.content;
        } else {
            this.errors.push('technical_drawing must be a string or object with content property');
            return;
        }

        // Check SVG structure
        if (!svgContent.trim().startsWith('<svg')) {
            this.errors.push('SVG content must start with <svg> tag');
        }

        if (!svgContent.trim().endsWith('</svg>')) {
            this.errors.push('SVG content must end with </svg> tag');
        }

        // Check for escaped quotes (common AI error)
        if (svgContent.includes('\\"') || svgContent.includes("\\'")) {
            this.errors.push('SVG has escaped quotes - use viewBox="0 0 800 400" not viewBox=\\"0 0 800 400\\"');
        }

        // Check for viewBox attribute
        if (!svgContent.includes('viewBox')) {
            this.warnings.push('SVG missing viewBox attribute - may not scale correctly');
        }

        // Validate viewBox format if present
        const viewBoxMatch = svgContent.match(/viewBox="([^"]+)"/);
        if (viewBoxMatch) {
            const viewBox = viewBoxMatch[1];
            const parts = viewBox.split(/\s+/);

            if (parts.length !== 4) {
                this.errors.push(`viewBox must have 4 numbers, got ${parts.length}`);
            } else {
                const nums = parts.map(p => parseFloat(p));
                if (nums.some(n => isNaN(n))) {
                    this.errors.push(`viewBox contains non-numeric values: ${viewBox}`);
                }
                if (nums.some(n => n < 0)) {
                    this.warnings.push('viewBox contains negative values');
                }
            }
        }

        // Check for width/height attributes
        if (!svgContent.match(/width=["']\d+["']/) && !svgContent.match(/width=["']100%["']/)) {
            this.warnings.push('SVG missing width attribute');
        }

        if (!svgContent.match(/height=["']\d+["']/) && !svgContent.match(/height=["']100%["']/)) {
            this.warnings.push('SVG missing height attribute');
        }
    }

    validateConstraints(constraints) {
        // Validate accuracy/tolerance format
        if (constraints.accuracy) {
            const tolerancePattern = /^±\d+(\.\d+)?(mm|m|cm)$/;
            if (!tolerancePattern.test(constraints.accuracy)) {
                this.errors.push(`Invalid tolerance format: ${constraints.accuracy}. Use format like ±0.1mm`);
            }
        }

        // Check for empty strings
        for (const [key, value] of Object.entries(constraints)) {
            if (typeof value === 'string' && value.trim() === '') {
                this.warnings.push(`Constraint ${key} is empty string - remove or provide value`);
            }
        }
    }

    getResult() {
        return {
            valid: this.errors.length === 0,
            errors: this.errors,
            warnings: this.warnings
        };
    }

    /**
     * Generate detailed error report
     * @returns {string} Formatted error report
     */
    getReport() {
        const result = this.getResult();
        let report = '';

        if (result.valid) {
            report += '✅ CAD Visualization is valid\n';
        } else {
            report += `❌ CAD Visualization has ${result.errors.length} error(s)\n`;
        }

        if (result.errors.length > 0) {
            report += '\nErrors:\n';
            result.errors.forEach((error, i) => {
                report += `  ${i + 1}. ${error}\n`;
            });
        }

        if (result.warnings.length > 0) {
            report += '\nWarnings:\n';
            result.warnings.forEach((warning, i) => {
                report += `  ${i + 1}. ${warning}\n`;
            });
        }

        return report;
    }
}

// Export for use in module
window.CADLinter = CADLinter;
