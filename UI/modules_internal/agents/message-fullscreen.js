/**
 * MESSAGE FULLSCREEN VIEWER
 * Provides fullscreen/popup view for message bubbles
 * 
 * Features:
 * - Double-click any message bubble to open fullscreen
 * - Click fullscreen button in viz-action-bar
 * - ESC key to close
 * - Click overlay to close
 * - Copy content functionality
 * - Smooth animations
 * 
 * Date: December 4, 2025
 */

(function() {
    'use strict';

    /**
     * Open message in fullscreen modal
     * @param {HTMLElement} bubbleElement - The message bubble element to display
     */
    window.openMessageFullscreen = function(bubbleElement) {
        console.log('[Fullscreen] Opening message fullscreen:', bubbleElement);

        // Get bubble content
        let content = '';
        let messageType = 'message';
        
        // Try different selectors to get content
        const contentElement = bubbleElement.querySelector('.ai-message-content') ||
                              bubbleElement.querySelector('.message-content') ||
                              bubbleElement.querySelector('.bubble-content') ||
                              bubbleElement.querySelector('.streaming-content') ||
                              bubbleElement;
        
        content = contentElement.innerHTML;
        
        // Detect message type from classes
        if (bubbleElement.classList.contains('thinking-bubble') || 
            bubbleElement.closest('.thinking-bubble')) {
            messageType = 'Thinking Block';
        } else if (bubbleElement.classList.contains('tool-bubble') || 
                   bubbleElement.closest('.tool-bubble')) {
            messageType = 'Tool Use';
        } else if (bubbleElement.classList.contains('tool-result-bubble') || 
                   bubbleElement.closest('.tool-result-bubble')) {
            messageType = 'Tool Result';
        } else if (bubbleElement.classList.contains('server-tool-bubble') || 
                   bubbleElement.closest('.server-tool-bubble')) {
            messageType = 'Server Tool';
        } else if (bubbleElement.classList.contains('user')) {
            messageType = 'User Message';
        } else {
            messageType = 'AI Message';
        }
        
        // Create fullscreen modal
        const modal = document.createElement('div');
        modal.className = 'message-fullscreen-modal';
        modal.innerHTML = `
            <div class="fullscreen-overlay"></div>
            <div class="fullscreen-content">
                <div class="fullscreen-header">
                    <h3><i class="fas fa-expand"></i> ${messageType}</h3>
                    <div class="fullscreen-actions">
                        <button class="fullscreen-action-btn" data-action="copy" title="Copy content">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                        <button class="fullscreen-action-btn" data-action="close" title="Close (ESC)">
                            <i class="fas fa-times"></i> Close
                        </button>
                    </div>
                </div>
                <div class="fullscreen-body">
                    ${content}
                </div>
            </div>
        `;
        
        // Add to body
        document.body.appendChild(modal);
        
        // Setup event handlers
        setupFullscreenHandlers(modal, content, contentElement);
        
        // Show with animation
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
        
        console.log('[Fullscreen] Modal created and displayed');
    };

    /**
     * Setup event handlers for fullscreen modal
     * @param {HTMLElement} modal - The modal element
     * @param {string} content - The HTML content
     * @param {HTMLElement} contentElement - The original content element
     */
    function setupFullscreenHandlers(modal, content, contentElement) {
        // Close button
        const closeBtn = modal.querySelector('[data-action="close"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                closeMessageFullscreen(modal);
            });
        }
        
        // Copy button
        const copyBtn = modal.querySelector('[data-action="copy"]');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                // Try to get raw text content
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = content;
                const textContent = tempDiv.textContent || tempDiv.innerText || content;
                
                copyToClipboard(textContent, copyBtn);
            });
        }
        
        // Close on overlay click
        const overlay = modal.querySelector('.fullscreen-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                closeMessageFullscreen(modal);
            });
        }
        
        // Close on ESC key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeMessageFullscreen(modal);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        modal._escHandler = escHandler; // Store for cleanup
    }

    /**
     * Close fullscreen modal
     * @param {HTMLElement} modal - The modal element to close
     */
    function closeMessageFullscreen(modal) {
        console.log('[Fullscreen] Closing modal');
        
        // Remove ESC handler
        if (modal._escHandler) {
            document.removeEventListener('keydown', modal._escHandler);
        }
        
        // Animate out
        modal.classList.remove('active');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300); // Wait for CSS transition
    }
    
    window.closeMessageFullscreen = closeMessageFullscreen;

    /**
     * Copy text to clipboard with visual feedback
     * @param {string} text - Text to copy
     * @param {HTMLElement} button - Button element for visual feedback
     */
    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('[Fullscreen] Content copied to clipboard');
            
            // Visual feedback
            if (button) {
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                button.classList.add('copied');
                
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                    button.classList.remove('copied');
                }, 2000);
            }
        }).catch(err => {
            console.error('[Fullscreen] Failed to copy:', err);
            alert('Failed to copy content');
        });
    }

    /**
     * Add double-click handler to message bubble
     * @param {HTMLElement} bubble - The bubble element
     */
    window.addMessageFullscreenHandler = function(bubble) {
        if (!bubble) return;
        
        bubble.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            e.preventDefault();
            window.openMessageFullscreen(bubble);
        });
        
        // Add visual hint
        bubble.style.cursor = 'pointer';
        bubble.title = bubble.title || 'Double-click to view fullscreen';
    };

    console.log('✅ Message Fullscreen Viewer loaded');
    console.log('   Functions available: openMessageFullscreen, addMessageFullscreenHandler');
})();
