/**
 * FILE: UI/js/tabulator-validation.js
 * PURPOSE: Input validation utilities for Tabulator enhancements
 * 
 * FEATURES:
 * - Type validation (string, number, date, array, object)
 * - Required field validation
 * - Range validation
 * - Custom validation rules
 * - Descriptive error messages
 * 
 * EXPORTS:
 * - ValidationHelper class
 * 
 * LAST MODIFIED: 2025-11-07 - Initial creation
 */

class ValidationHelper {
    /**
     * Validate string parameter
     */
    static validateString(value, paramName, required = true, minLength = 0, maxLength = Infinity) {
        if (required && (value === null || value === undefined || value === '')) {
            return { valid: false, error: `${paramName} is required` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        if (typeof value !== 'string') {
            return { valid: false, error: `${paramName} must be a string` };
        }

        if (value.length < minLength) {
            return { valid: false, error: `${paramName} must be at least ${minLength} characters` };
        }

        if (value.length > maxLength) {
            return { valid: false, error: `${paramName} must be at most ${maxLength} characters` };
        }

        return { valid: true };
    }

    /**
     * Validate number parameter
     */
    static validateNumber(value, paramName, required = true, min = -Infinity, max = Infinity) {
        if (required && (value === null || value === undefined)) {
            return { valid: false, error: `${paramName} is required` };
        }

        if (!required && value === undefined) {
            return { valid: true };
        }

        const num = Number(value);
        if (isNaN(num)) {
            return { valid: false, error: `${paramName} must be a number` };
        }

        if (num < min) {
            return { valid: false, error: `${paramName} must be at least ${min}` };
        }

        if (num > max) {
            return { valid: false, error: `${paramName} must be at most ${max}` };
        }

        return { valid: true, value: num };
    }

    /**
     * Validate date parameter
     */
    static validateDate(value, paramName, required = true) {
        if (required && !value) {
            return { valid: false, error: `${paramName} is required` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        const date = new Date(value);
        if (isNaN(date.getTime())) {
            return { valid: false, error: `${paramName} must be a valid date` };
        }

        return { valid: true, value: date };
    }

    /**
     * Validate array parameter
     */
    static validateArray(value, paramName, required = true, minLength = 0, maxLength = Infinity) {
        if (required && (!value || !Array.isArray(value))) {
            return { valid: false, error: `${paramName} is required and must be an array` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        if (!Array.isArray(value)) {
            return { valid: false, error: `${paramName} must be an array` };
        }

        if (value.length < minLength) {
            return { valid: false, error: `${paramName} must have at least ${minLength} items` };
        }

        if (value.length > maxLength) {
            return { valid: false, error: `${paramName} must have at most ${maxLength} items` };
        }

        return { valid: true };
    }

    /**
     * Validate object parameter
     */
    static validateObject(value, paramName, required = true) {
        if (required && (!value || typeof value !== 'object' || Array.isArray(value))) {
            return { valid: false, error: `${paramName} is required and must be an object` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        if (typeof value !== 'object' || Array.isArray(value)) {
            return { valid: false, error: `${paramName} must be an object` };
        }

        return { valid: true };
    }

    /**
     * Validate table key exists
     */
    static validateTableKey(helper, tableKey) {
        const validation = this.validateString(tableKey, 'tableKey', true);
        if (!validation.valid) return validation;

        const table = helper.getTable(tableKey);
        if (!table) {
            return { valid: false, error: `Table '${tableKey}' not found` };
        }

        return { valid: true, value: table };
    }

    /**
     * Validate URL parameter
     */
    static validateUrl(value, paramName, required = true) {
        if (required && !value) {
            return { valid: false, error: `${paramName} is required` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        try {
            new URL(value);
            return { valid: true };
        } catch (e) {
            return { valid: false, error: `${paramName} must be a valid URL` };
        }
    }

    /**
     * Validate field exists in table
     */
    static validateField(table, fieldName, paramName = 'field') {
        const validation = this.validateString(fieldName, paramName, true);
        if (!validation.valid) return validation;

        const columns = table.getColumnDefinitions();
        const fieldExists = columns.some(col => col.field === fieldName);

        if (!fieldExists) {
            return { valid: false, error: `Field '${fieldName}' does not exist in table` };
        }

        return { valid: true };
    }

    /**
     * Validate enum value
     */
    static validateEnum(value, paramName, allowedValues, required = true) {
        if (required && !value) {
            return { valid: false, error: `${paramName} is required` };
        }

        if (!required && !value) {
            return { valid: true };
        }

        if (!allowedValues.includes(value)) {
            return {
                valid: false,
                error: `${paramName} must be one of: ${allowedValues.join(', ')}`
            };
        }

        return { valid: true };
    }

    /**
     * Batch validate multiple parameters
     */
    static validateAll(validations) {
        const errors = [];

        for (const validation of validations) {
            if (!validation.valid) {
                errors.push(validation.error);
            }
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            error: errors.length > 0 ? errors.join('; ') : null
        };
    }
}

// Export to window
window.ValidationHelper = ValidationHelper;

console.log('[Validation Helper] Loaded and ready');
