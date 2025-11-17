"""
FILE: AI_infrastructure/sync/kanban_db_sync.py
PURPOSE: Sync InHouse Kanban data from SQL Server to local SQLite database

FEATURES:
- Full sync: Complete database copy
- Incremental sync: Only changed records
- Stage transition tracking
- Analytics calculation
- Error recovery and logging

DEPENDENCIES:
- pymssql (SQL Server connection)
- sqlite3 (built-in, SQLite connection)

EXPORTS:
- KanbanDatabaseSync class
- sync_from_sql_server() function
- calculate_analytics() function

USAGE:
    from AI_infrastructure.sync.kanban_db_sync import KanbanDatabaseSync
    
    syncer = KanbanDatabaseSync()
    syncer.full_sync()  # Initial sync
    syncer.incremental_sync()  # Daily updates

LAST MODIFIED: 2025-11-06 - Initial creation
"""

import sqlite3
import pymssql
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)


def calculate_business_hours(start_dt: datetime, end_dt: datetime) -> float:
    """
    Calculate business hours between two datetimes
    
    Business hours: Mon-Fri 8:00 AM - 6:00 PM (10 hours/day)
    Excludes: Weekends, nights
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        
    Returns:
        float: Business hours between dates
    """
    if start_dt >= end_dt:
        return 0.0
    
    business_hours = 0.0
    current = start_dt
    
    # Define business hours
    BUSINESS_START = 8  # 8 AM
    BUSINESS_END = 18   # 6 PM
    
    while current < end_dt:
        # Get current day's business hours
        current_day_start = current.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        current_day_end = current.replace(hour=BUSINESS_END, minute=0, second=0, microsecond=0)
        
        # Skip weekends (0=Monday, 6=Sunday)
        if current.weekday() >= 5:  # Saturday or Sunday
            current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
            continue
        
        # If before business hours, jump to start of business day
        if current < current_day_start:
            current = current_day_start
        
        # If after business hours for this day, move to next day
        if current >= current_day_end:
            current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
            continue
        
        # Calculate hours for this business day segment
        # End is either end of business day or the target end_dt, whichever is earlier
        segment_end = min(end_dt, current_day_end)
        
        if segment_end > current:
            segment_hours = (segment_end - current).total_seconds() / 3600
            business_hours += segment_hours
        
        # Move to next day's business start
        current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
    
    return round(business_hours, 2)


