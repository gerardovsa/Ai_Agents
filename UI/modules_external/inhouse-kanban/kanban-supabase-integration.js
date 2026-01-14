/**
 * Kanban Supabase Integration - Time Tracking & Analytics
 * 
 * Bridges InHouse Print SQL data with Supabase for enhanced tracking:
 * - Real-time metrics (time in stage, transitions)
 * - Performance tracking (quality, efficiency)
 * - Production log entries
 * - Custom notes and tags
 * - AI predictions and analytics
 * 
 * @created 2025-11-29
 * @version 1.0.0
 */

class KanbanSupabaseIntegration {
    constructor() {
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        this.initialized = false;
        this.activeTimers = new Map(); // ticket_id -> timer data
        this.stageTransitionCache = new Map(); // ticket_id -> last known stage
    }

    /**
     * Initialize integration - verify Supabase connection
     */
    async initialize() {
        try {
            console.log('🔄 Initializing Kanban Supabase Integration...');

            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/health`);
            const data = await response.json();

            if (data.success) {
                this.initialized = true;
                console.log('✅ Supabase integration ready');
                return true;
            } else {
                console.warn('⚠️ Supabase health check failed:', data.message);
                return false;
            }
        } catch (error) {
            console.error('❌ Failed to initialize Supabase integration:', error);
            return false;
        }
    }

    /**
     * Sync job ticket from SQL to Supabase (create or update)
     * @param {Object} job - Job data from InHouse Print SQL
     */
    async syncJobToSupabase(job) {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            const payload = {
                ticket_id: job.TicketID,
                order_id: job.OrderID,
                stage_id: job.StageID,
                stage_description: job.StageDescription,
                client_name: job.ClientName,
                order_date: job.OrderDate,
                short_job_desc: job.ShortJobDesc,
                date_required: job.DateRequired,
                qty: job.Qty,
                cost: job.Cost,
                paper_type: job.PaperType,
                gsm: job.GSM,
                paper_size: job.PaperSize,
                pages: job.Pages,
                job_type: job.JobType,
                bind_type: job.BindType,
                cello_yes: job.CelloYes ? 1 : 0,
                fold_yes: job.FoldYes ? 1 : 0,
                stitch_yes: job.StitchYes ? 1 : 0,
                production_notes: job.ProductionNotes,
                client_order_num: job.ClientOrderNum,
                shipping_desc: job.ShippingDesc,
                invoicing_business: job.InvoicingBusiness,
                priority: job.Priority,
                days_until_due: job.DaysUntilDue,
                days_in_system: job.DaysInSystem,
                urgency_level: job.UrgencyLevel,
                customer_order_count: job.CustomerOrderCount,
                customer_lifetime_value: job.CustomerLifetimeValue,
                ai_priority_score: job.AIPriorityScore,
                priority_label: job.PriorityLabel,
                priority_color: job.PriorityColorHex
            };

            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/sync-job`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Job ${job.TicketID} synced to Supabase`);
                return result;
            } else {
                console.warn(`⚠️ Failed to sync job ${job.TicketID}:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error syncing job ${job.TicketID}:`, error);
            return null;
        }
    }

    /**
     * Record stage transition when job moves between stages
     * @param {number} ticketId - Job ticket ID
     * @param {number} fromStageId - Previous stage ID (null if first stage)
     * @param {number} toStageId - New stage ID
     * @param {string} notes - Optional transition notes
     */
    async recordStageTransition(ticketId, fromStageId, toStageId, notes = null) {
        try {
            const payload = {
                ticket_id: ticketId,
                from_stage_id: fromStageId,
                to_stage_id: toStageId,
                notes: notes
            };

            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/stage-transition`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Stage transition recorded: ${ticketId} (${fromStageId} → ${toStageId})`);

                // Update cache
                this.stageTransitionCache.set(ticketId, toStageId);

                return result;
            } else {
                console.warn(`⚠️ Failed to record transition:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error recording stage transition:`, error);
            return null;
        }
    }

    /**
     * Get time metrics for a job (time in current stage, total time, transitions)
     * @param {number} ticketId - Job ticket ID
     */
    async getJobTimeMetrics(ticketId) {
        try {
            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/job-metrics/${ticketId}`);
            const result = await response.json();

            if (result.success) {
                return result.data;
            } else {
                console.warn(`⚠️ Failed to get metrics for job ${ticketId}:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error getting job metrics:`, error);
            return null;
        }
    }

