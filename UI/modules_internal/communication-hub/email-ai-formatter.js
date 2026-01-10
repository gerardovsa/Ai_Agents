/**
 * EMAIL AI FORMATTER
 * Formats emails with full thread history, attachments, and metadata for AI analysis
 * Generates markdown-formatted content optimized for LLM processing
 */

const EmailAIFormatter = {
    /**
     * Generate enhanced markdown email prompt for AI analysis
     * @param {object} fullEmail - Complete email data with thread history
     * @param {string} action - Quick action type: analyze, draft, quote, lookup, summarize
     * @returns {string} Markdown-formatted prompt
     */
    generateEnhancedPrompt(fullEmail, action = 'analyze') {
        const markdown = [];

        // Header with context
        markdown.push('EMAIL ASSIGNMENT - FIRST TIME ANALYSIS');
        markdown.push('');
        markdown.push('You have been assigned this email for processing. This is the FIRST TIME you are seeing this email.');
        markdown.push('');

        // Action-specific instructions
        markdown.push('YOUR TASK');
        markdown.push('');
        markdown.push(this.getActionInstructions(action));
        markdown.push('');

        // Email metadata
        markdown.push('EMAIL METADATA');
        markdown.push('');
        markdown.push(`- From: ${fullEmail.from || 'Unknown'}`);
        markdown.push(`- To: ${fullEmail.to || 'Unknown'}`);
        markdown.push(`- CC: ${fullEmail.cc || 'None'}`);
        markdown.push(`- Subject: ${fullEmail.subject || '(No Subject)'}`);
        markdown.push(`- Date: ${fullEmail.date || 'Unknown'}`);
        markdown.push(`- Provider: ${fullEmail.provider || 'Unknown'}`);
        markdown.push(`- Email ID: ${fullEmail.id || 'Unknown'}`);
        markdown.push('');

        // Thread history (if available)
        if (fullEmail.thread_history && fullEmail.thread_history.length > 0) {
            markdown.push('EMAIL THREAD HISTORY');
            markdown.push('');
            markdown.push('This email is part of an ongoing conversation. Messages are shown in chronological order (oldest first):');
            markdown.push('');

            fullEmail.thread_history.forEach((msg, index) => {
                markdown.push(`Message ${index + 1} of ${fullEmail.thread_history.length}`);
                markdown.push('');
                markdown.push(`From: ${msg.from || 'Unknown'}`);
                markdown.push(`Date: ${msg.date || 'Unknown'}`);
                markdown.push(`Subject: ${msg.subject || '(No Subject)'}`);
                markdown.push('');
                markdown.push('Content:');
                markdown.push('```');
                markdown.push(msg.body || '(No content)');
                markdown.push('```');
                markdown.push('');

                // Attachments for this message
                if (msg.attachments && msg.attachments.length > 0) {
                    markdown.push('Attachments:');
                    msg.attachments.forEach(att => {
                        markdown.push(`- ${this.formatAttachment(att)}`);
                    });
                    markdown.push('');
                }

                markdown.push('---');
                markdown.push('');
            });
        }

        // Current email body
        markdown.push('CURRENT EMAIL BODY');
        markdown.push('');
        markdown.push('```');
        // ✅ FIX: Use body_text (plain text), or convert body_html to text, or fallback to snippet
        let bodyContent = fullEmail.body_text || '';
        if (!bodyContent && fullEmail.body_html) {
            // Strip HTML tags to get plain text
            bodyContent = this.stripHtml(fullEmail.body_html);
        }
        if (!bodyContent) {
            bodyContent = fullEmail.body || fullEmail.snippet || '(No content)';
        }
        markdown.push(bodyContent);
        markdown.push('```');
        markdown.push('');

        // Attachments
        if (fullEmail.attachments && fullEmail.attachments.length > 0) {
            markdown.push('ATTACHMENTS');
            markdown.push('');
            markdown.push(`This email has ${fullEmail.attachments.length} attachment(s):`);
            markdown.push('');

            fullEmail.attachments.forEach((att, index) => {
                markdown.push(`Attachment ${index + 1}`);
                markdown.push('');
                markdown.push(this.formatAttachment(att));
                markdown.push('');
            });
        }

        // Response requirements
        markdown.push('RESPONSE REQUIREMENTS');
        markdown.push('');
        markdown.push('Please respond with:');
        markdown.push('');
        markdown.push('1. Acknowledgment: Confirm you have received and reviewed the email');
        markdown.push('2. Summary: Key points, requests, and context from the email (and thread history if applicable)');
        markdown.push('3. Next Actions: Specific actions you can take to help with this email');
        markdown.push('4. Questions: Any clarifications needed before proceeding');
        markdown.push('');

        return markdown.join('\n');
    },

    /**
     * Get action-specific instructions
     * @param {string} action - Action type
     * @returns {string} Instructions text
     */
    getActionInstructions(action) {
        const instructions = {
            analyze: `Analyze this email thoroughly and provide:
A comprehensive summary of the email content and any thread history
Identification of key points, requests, and action items
Assessment of urgency level (High/Medium/Low)
Recommended next steps and timeline`,

            draft_reply: `Your goal is to DRAFT A RESPONSE EMAIL. You should:
Search for relevant information to inform your response
Draft a professional, contextually-appropriate reply
Include all necessary details and address all points raised
Format the response ready to send (with greeting, body, closing)`,

            extract_tasks: `Your goal is to EXTRACT ACTION ITEMS. You should:
Identify all tasks, action items, and deliverables mentioned in the email
Organize them by priority and deadline
Note any dependencies or prerequisites
Provide a clear checklist format with owners and due dates`,

            discuss: `Your goal is to DISCUSS AND CLARIFY. You should:
Identify any ambiguous points or missing information in the email
Ask clarifying questions to better understand the request
Suggest different approaches or considerations
Engage in a collaborative dialogue to determine the best path forward`,

            summarize: `Your goal is to SUMMARIZE WITH OPTIONS. You should:
Provide a concise summary of the email and situation
Present 3-5 distinct response options with pros/cons
Recommend your preferred approach with reasoning
Outline next steps for each option`
        };

        return instructions[action] || instructions.analyze;
    },

    /**
     * Format attachment information
     * @param {object} att - Attachment object
     * @returns {string} Formatted attachment string
     */
    formatAttachment(att) {
        const parts = [];

        // Basic info - handle both 'filename' (old) and 'name' (new) fields
        const filename = att.filename || att.name || 'Unknown filename';
        parts.push(`📎 ${filename}`);

        // File type and size
        const type = this.getAttachmentType(att);
        const size = att.size ? this.formatFileSize(att.size) : 'Unknown size';
        const contentType = att.contentType || att.mimeType || 'unknown';
        parts.push(`(${type}, ${size}, ${contentType})`);

        // Content handling
        if (type === 'Image') {
            parts.push('\n  - ⚠️ Image attachment - Visual content cannot be directly analyzed as text');
            parts.push('\n  - Consider asking user if they need image analysis or OCR');
        } else if (type === 'PDF' || type === 'Document') {
            if (att.text_content) {
                parts.push('\n  - Text content extracted and available for analysis');
                parts.push(`\n  - Content preview: ${att.text_content.substring(0, 200)}...`);
            } else if (att.download_url || att.id) {
                if (att.download_url) {
                    parts.push(`\n  - Download URL available: \`${att.download_url}\``);
                }
                if (att.id) {
                    parts.push(`\n  - Attachment ID: ${att.id}`);
                }
                parts.push('\n  - ⚠️ Text extraction may be needed');
            } else {
                parts.push('\n  - ⚠️ Content not yet extracted - may need to request access');
            }
        } else {
            if (att.download_url) {
                parts.push(`\n  - Download URL: \`${att.download_url}\``);
            }
            if (att.id && !att.download_url) {
                parts.push(`\n  - Attachment ID: ${att.id}`);
            }
        }

        return parts.join(' ');
    },

    /**
     * Determine attachment type from filename/mimetype
     * @param {object} att - Attachment object
     * @returns {string} Human-readable type
     */
    getAttachmentType(att) {
        // Handle both old and new field names
        const filename = (att.filename || att.name || '').toLowerCase();
        const mimetype = (att.mimetype || att.mimeType || att.contentType || '').toLowerCase();

        if (mimetype.startsWith('image/') || /\.(jpg|jpeg|png|gif|bmp|webp)$/.test(filename)) {
            return 'Image';
        } else if (mimetype.includes('pdf') || filename.endsWith('.pdf')) {
            return 'PDF';
        } else if (mimetype.includes('word') || /\.(doc|docx)$/.test(filename)) {
            return 'Document (Word)';
        } else if (mimetype.includes('excel') || mimetype.includes('spreadsheet') || /\.(xls|xlsx|csv)$/.test(filename)) {
            return 'Spreadsheet';
        } else if (mimetype.includes('presentation') || /\.(ppt|pptx)$/.test(filename)) {
            return 'Presentation';
        } else if (mimetype.startsWith('text/') || /\.(txt|md|json|xml)$/.test(filename)) {
            return 'Text File';
        } else if (filename.endsWith('.zip') || filename.endsWith('.rar') || filename.endsWith('.7z')) {
            return 'Archive';
        } else {
            return 'File';
        }
    },

    /**
     * Format file size in human-readable format
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted size
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} bytes`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
        return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    },

    /**
     * Generate complete email metadata for thread storage
     * @param {object} fullEmail - Complete email data
     * @param {string} action - Selected action
     * @returns {object} Metadata object
     */
    generateEmailMetadata(fullEmail, action) {
        return {
            context_type: 'email',
            email_id: fullEmail.id,
            email_subject: fullEmail.subject,
            email_from: fullEmail.from,
            email_to: fullEmail.to,
            email_cc: fullEmail.cc,
            email_date: fullEmail.date,
            email_provider: fullEmail.provider,
            email_thread_count: fullEmail.thread_history ? fullEmail.thread_history.length + 1 : 1,
            email_has_attachments: (fullEmail.attachments && fullEmail.attachments.length > 0),
            email_attachment_count: fullEmail.attachments ? fullEmail.attachments.length : 0,
            email_first_time_assignment: true,
            email_action_type: action,
            assigned_at: new Date().toISOString()
        };
    },

    /**
     * Generate Claude-compatible message content with images
     * Follows Anthropic Messages API format for multimodal messages
     * @param {string} textPrompt - Markdown text prompt
     * @param {array} processedAttachments - Processed attachments with image data
     * @returns {array} Claude message content blocks
     */
    generateClaudeMessageContent(textPrompt, processedAttachments) {
        // ✅ FIX: Return text-only content with attachment metadata
        // Base64 data will be added by backend when calling Claude API
        let message = textPrompt;

        // Add attachment placeholders (NO base64 data)
        if (processedAttachments && processedAttachments.length > 0) {
            const imageAttachments = processedAttachments.filter(a => a.detected_type === 'image');
            const pdfAttachments = processedAttachments.filter(a => a.detected_type === 'pdf');

            if (imageAttachments.length > 0 || pdfAttachments.length > 0) {
                message += '\n\n📎 **ATTACHMENTS FOR AI ANALYSIS:**\n\n';

                imageAttachments.forEach(att => {
                    message += `🖼️ **Image**: ${att.filename} (${this.formatFileSize(att.size)})\n`;
                    message += `   - Type: ${att.file_type}\n`;
                    message += `   - Attachment ID: ${att.attachment_id || att.id}\n`;
                    message += `   - Status: Ready for visual analysis\n\n`;
                });

                pdfAttachments.forEach(att => {
                    message += `📄 **PDF Document**: ${att.filename} (${this.formatFileSize(att.size)})\n`;
                    message += `   - Type: ${att.file_type}\n`;
                    message += `   - Attachment ID: ${att.attachment_id || att.id}\n`;
                    message += `   - Status: Ready for document analysis\n\n`;
                });

                message += '\n**Note**: Attachments will be automatically included for AI analysis.\n';
            }
        }

        return message;
    },

    /**
     * Format file size helper (duplicated for convenience)
     * @param {number} bytes - File size
     * @returns {string} Formatted size
     */
    formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        if (bytes < 1024) return `${bytes} bytes`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
        return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    },

    /**
     * Strip HTML tags to get plain text
     * @param {string} html - HTML content
     * @returns {string} Plain text
     */
    stripHtml(html) {
        if (!html) return '';

        // ✅ FIX: Remove <img> tags with cid: URLs before parsing to prevent ERR_UNKNOWN_URL_SCHEME errors
        // Email inline images use cid: (Content-ID) URLs which browsers cannot load
        html = html.replace(/<img[^>]*>/gi, '[Image]');

        // Create a temporary div to parse HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        // Get text content (browsers handle entity decoding)
        let text = tempDiv.textContent || tempDiv.innerText || '';

        // Clean up extra whitespace
        text = text.replace(/\s+/g, ' ').trim();

        // Convert common HTML entities manually if needed
        text = text.replace(/&nbsp;/g, ' ')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'");

        return text;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmailAIFormatter;
}
if (typeof window !== 'undefined') {
    window.EmailAIFormatter = EmailAIFormatter;
}
