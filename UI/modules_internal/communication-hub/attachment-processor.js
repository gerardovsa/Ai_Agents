/**
 * ATTACHMENT PROCESSOR
 * Handles downloading, text extraction, and formatting of email attachments for AI analysis
 * Integrates with Communication Hub export functionality
 */

const AttachmentProcessor = {
    /**
     * Process all attachments for an email and prepare for AI analysis
     * @param {string} emailId - Email ID
     * @param {array} attachments - Array of attachment objects
     * @param {object} communicationHub - Reference to Communication Hub instance
     * @returns {Promise<array>} Processed attachments with text content
     */
    async processAttachmentsForAI(emailId, attachments, communicationHub) {
        if (!attachments || attachments.length === 0) {
            return [];
        }

        const processedAttachments = [];

        for (const attachment of attachments) {
            try {
                const processed = await this.processAttachment(emailId, attachment, communicationHub);
                processedAttachments.push(processed);
            } catch (error) {
                console.error(`[AttachmentProcessor] Failed to process ${attachment.filename}:`, error);
                processedAttachments.push({
                    ...attachment,
                    processing_status: 'failed',
                    processing_error: error.message
                });
            }
        }

        return processedAttachments;
    },

    /**
     * Process single attachment
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<object>} Processed attachment with text content
     */
    async processAttachment(emailId, attachment, communicationHub) {
        const type = this.detectFileType(attachment);

        const processed = {
            ...attachment,
            detected_type: type.category,
            file_type: type.specific,
            processing_status: 'pending',
            text_content: null,
            download_url: null,
            ai_accessible: false
        };

        // Get download URL
        try {
            const userId = window.UserAuth?.user?.id || 1;
            const provider = attachment.provider || 'gmail';

            if (provider === 'gmail') {
                processed.download_url = `${communicationHub.state.apiBase}/gmail/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            } else if (provider === 'outlook') {
                processed.download_url = `${communicationHub.state.apiBase}/outlook/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            }
        } catch (error) {
            console.warn('[AttachmentProcessor] Could not generate download URL:', error);
        }

        // Process based on type
        switch (type.category) {
            case 'text':
                processed.ai_accessible = true;
                processed.text_content = await this.extractTextContent(emailId, attachment, communicationHub);
                processed.processing_status = processed.text_content ? 'success' : 'no_content';
                break;

            case 'document':
                processed.ai_accessible = true;
                processed.text_content = await this.extractDocumentText(emailId, attachment, communicationHub);
                processed.processing_status = processed.text_content ? 'success' : 'requires_extraction';
                break;

            case 'spreadsheet':
                processed.ai_accessible = true;
                processed.text_content = await this.extractSpreadsheetText(emailId, attachment, communicationHub);
                processed.processing_status = processed.text_content ? 'success' : 'requires_extraction';
                break;

            case 'pdf':
                processed.ai_accessible = true; // PDFs supported via Messages API
                processed.document_data = await this.downloadDocumentAsBase64(attachment.id, attachment.filename, communicationHub);
                processed.processing_status = processed.document_data ? 'success' : 'download_failed';
                processed.ai_note = processed.document_data
                    ? 'PDF encoded as base64 for Messages API document analysis'
                    : 'PDF download failed or too large - manual review required';
                break;

            case 'image':
                processed.ai_accessible = true; // Claude supports vision!
                processed.image_data = await this.downloadImageAsBase64(emailId, attachment, communicationHub);
                processed.processing_status = processed.image_data ? 'success' : 'download_failed';
                processed.ai_note = processed.image_data
                    ? 'Image encoded as base64 for Claude Vision API analysis'
                    : 'Image download failed - manual review required';
                break;

            case 'archive':
                processed.ai_accessible = false;
                processed.processing_status = 'archive_not_supported';
                processed.ai_note = 'Archive files must be extracted manually. Contains multiple files.';
                break;

            default:
                processed.ai_accessible = false;
                processed.processing_status = 'unknown_type';
                processed.ai_note = 'File type not recognized for automatic processing.';
        }

        return processed;
    },

    /**
     * Detect file type from filename and mimetype
     * @param {object} attachment - Attachment object
     * @returns {object} Type information
     */
    detectFileType(attachment) {
        const filename = (attachment.filename || '').toLowerCase();
        const mimetype = (attachment.mimetype || '').toLowerCase();

        // Images
        if (mimetype.startsWith('image/') || /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i.test(filename)) {
            return { category: 'image', specific: mimetype.split('/')[1] || 'unknown' };
        }

        // PDFs
        if (mimetype.includes('pdf') || filename.endsWith('.pdf')) {
            return { category: 'pdf', specific: 'pdf' };
        }

        // Word Documents
        if (mimetype.includes('word') || /\.(doc|docx)$/i.test(filename)) {
            return { category: 'document', specific: 'word' };
        }

        // Excel Spreadsheets
        if (mimetype.includes('excel') || mimetype.includes('spreadsheet') || /\.(xls|xlsx)$/i.test(filename)) {
            return { category: 'spreadsheet', specific: 'excel' };
        }

        // CSV
        if (mimetype.includes('csv') || filename.endsWith('.csv')) {
            return { category: 'spreadsheet', specific: 'csv' };
        }

        // PowerPoint
        if (mimetype.includes('presentation') || /\.(ppt|pptx)$/i.test(filename)) {
            return { category: 'document', specific: 'powerpoint' };
        }

        // Text files
        if (mimetype.startsWith('text/') || /\.(txt|md|json|xml|html|css|js)$/i.test(filename)) {
            return { category: 'text', specific: mimetype.split('/')[1] || 'plain' };
        }

        // Archives
        if (/\.(zip|rar|7z|tar|gz)$/i.test(filename)) {
            return { category: 'archive', specific: filename.split('.').pop() };
        }

        return { category: 'unknown', specific: 'unknown' };
    },

    /**
     * Extract text from plain text files
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<string>} Extracted text
     */
    async extractTextContent(emailId, attachment, communicationHub) {
        try {
            const userId = window.UserAuth?.user?.id || 1;
            const provider = attachment.provider || 'gmail';

            let url;
            if (provider === 'gmail') {
                url = `${communicationHub.state.apiBase}/gmail/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            } else {
                url = `${communicationHub.state.apiBase}/outlook/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const text = await response.text();
            return text.substring(0, 50000); // Limit to 50KB for AI processing
        } catch (error) {
            console.error('[AttachmentProcessor] Text extraction failed:', error);
            return null;
        }
    },

    /**
     * Extract text from document files (Word, PowerPoint)
     * Uses backend API endpoint if available
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<string>} Extracted text
     */
    async extractDocumentText(emailId, attachment, communicationHub) {
        try {
            const userId = window.UserAuth?.user?.id || 1;

            // Try document extraction API endpoint
            const response = await fetch(`${communicationHub.state.apiBase}/extract-document-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_id: emailId,
                    attachment_id: attachment.id,
                    user_id: userId,
                    provider: attachment.provider || 'gmail'
                })
            });

            if (response.ok) {
                const data = await response.json();
                return data.text ? data.text.substring(0, 50000) : null;
            }

            // Fallback: Download and note that manual extraction is needed
            return `[Document: ${attachment.filename} - ${this.formatFileSize(attachment.size)}]\nText extraction requires backend processing. Document should be downloaded and reviewed manually.`;
        } catch (error) {
            console.error('[AttachmentProcessor] Document extraction failed:', error);
            return `[Document: ${attachment.filename}]\nText extraction not available. Manual review required.`;
        }
    },

    /**
     * Extract text from spreadsheet files (Excel, CSV)
     * For CSV, can read directly. For Excel, needs backend processing
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<string>} Extracted text (formatted as table)
     */
    async extractSpreadsheetText(emailId, attachment, communicationHub) {
        try {
            const type = this.detectFileType(attachment);

            if (type.specific === 'csv') {
                // CSV can be read directly as text
                const csvText = await this.extractTextContent(emailId, attachment, communicationHub);
                if (csvText) {
                    // Convert CSV to readable table format (first 100 rows)
                    const rows = csvText.split('\n').slice(0, 100);
                    return `[CSV Spreadsheet: ${attachment.filename}]\n\n${rows.join('\n')}\n\n[...remaining rows truncated...]`;
                }
            }

            // For Excel files, need backend processing
            const userId = window.UserAuth?.user?.id || 1;
            const response = await fetch(`${communicationHub.state.apiBase}/extract-spreadsheet-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_id: emailId,
                    attachment_id: attachment.id,
                    user_id: userId,
                    provider: attachment.provider || 'gmail'
                })
            });

            if (response.ok) {
                const data = await response.json();
                return data.text ? data.text.substring(0, 50000) : null;
            }

            return `[Spreadsheet: ${attachment.filename}]\nData extraction requires backend processing. File should be downloaded for manual review.`;
        } catch (error) {
            console.error('[AttachmentProcessor] Spreadsheet extraction failed:', error);
            return `[Spreadsheet: ${attachment.filename}]\nData extraction not available. Manual review required.`;
        }
    },

    /**
     * Extract text from PDF files
     * Uses backend API endpoint for PDF text extraction
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<string>} Extracted text
     */
    async extractPDFText(emailId, attachment, communicationHub) {
        try {
            const userId = window.UserAuth?.user?.id || 1;

            // Try PDF extraction API endpoint
            const response = await fetch(`${communicationHub.state.apiBase}/extract-pdf-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_id: emailId,
                    attachment_id: attachment.id,
                    user_id: userId,
                    provider: attachment.provider || 'gmail'
                })
            });

            if (response.ok) {
                const data = await response.json();
                return data.text ? data.text.substring(0, 50000) : null;
            }

            return `[PDF Document: ${attachment.filename} - ${this.formatFileSize(attachment.size)}]\nPDF text extraction requires backend processing. Document should be downloaded for manual review.`;
        } catch (error) {
            console.error('[AttachmentProcessor] PDF extraction failed:', error);
            return `[PDF Document: ${attachment.filename}]\nText extraction not available. Manual review required.`;
        }
    },

    /**
     * Download image and convert to base64 for Claude Vision API
     * @param {string} emailId - Email ID
     * @param {object} attachment - Attachment object
     * @param {object} communicationHub - Communication Hub instance
     * @returns {Promise<object>} Object with base64 data and media type
     */
    async downloadImageAsBase64(emailId, attachment, communicationHub) {
        try {
            const userId = window.UserAuth?.user?.id || 1;
            const provider = attachment.provider || 'gmail';

            let url;
            if (provider === 'gmail') {
                url = `${communicationHub.state.apiBase}/gmail/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            } else {
                url = `${communicationHub.state.apiBase}/outlook/attachment?message_id=${emailId}&attachment_id=${attachment.id}&user_id=${userId}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            // Get image as blob
            const blob = await response.blob();

            // Check file size (Claude has 5MB limit per image)
            if (blob.size > 5 * 1024 * 1024) {
                console.warn('[AttachmentProcessor] Image too large for Claude Vision:', blob.size);
                return null;
            }

            // Convert to base64
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64data = reader.result.split(',')[1]; // Remove data:image/...;base64, prefix
                    resolve({
                        type: 'base64',
                        media_type: attachment.mimetype || 'image/jpeg',
                        data: base64data
                    });
                };
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (error) {
            console.error('[AttachmentProcessor] Image download failed:', error);
            return null;
        }
    },

    /**
     * Download document (PDF) and convert to base64
     * @param {string} attachmentId - Attachment ID
     * @param {string} filename - Filename
     * @param {object} communicationHub - CommunicationHub instance for API access
     * @returns {Promise<object|null>} Document data in Messages API format or null
     */
    async downloadDocumentAsBase64(attachmentId, filename, communicationHub) {
        try {
            const response = await communicationHub.api.get(
                `/api/communication-hub/attachment/${attachmentId}`,
                { responseType: 'blob' }
            );

            const blob = response.data || response;

            // Check size limit (4.5 MB for documents per Messages API)
            if (blob.size > 4.5 * 1024 * 1024) {
                console.warn('[AttachmentProcessor] Document too large for Messages API:', blob.size);
                return null;
            }

            // Convert to base64
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64data = reader.result.split(',')[1];
                    resolve({
                        type: 'base64',
                        media_type: 'application/pdf',
                        data: base64data
                    });
                };
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (error) {
            console.error('[AttachmentProcessor] Failed to download document as base64:', error);
            return null;
        }
    },

    /**
     * Format file size in human-readable format
     * @param {number} bytes - File size in bytes
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
     * Generate markdown summary of all attachments for AI prompt
     * @param {array} processedAttachments - Array of processed attachments
     * @returns {string} Markdown summary
     */
    generateAttachmentSummary(processedAttachments) {
        if (!processedAttachments || processedAttachments.length === 0) {
            return '';
        }

        const lines = [];
        lines.push('## ATTACHMENTS SUMMARY');
        lines.push('');

        const imageCount = processedAttachments.filter(a => a.detected_type === 'image' && a.image_data).length;
        const pdfCount = processedAttachments.filter(a => a.detected_type === 'pdf' && a.document_data).length;
        const textCount = processedAttachments.filter(a => a.detected_type === 'text').length;

        lines.push(`Total attachments: ${processedAttachments.length}`);
        if (imageCount > 0) lines.push(`- Images: ${imageCount} (included inline for visual analysis)`);
        if (pdfCount > 0) lines.push(`- PDF Documents: ${pdfCount} (included inline for document analysis)`);
        if (textCount > 0) lines.push(`- Text files: ${textCount}`);
        lines.push('');

        processedAttachments.forEach((att, index) => {
            lines.push(`### Attachment ${index + 1}: ${att.filename}`);
            lines.push('');
            lines.push(`- **Type**: ${att.file_type} (${att.detected_type})`);
            lines.push(`- **Size**: ${this.formatFileSize(att.size)}`);
            lines.push(`- **AI Accessible**: ${att.ai_accessible ? 'Yes ✓' : 'No ✗'}`);
            lines.push(`- **Processing Status**: ${att.processing_status}`);

            if (att.download_url) {
                lines.push(`- **Download URL**: \`${att.download_url}\``);
            }

            if (att.ai_note) {
                lines.push(`- **Note**: ${att.ai_note}`);
            }

            // Special handling for images
            if (att.detected_type === 'image' && att.image_data) {
                lines.push('');
                lines.push('**📷 IMAGE INCLUDED**: This image has been embedded in the message for you to analyze visually.');
                lines.push('Please examine the image carefully and describe what you see in relation to the email context.');
            }

            // Text content for documents
            if (att.text_content) {
                lines.push('');
                lines.push('**Extracted Content**:');
                lines.push('```');
                lines.push(att.text_content);
                lines.push('```');
            }

            lines.push('');
            lines.push('---');
            lines.push('');
        });

        return lines.join('\n');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AttachmentProcessor;
}
if (typeof window !== 'undefined') {
    window.AttachmentProcessor = AttachmentProcessor;
}