    /**
     * Add production log entry (note, wastage, stock change, delay, notification)
     * @param {Object} logEntry - Production log data
     */
    async addProductionLogEntry(logEntry) {
        try {
            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/production-log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Production log entry added for ticket ${logEntry.ticket_id}`);
                return result;
            } else {
                console.warn(`⚠️ Failed to add production log:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error adding production log:`, error);
            return null;
        }
    }

    /**
     * Add custom job note
     * @param {number} ticketId - Job ticket ID
     * @param {string} noteText - Note content
     * @param {string} noteType - Type: 'issue', 'quality', 'customer', 'internal'
     * @param {string} priority - Priority: 'high', 'medium', 'low'
     */
    async addJobNote(ticketId, noteText, noteType = 'internal', priority = 'medium') {
        try {
            const payload = {
                ticket_id: ticketId,
                note_text: noteText,
                note_type: noteType,
                priority: priority,
                created_by: window.currentUserInitials || 'SYSTEM'
            };

            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/job-note`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Note added to job ${ticketId}`);
                return result;
            } else {
                console.warn(`⚠️ Failed to add note:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error adding job note:`, error);
            return null;
        }
    }

    /**
     * Record job performance metrics
     * @param {Object} performance - Performance data (hours, quality, costs, etc.)
     */
    async recordJobPerformance(performance) {
        try {
            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/job-performance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(performance)
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Performance recorded for job ${performance.ticket_id}`);
                return result;
            } else {
                console.warn(`⚠️ Failed to record performance:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error recording job performance:`, error);
            return null;
        }
    }

    /**
     * Batch sync multiple jobs at once (for initial load or refresh)
     * @param {Array} jobs - Array of job objects
     */
    async batchSyncJobs(jobs) {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            console.log(`🔄 Batch syncing ${jobs.length} jobs to Supabase...`);

            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/batch-sync`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jobs: jobs.map(job => ({
                        ticket_id: job.TicketID,
                        order_id: job.OrderID,
                        stage_id: job.StageID,
                        stage_description: job.StageDescription,
                        client_name: job.ClientName,
                        order_date: job.OrderDate,
                        short_job_desc: job.ShortJobDesc,
                        date_required: job.DateRequired,
                        qty: job.Qty,
                        cost: job.Cost,
                        priority: job.Priority,
                        days_in_system: job.DaysInSystem,
                        ai_priority_score: job.AIPriorityScore
                    }))
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log(`✅ Batch sync complete: ${result.synced} jobs synced`);
                return result;
            } else {
                console.warn(`⚠️ Batch sync failed:`, result.message);
                return null;
            }
        } catch (error) {
            console.error(`❌ Error in batch sync:`, error);
            return null;
        }
    }

    /**
     * Start tracking time for a job (e.g., when work begins)
     * @param {number} ticketId - Job ticket ID
     * @param {number} stageId - Current stage ID
     */
    startJobTimer(ticketId, stageId) {
        const timerData = {
            ticketId: ticketId,
            stageId: stageId,
            startTime: new Date().toISOString(),
            startTimestamp: Date.now()
        };

        this.activeTimers.set(ticketId, timerData);
        console.log(`⏱️ Started timer for job ${ticketId} in stage ${stageId}`);

        return timerData;
    }

    /**
     * Stop tracking time for a job and record the duration
     * @param {number} ticketId - Job ticket ID
     * @param {string} notes - Optional notes about the work done
     */
    async stopJobTimer(ticketId, notes = null) {
        const timerData = this.activeTimers.get(ticketId);

        if (!timerData) {
            console.warn(`⚠️ No active timer found for job ${ticketId}`);
            return null;
        }

        const endTime = Date.now();
        const durationMs = endTime - timerData.startTimestamp;
        const durationHours = durationMs / (1000 * 60 * 60);

        // Record as production log entry
        const logEntry = {
            ticket_id: ticketId,
            entry_type: 'time_tracking',
            note_text: notes || `Work completed in stage ${timerData.stageId}`,
            delay_hours: durationHours,
            created_by_user: window.currentUserInitials || 'SYSTEM'
        };

        const result = await this.addProductionLogEntry(logEntry);

        // Remove from active timers
        this.activeTimers.delete(ticketId);

        console.log(`⏱️ Stopped timer for job ${ticketId}: ${durationHours.toFixed(2)} hours`);

        return {
            duration_hours: durationHours,
            duration_minutes: Math.round(durationMs / (1000 * 60)),
            log_result: result
        };
    }

    /**
     * Get active timer for a job (if any)
     * @param {number} ticketId - Job ticket ID
     */
    getJobTimer(ticketId) {
        return this.activeTimers.get(ticketId) || null;
    }

    /**
     * Check if stage transition needs to be recorded (compares with cache)
     * @param {number} ticketId - Job ticket ID
     * @param {number} currentStageId - Current stage ID from SQL
     */
    async checkAndRecordTransition(ticketId, currentStageId) {
        const lastKnownStage = this.stageTransitionCache.get(ticketId);

        if (lastKnownStage !== undefined && lastKnownStage !== currentStageId) {
            // Stage changed! Record transition
            console.log(`🔄 Stage change detected for job ${ticketId}: ${lastKnownStage} → ${currentStageId}`);
            await this.recordStageTransition(ticketId, lastKnownStage, currentStageId, 'Auto-detected stage change');
        } else if (lastKnownStage === undefined) {
            // First time seeing this job, record current stage
            this.stageTransitionCache.set(ticketId, currentStageId);
        }
    }

    /**
     * Get all production log entries for a job
     * @param {number} ticketId - Job ticket ID
     */
    async getJobProductionLog(ticketId) {
        try {
            const response = await fetch(`${this.backendUrl}/api/kanban/supabase/production-log/${ticketId}`);
            const result = await response.json();

            if (result.success) {
                return result.data;
            } else {
                console.warn(`⚠️ Failed to get production log:`, result.message);
                return [];
            }
        } catch (error) {
            console.error(`❌ Error getting production log:`, error);
            return [];
        }
    }
}

// Export singleton instance
window.KanbanSupabaseIntegration = window.KanbanSupabaseIntegration || new KanbanSupabaseIntegration();

console.log('✅ Kanban Supabase Integration loaded');
