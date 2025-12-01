/**
 * FILE: UI/js/tabulator-i18n.js
 * PURPOSE: Internationalization system for Tabulator enhancements
 * 
 * FEATURES:
 * - Multi-language support
 * - Easy translation management
 * - Fallback to English
 * - Dynamic language switching
 * 
 * EXPORTS:
 * - I18nHelper class
 * 
 * LAST MODIFIED: 2025-11-07 - Initial creation
 */

class I18nHelper {
    constructor() {
        this.currentLang = 'en';
        this.translations = {
            en: {
                // Mobile card labels
                'mobile.stock': 'Stock',
                'mobile.status': 'Status',
                'mobile.item': 'Item',

                // Common actions
                'action.save': 'Save',
                'action.cancel': 'Cancel',
                'action.delete': 'Delete',
                'action.export': 'Export',
                'action.refresh': 'Refresh',
                'action.edit': 'Edit',
                'action.view': 'View',
                'action.close': 'Close',

                // Filter messages
                'filter.applied': 'Filter applied',
                'filter.cleared': 'Filters cleared',
                'filter.error': 'Error applying filter',

                // Preset messages
                'preset.saved': 'Preset saved successfully',
                'preset.loaded': 'Preset loaded successfully',
                'preset.deleted': 'Preset deleted successfully',
                'preset.error': 'Error managing preset',

                // Inline editing messages
                'edit.saving': 'Saving changes...',
                'edit.success': 'Changes saved successfully',
                'edit.error': 'Failed to save changes',

                // Bulk action messages
                'bulk.success': 'Bulk action completed',
                'bulk.error': 'Bulk action failed',
                'bulk.noSelection': 'No rows selected',

                // Auto-refresh messages
                'refresh.enabled': 'Auto-refresh enabled',
                'refresh.disabled': 'Auto-refresh disabled',
                'refresh.error': 'Error refreshing data',

                // Export messages
                'export.success': 'Export completed',
                'export.error': 'Export failed',

                // History messages
                'history.noChanges': 'No changes to undo',
                'history.undone': 'Changes undone',
                'history.error': 'Error accessing history',

                // Alert messages
                'alert.triggered': 'Alert triggered',
                'alert.cleared': 'Alerts cleared',

                // Validation messages
                'validation.required': '{field} is required',
                'validation.invalid': '{field} is invalid',
                'validation.tooShort': '{field} is too short',
                'validation.tooLong': '{field} is too long',

                // Confirmation messages
                'confirm.delete': 'Are you sure you want to delete?',
                'confirm.bulkDelete': 'Are you sure you want to delete {count} items?',

                // Error messages
                'error.network': 'Network error occurred',
                'error.timeout': 'Request timed out',
                'error.unknown': 'An unknown error occurred'
            },
            es: {
                // Spanish translations
                'mobile.stock': 'Existencias',
                'mobile.status': 'Estado',
                'mobile.item': 'Artículo',

                'action.save': 'Guardar',
                'action.cancel': 'Cancelar',
                'action.delete': 'Eliminar',
                'action.export': 'Exportar',
                'action.refresh': 'Actualizar',
                'action.edit': 'Editar',
                'action.view': 'Ver',
                'action.close': 'Cerrar',

                'filter.applied': 'Filtro aplicado',
                'filter.cleared': 'Filtros borrados',
                'filter.error': 'Error al aplicar filtro',

                'edit.saving': 'Guardando cambios...',
                'edit.success': 'Cambios guardados exitosamente',
                'edit.error': 'Error al guardar cambios',

                'bulk.noSelection': 'No hay filas seleccionadas',

                'validation.required': '{field} es requerido'
            }
        };
    }

    /**
     * Get translation for key
     */
    t(key, params = {}) {
        const translation = this.translations[this.currentLang]?.[key]
            || this.translations['en'][key]
            || key;

        // Replace parameters
        return translation.replace(/\{(\w+)\}/g, (match, param) => {
            return params[param] !== undefined ? params[param] : match;
        });
    }

    /**
     * Set current language
     */
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            console.log(`[i18n] Language set to: ${lang}`);
            return true;
        }
        console.warn(`[i18n] Language '${lang}' not available`);
        return false;
    }

    /**
     * Add translations for a language
     */
    addTranslations(lang, translations) {
        if (!this.translations[lang]) {
            this.translations[lang] = {};
        }
        Object.assign(this.translations[lang], translations);
        console.log(`[i18n] Added translations for: ${lang}`);
    }

    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLang;
    }

    /**
     * Get available languages
     */
    getAvailableLanguages() {
        return Object.keys(this.translations);
    }
}

// Export to window
window.I18nHelper = I18nHelper;

// Create global instance
window.i18n = new I18nHelper();

console.log('[i18n Helper] Loaded and ready');