class KanbanDatabaseSync:
    """
    Synchronizes data from InHousePrint SQL Server to local SQLite database
    Adds custom analytics and tracking capabilities
    """
    
    # SQL Server configuration
    SQL_SERVER_CONFIG = {
        'server': '3.25.76.138',
        'port': 1433,
        'database': 'InHousePrint',
        'user': 'sa',
        'password': 'Jack2011'
    }
    
    def __init__(self, sqlite_path: Optional[str] = None):
        """
        Initialize database sync
        
        Args:
            sqlite_path: Path to SQLite database (default: data/kanban_analytics.db)
        """
        if sqlite_path is None:
            project_root = Path(__file__).parent.parent.parent
            sqlite_path = project_root / 'data' / 'kanban_analytics.db'
        
        self.sqlite_path = Path(sqlite_path)
        self.sqlite_conn = None
        self.sql_server_conn = None
        
        logger.info(f"Kanban DB Sync initialized - SQLite path: {self.sqlite_path}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def connect(self):
        """Establish database connections"""
        try:
            # Connect to SQLite
            self.sqlite_conn = sqlite3.connect(str(self.sqlite_path))
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite: {self.sqlite_path}")
            
            # Connect to SQL Server
            self.sql_server_conn = pymssql.connect(**self.SQL_SERVER_CONFIG)
            logger.info(f"Connected to SQL Server: {self.SQL_SERVER_CONFIG['server']}")
            
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise
    
    def disconnect(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.debug("SQLite connection closed")
        
        if self.sql_server_conn:
            self.sql_server_conn.close()
            logger.debug("SQL Server connection closed")
    
    def initialize_schema(self):
        """
        Create SQLite database schema from SQL file
        """
        schema_path = self.sqlite_path.parent / 'kanban_analytics.sql'
        
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        logger.info(f"Initializing schema from: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cursor = self.sqlite_conn.cursor()
        cursor.executescript(schema_sql)
        self.sqlite_conn.commit()
        
        logger.info("Schema initialized successfully")
    
    def full_sync(self):
        """
        Perform full database sync (initial setup or reset)
        Copies all active jobs from SQL Server to SQLite
        """
        logger.info("Starting FULL SYNC from SQL Server...")
        
        sync_start = datetime.now()
        
        try:
            # Record sync start
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO sync_history (sync_type, sync_start, sync_status)
                VALUES ('full', %s, 'running')
            """, (sync_start.isoformat(),))
            sync_id = cursor.lastrowid
            self.sqlite_conn.commit()
            
            # Sync stages
            stages_synced = self._sync_job_stages()
            
            # Sync clients
            clients_synced = self._sync_clients()
            
            # Sync orders
            orders_synced = self._sync_orders()
            
            # Sync job tickets
            jobs_synced = self._sync_job_tickets()
            
            # Calculate initial analytics
            self._calculate_stage_analytics()
            self._calculate_customer_analytics()
            
            # Update sync record
            sync_end = datetime.now()
            duration = (sync_end - sync_start).total_seconds()
            
            cursor.execute("""
                UPDATE sync_history
                SET sync_end = %s,
                    sync_status = 'success', records_synced = %s, sync_duration_seconds = %s
                WHERE sync_id = %s
            """, (sync_end.isoformat(), jobs_synced + orders_synced + clients_synced, duration, sync_id))
            self.sqlite_conn.commit()
            
            logger.info(f"FULL SYNC completed successfully in {duration:.2f}s")
            logger.info(f"  Stages: {stages_synced}")
            logger.info(f"  Clients: {clients_synced}")
            logger.info(f"  Orders: {orders_synced}")
            logger.info(f"  Jobs: {jobs_synced}")
            
            return {
                'success': True,
                'sync_id': sync_id,
                'duration': duration,
                'records_synced': {
                    'stages': stages_synced,
                    'clients': clients_synced,
                    'orders': orders_synced,
                    'jobs': jobs_synced
                }
            }
            
        except Exception as e:
            logger.error(f"FULL SYNC failed: {e}", exc_info=True)
            
            # Record failure
            cursor.execute("""
                UPDATE sync_history
                SET sync_status = 'failed', error_message = %s
                WHERE sync_id = %s
            """, (str(e), sync_id))
            self.sqlite_conn.commit()
            
            raise
    
    def incremental_sync(self, lookback_hours: int = 24):
        """
        Perform incremental sync (only changed records)
        
        Args:
            lookback_hours: How many hours back to check for changes (default: 24)
        """
        logger.info(f"Starting INCREMENTAL SYNC (lookback: {lookback_hours}h)...")
        
        sync_start = datetime.now()
        
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO sync_history (sync_type, sync_start, sync_status)
                VALUES ('incremental', %s, 'running')
            """, (sync_start.isoformat(),))
            sync_id = cursor.lastrowid
            self.sqlite_conn.commit()
            
            # Sync only recent changes
            jobs_updated = self._sync_job_tickets(incremental=True, lookback_hours=lookback_hours)
            
            # Track stage transitions
            transitions_recorded = self._track_stage_transitions()
            
            # Update analytics
            self._calculate_stage_analytics(date_filter=datetime.now().date())
            
            sync_end = datetime.now()
            duration = (sync_end - sync_start).total_seconds()
            
            cursor.execute("""
                UPDATE sync_history
                SET sync_end = %s,
                    sync_status = 'success', records_updated = %s, sync_duration_seconds = %s
                WHERE sync_id = %s
            """, (sync_end.isoformat(), jobs_updated, duration, sync_id))
            self.sqlite_conn.commit()
            
            logger.info(f"INCREMENTAL SYNC completed in {duration:.2f}s")
            logger.info(f"  Jobs updated: {jobs_updated}")
            logger.info(f"  Transitions recorded: {transitions_recorded}")
            
            return {
                'success': True,
                'sync_id': sync_id,
                'duration': duration,
                'jobs_updated': jobs_updated,
                'transitions_recorded': transitions_recorded
            }
            
        except Exception as e:
            logger.error(f"INCREMENTAL SYNC failed: {e}", exc_info=True)
            
            cursor.execute("""
                UPDATE sync_history
                SET sync_status = 'failed', error_message = %s
                WHERE sync_id = %s
            """, (str(e), sync_id))
            self.sqlite_conn.commit()
            
            raise
    
    def _sync_job_stages(self) -> int:
        """Sync job stages from SQL Server"""
        logger.info("Syncing job stages...")
        
        sql_cursor = self.sql_server_conn.cursor()
        sql_cursor.execute("""
            SELECT StageID, [Desc] as StageDescription
            FROM JobStage
            ORDER BY StageID
        """)
        
        sqlite_cursor = self.sqlite_conn.cursor()
        count = 0
        
        for row in sql_cursor.fetchall():
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO job_stages (stage_id, stage_description, stage_order, synced_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (row[0], row[1], count))
            count += 1
        
        self.sqlite_conn.commit()
        logger.debug(f"Synced {count} job stages")
        return count
    
    def _sync_clients(self) -> int:
        """Sync client information"""
        logger.info("Syncing clients...")
        
        sql_cursor = self.sql_server_conn.cursor()
        sql_cursor.execute("""
            SELECT DISTINCT
                o.ClientName,
                COUNT(DISTINCT o.OrderID) as TotalOrders,
                SUM(CAST(jt.Cost as DECIMAL(10,2))) as TotalValue,
                MIN(o.OrderDate) as FirstOrderDate,
                MAX(o.OrderDate) as LastOrderDate,
                CASE 
                    WHEN COUNT(DISTINCT o.OrderID) >= 20 OR SUM(CAST(jt.Cost as DECIMAL(10,2))) >= 50000 THEN 'VIP'
                    WHEN COUNT(DISTINCT o.OrderID) >= 10 OR SUM(CAST(jt.Cost as DECIMAL(10,2))) >= 20000 THEN 'Premium'
                    WHEN COUNT(DISTINCT o.OrderID) >= 5 THEN 'Regular'
                    ELSE 'New'
                END as CustomerTier
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate >= DATEADD(month, -12, GETDATE())
            GROUP BY o.ClientName
        """)
        
        sqlite_cursor = self.sqlite_conn.cursor()
        count = 0
        
        for row in sql_cursor.fetchall():
            # Convert Decimal to float for SQLite compatibility
            total_value = float(row[2]) if row[2] is not None else 0.0
            
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO clients 
                (client_name, total_orders, total_value, first_order_date, last_order_date, customer_tier, synced_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (row[0], row[1], total_value, row[3], row[4], row[5]))
            count += 1
        
        self.sqlite_conn.commit()
        logger.debug(f"Synced {count} clients")
        return count
    
    def _sync_orders(self) -> int:
        """Sync orders"""
        logger.info("Syncing orders...")
        
        sql_cursor = self.sql_server_conn.cursor()
        sql_cursor.execute("""
            SELECT 
                o.OrderID,
                o.ClientName,
                o.OrderDate,
                o.DateRequired,
                ISNULL(st.ShippingDesc, 'N/A') as ShippingType,
                o.InvoicingBusinessID,
                o.ClientOrderNum
            FROM Orders o
            LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
            WHERE o.OrderDate >= DATEADD(month, -6, GETDATE())
        """)
        
        sqlite_cursor = self.sqlite_conn.cursor()
        count = 0
        
        for row in sql_cursor.fetchall():
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO orders 
                (order_id, client_name, order_date, date_required, shipping_type, invoicing_business_id, client_order_num, synced_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, row)
            count += 1
        
        self.sqlite_conn.commit()
        logger.debug(f"Synced {count} orders")
        return count
    
    def _sync_job_tickets(self, incremental: bool = False, lookback_hours: int = 24) -> int:
        """
        Sync job tickets from SQL Server
        
        Args:
            incremental: If True, only sync recent changes
            lookback_hours: For incremental sync, how far back to look
        """
        logger.info(f"Syncing job tickets (incremental={incremental})...")
        
        # Build query with optional time filter
        time_filter = ""
        if incremental:
            time_filter = f"AND o.OrderDate >= DATEADD(hour, -{lookback_hours}, GETDATE())"
        
        sql_cursor = self.sql_server_conn.cursor()
        sql_cursor.execute(f"""
            SELECT 
                jt.TicketID,
                jt.OrderID,
                jt.StageID,
                js.[Desc] as StageDescription,
                o.ClientName,
                o.OrderDate,
                jt.ShortJobDesc,
                o.DateRequired,
                jt.QTY,
                CAST(jt.Cost as DECIMAL(10,2)) as Cost,
                
                -- Specifications
                ISNULL(pt.[Desc], '') as PaperType,
                ISNULL(gsm.[DESC], '') as GSM,
                ISNULL(ps.[Desc], '') as PaperSize,
                ISNULL(jt.Pages, 0) as Pages,
                ISNULL(jtype.[Desc], '') as JobType,
                ISNULL(bt.BindTypeDesc, '') as BindType,
                
                -- Finishing
                CASE 
                    WHEN (jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                          jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1) THEN 1
                    ELSE 0
                END as CelloYes,
                CASE 
                    WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' THEN 1
                    ELSE 0
                END as FoldYes,
                ISNULL(jt.StitchYes, 0) as StitchYes,
                
                -- Production info
                ISNULL(jt.TicketNotes, '') as ProductionNotes,
                ISNULL(o.ClientOrderNum, '') as ClientOrderNum,
                ISNULL(st.ShippingDesc, 'N/A') as ShippingDesc,
                ISNULL(b.BusinessName, '') as InvoicingBusiness,
                
                -- Calculated fields
                CASE 
                    WHEN o.DateRequired < GETDATE() THEN 'Overdue'
                    WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'Urgent'
                    WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'Normal'
                    ELSE 'Low Priority'
                END as Priority,
                
                DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
                DATEDIFF(day, o.OrderDate, GETDATE()) as DaysInSystem,
                
                CASE
                    WHEN o.DateRequired < GETDATE() THEN 'OVERDUE'
                    WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'CRITICAL'
                    WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'HIGH'
                    WHEN o.DateRequired <= DATEADD(day, 7, GETDATE()) THEN 'MEDIUM'
                    ELSE 'LOW'
                END as UrgencyLevel,
                
                -- Customer metrics
                (SELECT COUNT(*) FROM Orders o2 WHERE o2.ClientName = o.ClientName AND o2.OrderDate >= DATEADD(month, -12, GETDATE())) as CustomerOrderCount,
                (SELECT SUM(CAST(jt2.Cost as DECIMAL(10,2))) FROM JobTickets jt2 INNER JOIN Orders o2 ON jt2.OrderID = o2.OrderID WHERE o2.ClientName = o.ClientName AND o2.OrderDate >= DATEADD(month, -12, GETDATE())) as CustomerLifetimeValue,
                
                -- AI Priority Score
                (
                    CASE WHEN o.DateRequired < GETDATE() THEN 400
                         WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 350
                         WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 250
                         WHEN o.DateRequired <= DATEADD(day, 7, GETDATE()) THEN 150
                         ELSE 50 END
                    +
                    CASE WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 5000 THEN 300
                         WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 2000 THEN 200
                         WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 1000 THEN 150
                         WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 500 THEN 100
                         ELSE 50 END
                ) as AIPriorityScore
                
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            INNER JOIN JobStage js ON jt.StageID = js.StageID
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
            LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
            LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
            LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
            LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
            LEFT JOIN Business b ON o.InvoicingBusinessID = b.BusinessID
            
            WHERE jt.InternalInvoiceComplete = 0
                AND jt.StageID != 10
                {time_filter}
            ORDER BY AIPriorityScore DESC
        """)
        
        sqlite_cursor = self.sqlite_conn.cursor()
        count = 0
        
        # Get column names for dictionary access
        columns = [desc[0] for desc in sql_cursor.description]
        
        for row in sql_cursor.fetchall():
            # Create dictionary for easy access
            row_dict = dict(zip(columns, row))
            
            # Determine priority label and color
            score = row_dict.get('AIPriorityScore') or 0
            if score >= 800:
                priority_label, priority_color = 'CRITICAL', 'red'
            elif score >= 600:
                priority_label, priority_color = 'HIGH', 'orange'
            elif score >= 400:
                priority_label, priority_color = 'URGENT', 'yellow'
            elif score >= 200:
                priority_label, priority_color = 'NORMAL', 'green'
            else:
                priority_label, priority_color = 'LOW', 'blue'
            
            # Convert Decimal types to float for SQLite
            cost = float(row_dict['Cost']) if row_dict['Cost'] is not None else 0.0
            customer_lifetime_value = float(row_dict['CustomerLifetimeValue']) if row_dict['CustomerLifetimeValue'] is not None else 0.0
            
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO job_tickets (
                    ticket_id, order_id, stage_id, stage_description, client_name, order_date,
                    short_job_desc, date_required, qty, cost,
                    paper_type, gsm, paper_size, pages, job_type, bind_type,
                    cello_yes, fold_yes, stitch_yes,
                    production_notes, client_order_num, shipping_desc, invoicing_business,
                    priority, days_until_due, days_in_system, urgency_level,
                    customer_order_count, customer_lifetime_value,
                    ai_priority_score, priority_label, priority_color,
                    synced_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                row_dict['TicketID'], row_dict['OrderID'], row_dict['StageID'], row_dict['StageDescription'],
                row_dict['ClientName'], row_dict['OrderDate'], row_dict['ShortJobDesc'], row_dict['DateRequired'],
                row_dict['QTY'], cost, row_dict['PaperType'], row_dict['GSM'], row_dict['PaperSize'],
                row_dict['Pages'], row_dict['JobType'], row_dict['BindType'], row_dict['CelloYes'],
                row_dict['FoldYes'], row_dict['StitchYes'], row_dict['ProductionNotes'],
                row_dict['ClientOrderNum'], row_dict['ShippingDesc'], row_dict['InvoicingBusiness'],
                row_dict['Priority'], row_dict['DaysUntilDue'], row_dict['DaysInSystem'],
                row_dict['UrgencyLevel'], row_dict['CustomerOrderCount'], customer_lifetime_value,
                row_dict['AIPriorityScore'], priority_label, priority_color
            ))
            count += 1
        
        self.sqlite_conn.commit()
        logger.debug(f"Synced {count} job tickets")
        return count
    
    def _track_stage_transitions(self) -> int:
        """
        Track stage transitions by comparing current and previous stage
        Records when jobs move between stages
        Calculates business_hours and total_hours for each transition
        """
        logger.info("Tracking stage transitions...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Get all jobs and check for stage changes
        cursor.execute("""
            SELECT 
                jt.ticket_id,
                jt.stage_id as current_stage,
                (SELECT stage_id FROM stage_transitions st 
                 WHERE st.ticket_id = jt.ticket_id 
                 ORDER BY transition_date DESC LIMIT 1) as last_recorded_stage,
                (SELECT transition_date FROM stage_transitions st 
                 WHERE st.ticket_id = jt.ticket_id 
                 ORDER BY transition_date DESC LIMIT 1) as last_transition_date
            FROM job_tickets jt
            WHERE jt.stage_id != 9  -- Not complete
        """)
        
        transitions = 0
        now = datetime.now()
        
        for row in cursor.fetchall():
            ticket_id = row[0]
            current_stage = row[1]
            last_stage = row[2]
            last_transition_date_str = row[3]
            
            # Calculate time since last transition
            business_hrs = 0.0
            total_hrs = 0.0
            
            if last_transition_date_str:
                try:
                    last_transition_date = datetime.fromisoformat(last_transition_date_str)
                    total_hrs = (now - last_transition_date).total_seconds() / 3600
                    business_hrs = calculate_business_hours(last_transition_date, now)
                except Exception as e:
                    logger.warning(f"Could not calculate hours for ticket {ticket_id}: {e}")
            
            # If stage changed, record transition
            if last_stage and last_stage != current_stage:
                cursor.execute("""
                    INSERT INTO stage_transitions (
                        ticket_id, from_stage_id, to_stage_id, 
                        business_hours, total_hours
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (ticket_id, last_stage, current_stage, business_hrs, total_hrs))
                transitions += 1
            elif not last_stage:
                # First time seeing this job, record initial stage
                cursor.execute("""
                    INSERT INTO stage_transitions (
                        ticket_id, from_stage_id, to_stage_id,
                        business_hours, total_hours
                    )
                    VALUES (%s, NULL, %s, 0.0, 0.0)
                """, (ticket_id, current_stage))
                transitions += 1
        
        self.sqlite_conn.commit()
        logger.debug(f"Recorded {transitions} stage transitions")
        return transitions
    
    def _calculate_stage_analytics(self, date_filter: Optional[datetime.date] = None):
        """
        Calculate stage analytics for bottleneck detection
        
        Args:
            date_filter: Calculate for specific date (default: today)
        """
        if date_filter is None:
            date_filter = datetime.now().date()
        
        logger.info(f"Calculating stage analytics for {date_filter}...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Get all stages
        cursor.execute("SELECT stage_id FROM job_stages")
        stages = [row[0] for row in cursor.fetchall()]
        
        for stage_id in stages:
            # Count jobs in this stage
            cursor.execute("""
                SELECT COUNT(*) FROM job_tickets WHERE stage_id = %s
            """, (stage_id,))
            jobs_in_progress = cursor.fetchone()[0]
            
            # Calculate average time in stage
            cursor.execute("""
                SELECT 
                    AVG(transition_time_hours),
                    MIN(transition_time_hours),
                    MAX(transition_time_hours),
                    SUM(transition_time_hours)
                FROM stage_transitions
                WHERE to_stage_id = %s
                AND transition_time_hours IS NOT NULL
            """, (stage_id,))
            
            time_stats = cursor.fetchone()
            avg_time = time_stats[0] or 0
            min_time = time_stats[1] or 0
            max_time = time_stats[2] or 0
            total_time = time_stats[3] or 0
            
            # Determine if bottleneck (simple heuristic)
            is_bottleneck = jobs_in_progress > 10 and avg_time > 48  # More than 10 jobs and avg >2 days
            
            if is_bottleneck:
                if jobs_in_progress > 30:
                    severity = 'severe'
                elif jobs_in_progress > 20:
                    severity = 'moderate'
                else:
                    severity = 'minor'
            else:
                severity = 'none'
            
            # Insert or update analytics
            cursor.execute("""
                INSERT OR REPLACE INTO stage_analytics (
                    stage_id, date, jobs_in_progress, avg_time_in_stage_hours,
                    min_time_in_stage_hours, max_time_in_stage_hours, total_time_hours,
                    is_bottleneck, bottleneck_severity, queue_depth, calculated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (stage_id, date_filter.isoformat(), jobs_in_progress, avg_time,
                  min_time, max_time, total_time, 1 if is_bottleneck else 0, severity, jobs_in_progress))
        
        self.sqlite_conn.commit()
        logger.debug(f"Calculated analytics for {len(stages)} stages")
    
    def _calculate_customer_analytics(self):
        """Calculate customer performance analytics"""
        logger.info("Calculating customer analytics...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Get all clients
        cursor.execute("SELECT client_name FROM clients")
        clients = [row[0] for row in cursor.fetchall()]
        
        period_start = (datetime.now() - timedelta(days=30)).date()
        period_end = datetime.now().date()
        
        for client_name in clients:
            # Get client metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(cost) as total_revenue,
                    AVG(cost) as avg_order_value,
                    AVG(days_in_system) as avg_turnaround
                FROM job_tickets
                WHERE client_name = %s
                AND order_date >= %s
            """, (client_name, period_start.isoformat()))
            
            stats = cursor.fetchone()
            
            if stats[0] > 0:  # Has orders in period
                cursor.execute("""
                    INSERT OR REPLACE INTO customer_analytics (
                        client_name, analysis_period, period_start, period_end,
                        total_orders, total_revenue, avg_order_value, avg_turnaround_days,
                        calculated_at
                    )
                    VALUES (%s, 'monthly', %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (client_name, period_start.isoformat(), period_end.isoformat(),
                      stats[0], stats[1] or 0, stats[2] or 0, stats[3] or 0))
        
        self.sqlite_conn.commit()
        logger.debug(f"Calculated analytics for {len(clients)} customers")


# ============================================
# STANDALONE FUNCTIONS
# ============================================

def sync_from_sql_server(full_sync: bool = False, sqlite_path: Optional[str] = None) -> Dict:
    """
    Convenience function to sync data from SQL Server
    
    Args:
        full_sync: If True, perform full sync; otherwise incremental
        sqlite_path: Path to SQLite database (optional)
    
    Returns:
        Dict with sync results
    """
    with KanbanDatabaseSync(sqlite_path) as syncer:
        # Initialize schema if needed
        if not syncer.sqlite_path.exists() or full_sync:
            syncer.initialize_schema()
        
        if full_sync:
            return syncer.full_sync()
        else:
            return syncer.incremental_sync()


def get_sync_history(sqlite_path: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    Get sync history
    
    Args:
        sqlite_path: Path to SQLite database
        limit: Number of records to return
    
    Returns:
        List of sync history records
    """
    if sqlite_path is None:
        project_root = Path(__file__).parent.parent.parent
        sqlite_path = project_root / 'data' / 'kanban_analytics.db'
    
    conn = sqlite3.connect(str(sqlite_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sync_history
        ORDER BY sync_start DESC
        LIMIT %s
    """, (limit,))
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return history


if __name__ == '__main__':
    # CLI usage
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        print("Performing FULL SYNC...")
        result = sync_from_sql_server(full_sync=True)
    else:
        print("Performing INCREMENTAL SYNC...")
        result = sync_from_sql_server(full_sync=False)
    
    print("\nSync completed!")
    print(f"Duration: {result.get('duration', 0):.2f}s")
    
    if 'records_synced' in result:
        print(f"Records synced: {result['records_synced']}")
