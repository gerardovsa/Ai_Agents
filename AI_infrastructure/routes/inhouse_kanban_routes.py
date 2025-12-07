"""
AI_infrastructure/routes/inhouse_kanban_routes.py
InHousePrint Kanban Board Routes
=================================
REST API endpoints for InHousePrint production workflow Kanban.

Connects to SQL Server database for real-time job tracking.

Fixed: December 7, 2025
- All cursor management issues resolved
- Proper resource cleanup in all functions
- Exception-safe database operations

Endpoints:
    GET    /api/inhouse-kanban/jobs           - List active jobs
    GET    /api/inhouse-kanban/jobs/:id       - Get job details
    GET    /api/inhouse-kanban/stages         - Get stage summary
    GET    /api/inhouse-kanban/metrics        - Get dashboard metrics
    GET    /api/inhouse-kanban/health         - Health check
"""

from flask import Blueprint, request, jsonify
import pymssql
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Create blueprint
inhouse_kanban_bp = Blueprint('inhouse_kanban', __name__, url_prefix='/api/inhouse-kanban')

# Database connection configuration
# Uses pymssql (simpler than pyodbc, no ODBC driver needed)
DB_CONFIG = {
    'server': '3.25.76.138',
    'port': 1433,
    'database': 'InHousePrint',
    'user': 'sa',
    'password': 'Jack2011'
}

# Connection retry configuration
MAX_RETRIES = 2
RETRY_DELAY = 1  # seconds


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_db_connection():
    """
    Get SQL Server connection to InHousePrint database
    Uses pymssql instead of pyodbc (no ODBC driver required)
    
    Implements retry logic for network issues
    
    FIXED: Proper exception handling, no cursor management needed here
    """
    import time
    
    for attempt in range(MAX_RETRIES):
        try:
            conn = pymssql.connect(
                server=DB_CONFIG['server'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                timeout=10,  # Reduced timeout for faster failure detection
                login_timeout=10
            )
            if attempt > 0:
                logger.info(f"Connected to InHousePrint database (attempt {attempt + 1})")
            else:
                logger.debug(f"Connected to InHousePrint database")
            return conn
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to connect to InHousePrint database after {MAX_RETRIES} attempts: {e}")
                raise


def calculate_ai_priority_score(job: Dict) -> int:
    """
    Calculate AI Priority Score (0-999)
    
    Algorithm mirrors kanban_board_system.py logic:
    - Days until due date: -50 to +300 points
    - Job value: 0 to 400 points
    - Customer tier: 0 to 200 points
    - Stage urgency: 0 to 99 points
    
    NO DATABASE OPERATIONS - Pure calculation function
    """
    score = 500  # Base score
    
    # Days until due (most critical factor)
    if job.get('DateRequired'):
        try:
            if isinstance(job['DateRequired'], str):
                due_date = datetime.fromisoformat(job['DateRequired'].replace('Z', '+00:00'))
            else:
                due_date = job['DateRequired']
            
            days_until = (due_date - datetime.now()).days
            
            if days_until < 0:
                score += 300  # Overdue
            elif days_until <= 1:
                score += 250  # Due today/tomorrow
            elif days_until <= 3:
                score += 200  # Due within 3 days
            elif days_until <= 7:
                score += 150  # Due this week
            else:
                score -= min(50, (days_until - 7) * 5)  # Future jobs
        except:
            pass
    
    # Job value
    value = job.get('Cost', 0) or 0
    if value >= 5000:
        score += 200
    elif value >= 2000:
        score += 150
    elif value >= 1000:
        score += 100
    elif value >= 500:
        score += 50
    
    # Customer tier (from ClientList OrderCount and TotalValue)
    order_count = job.get('CustomerOrderCount', 0) or 0
    total_value = job.get('CustomerTotalValue', 0) or 0
    
    if order_count >= 20 or total_value >= 50000:
        score += 100  # VIP
    elif order_count >= 10 or total_value >= 20000:
        score += 75   # Premium
    elif order_count >= 5:
        score += 50   # Regular
    
    # Stage urgency
    stage_id = job.get('StageID', 0) or 0
    if stage_id in [3, 4, 5]:  # Bindery, Guillotine, Dispatch
        score += 50
    
    return min(999, max(0, score))


def get_priority_label_color(score: int) -> Dict[str, str]:
    """Convert priority score to label and color - NO DATABASE"""
    if score >= 800:
        return {'label': 'CRITICAL', 'color': 'red', 'hex': '#ef4444'}
    elif score >= 600:
        return {'label': 'HIGH', 'color': 'orange', 'hex': '#f97316'}
    elif score >= 400:
        return {'label': 'URGENT', 'color': 'yellow', 'hex': '#eab308'}
    elif score >= 200:
        return {'label': 'NORMAL', 'color': 'green', 'hex': '#22c55e'}
    else:
        return {'label': 'LOW', 'color': 'blue', 'hex': '#3b82f6'}


def get_customer_tier(order_count: int, total_value: float) -> Dict[str, str]:
    """Determine customer tier badge - NO DATABASE"""
    order_count = order_count or 0
    total_value = total_value or 0
    
    if order_count >= 20 or total_value >= 50000:
        return {'tier': 'VIP', 'color': 'purple', 'hex': '#a855f7'}
    elif order_count >= 10 or total_value >= 20000:
        return {'tier': 'Premium', 'color': 'blue', 'hex': '#3b82f6'}
    elif order_count >= 5:
        return {'tier': 'Regular', 'color': 'green', 'hex': '#22c55e'}
    else:
        return {'tier': 'New', 'color': 'gray', 'hex': '#6b7280'}


def get_wip_status(days_in_system: int) -> Dict[str, str]:
    """Determine WIP status - NO DATABASE"""
    days_in_system = days_in_system or 0
    
    if days_in_system >= 14:
        return {'status': 'DELAYED', 'color': 'red', 'hex': '#ef4444'}
    elif days_in_system >= 7:
        return {'status': 'AT_RISK', 'color': 'orange', 'hex': '#f97316'}
    else:
        return {'status': 'ON_TRACK', 'color': 'green', 'hex': '#22c55e'}


# ============================================
# MAIN QUERY - ACTIVE JOBS
# ============================================

@inhouse_kanban_bp.route('/jobs', methods=['GET'])
def get_active_jobs():
    """
    Get active jobs for Kanban board
    
    Query params:
        - timeframe_months: Lookback period (default: -6)
        - priority_filter: Filter by priority (all/critical/high/urgent/normal/low)
        - stage_id: Filter by specific stage
        - limit: Max results (default: 100)
    
    FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize BEFORE try
    conn = None    # ✅ Initialize BEFORE try
    
    try:
        # Validate BEFORE creating resources
        timeframe_months = int(request.args.get('timeframe_months', -6))
        priority_filter = request.args.get('priority_filter', 'all').lower()
        stage_id = request.args.get('stage_id')
        limit = int(request.args.get('limit', 100))
        
        # Main query (mirrors kanban_board_system.py lines ~118-305)
        query = """
        SELECT TOP (%s)
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
            
            -- Job specifications (proper JOINs to lookup tables)
            ISNULL(pt.[Desc], '') as PaperType,
            ISNULL(gsm.[DESC], '') as GSM,
            ISNULL(ps.[Desc], '') as PaperSize,
            ISNULL(jt.Pages, 0) as Pages,
            ISNULL(jtype.[Desc], '') as JobType,
            ISNULL(bt.BindTypeDesc, '') as BindType,
            
            -- Finishing options (these exist in JobTickets)
            ISNULL(jt.FrontCelloMatt, 0) as FrontCelloMatt,
            ISNULL(jt.FrontCelloGloss, 0) as FrontCelloGloss,
            ISNULL(jt.BackCelloMatt, 0) as BackCelloMatt,
            ISNULL(jt.BackCelloGloss, 0) as BackCelloGloss,
            ISNULL(jt.FoldDesc, '') as FoldDesc,
            ISNULL(jt.StitchYes, 0) as StitchYes,
            ISNULL(jt.RingBind, 0) as RingBind,
            ISNULL(jt.PerfectBind, 0) as PerfectBind,
            ISNULL(jt.Books, 0) as Books,
            
            -- Calculate CelloYes based on actual cello columns
            CASE 
                WHEN (jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                      jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1) THEN 1
                ELSE 0
            END as CelloYes,
            
            -- Calculate FoldYes based on FoldDesc
            CASE 
                WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' THEN 1
                ELSE 0
            END as FoldYes,
            
            -- Production notes
            ISNULL(jt.TicketNotes, '') as ProductionNotes,
            ISNULL(o.ClientOrderNum, '') as ClientOrderNum,
            
            -- Shipping information
            ISNULL(st.ShippingDesc, 'N/A') as ShippingDesc,
            
            -- Business division
            ISNULL(o.InvoicingBusinessID, 0) as InvoicingBusinessID,
            ISNULL(b.[BusinessName], '') as InvoicingBusiness,
            
            -- Priority calculations
            CASE 
                WHEN o.DateRequired < GETDATE() THEN 'Overdue'
                WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'Urgent'
                WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'Normal'
                ELSE 'Low Priority'
            END as Priority,
            
            DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
            DATEDIFF(day, o.OrderDate, GETDATE()) as DaysInSystem,
            
            -- Urgency level
            CASE
                WHEN o.DateRequired < GETDATE() THEN 'OVERDUE'
                WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'CRITICAL'
                WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'HIGH'
                WHEN o.DateRequired <= DATEADD(day, 7, GETDATE()) THEN 'MEDIUM'
                ELSE 'LOW'
            END as UrgencyLevel,
            
            -- Customer metrics
            (
                SELECT COUNT(*) 
                FROM Orders o2 
                WHERE o2.ClientName = o.ClientName 
                AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
            ) as CustomerOrderCount,
            
            (
                SELECT SUM(CAST(jt2.Cost as DECIMAL(10,2))) 
                FROM JobTickets jt2 
                INNER JOIN Orders o2 ON jt2.OrderID = o2.OrderID
                WHERE o2.ClientName = o.ClientName 
                AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
            ) as CustomerLifetimeValue,
            
            -- AI Priority Score (0-999)
            (
                CASE 
                    WHEN o.DateRequired < GETDATE() THEN 400
                    WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 350
                    WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 250
                    WHEN o.DateRequired <= DATEADD(day, 7, GETDATE()) THEN 150
                    ELSE 50
                END
                +
                CASE 
                    WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 5000 THEN 300
                    WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 2000 THEN 200
                    WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 1000 THEN 150
                    WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 500 THEN 100
                    ELSE 50
                END
                +
                CASE 
                    WHEN (
                        SELECT COUNT(*) FROM Orders o2 
                        WHERE o2.ClientName = o.ClientName 
                        AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
                    ) >= 50 THEN 200
                    WHEN (
                        SELECT COUNT(*) FROM Orders o2 
                        WHERE o2.ClientName = o.ClientName 
                        AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
                    ) >= 20 THEN 150
                    WHEN (
                        SELECT COUNT(*) FROM Orders o2 
                        WHERE o2.ClientName = o.ClientName 
                        AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
                    ) >= 5 THEN 75
                    ELSE 25
                END
                +
                CASE 
                    WHEN DATEDIFF(day, o.OrderDate, GETDATE()) > 30 THEN 99
                    WHEN DATEDIFF(day, o.OrderDate, GETDATE()) > 14 THEN 50
                    WHEN DATEDIFF(day, o.OrderDate, GETDATE()) > 7 THEN 25
                    ELSE 0
                END
            ) as AIPriorityScore
            
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobStage js ON jt.StageID = js.StageID
        
        -- Lookup table JOINs (corrected)
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
        LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
        LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
        LEFT JOIN Business b ON o.InvoicingBusinessID = b.BusinessID
        
        WHERE jt.InternalInvoiceComplete = 0
            AND jt.StageID != 10
            AND o.OrderDate >= DATEADD(month, %s, GETDATE())
        """
        
        # Add stage filter if specified
        if stage_id:
            query += " AND jt.StageID = %s"
        
        query += " ORDER BY AIPriorityScore DESC, o.DateRequired ASC"
        
        # Execute query
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = [limit, timeframe_months]
        if stage_id:
            params.append(int(stage_id))
        
        cursor.execute(query, params)
        
        # Fetch results
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE processing results (return connection to pool)
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Process results AFTER closing connection
        jobs = []
        for row in rows:
            job_dict = {}
            for idx, col in enumerate(columns):
                value = row[idx]
                # Convert datetime to ISO string
                if isinstance(value, datetime):
                    value = value.isoformat()
                # Convert decimal/numeric types to float for JSON serialization
                elif hasattr(value, '__float__'):
                    value = float(value)
                job_dict[col] = value
            
            # Calculate AI Priority Score (pure Python, no DB)
            job_dict['AIPriorityScore'] = calculate_ai_priority_score(job_dict)
            
            # Add priority label and color
            priority_info = get_priority_label_color(job_dict['AIPriorityScore'])
            job_dict['PriorityLabel'] = priority_info['label']
            job_dict['PriorityColor'] = priority_info['color']
            job_dict['PriorityColorHex'] = priority_info['hex']
            
            # Add customer tier
            tier_info = get_customer_tier(
                job_dict.get('CustomerOrderCount', 0),
                job_dict.get('CustomerTotalValue', 0)
            )
            job_dict['CustomerTier'] = tier_info['tier']
            job_dict['CustomerTierColor'] = tier_info['color']
            job_dict['CustomerTierColorHex'] = tier_info['hex']
            
            # Add WIP status
            wip_info = get_wip_status(job_dict.get('DaysInSystem', 0))
            job_dict['WIPStatus'] = wip_info['status']
            job_dict['WIPColor'] = wip_info['color']
            job_dict['WIPColorHex'] = wip_info['hex']
            
            jobs.append(job_dict)
        
        # Apply priority filter if specified
        if priority_filter != 'all':
            jobs = [j for j in jobs if j['PriorityLabel'].lower() == priority_filter]
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs),
            'timeframe_months': timeframe_months
        })
        
    except Exception as e:
        logger.error(f"Failed to get active jobs: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:  # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# STAGE SUMMARY
# ============================================

@inhouse_kanban_bp.route('/stages', methods=['GET'])
def get_stage_summary():
    """
    Get summary of jobs by stage
    
    Query params:
        - timeframe_months: Lookback period (default: -6)
    
    FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize BEFORE try
    conn = None    # ✅ Initialize BEFORE try
    
    try:
        timeframe_months = int(request.args.get('timeframe_months', -6))
        
        query = """
        SELECT 
            js.StageID,
            js.[Desc] as StageDescription,
            COUNT(jt.TicketID) as JobCount,
            ISNULL(SUM(jt.Cost), 0) as TotalValue,
            ISNULL(AVG(DATEDIFF(day, o.OrderDate, GETDATE())), 0) as AvgDaysInStage
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobStage js ON jt.StageID = js.StageID
        WHERE jt.InternalInvoiceComplete = 0
            AND jt.StageID != 10
            AND o.OrderDate >= DATEADD(month, %s, GETDATE())
        GROUP BY js.StageID, js.[Desc]
        ORDER BY js.StageID
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, [timeframe_months])
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE processing results
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Process results AFTER closing connection
        stages = []
        for row in rows:
            stage_dict = {}
            for idx, col in enumerate(columns):
                value = row[idx]
                if isinstance(value, datetime):
                    value = value.isoformat()
                # Convert decimal/numeric types to float for JSON serialization
                elif hasattr(value, '__float__'):
                    value = float(value)
                stage_dict[col] = value
            stages.append(stage_dict)
        
        return jsonify({
            'success': True,
            'stages': stages,
            'count': len(stages)
        })
        
    except Exception as e:
        logger.error(f"Failed to get stage summary: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:  # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# DASHBOARD METRICS
# ============================================

@inhouse_kanban_bp.route('/metrics', methods=['GET'])
def get_dashboard_metrics():
    """
    Get top-level dashboard metrics
    
    Returns:
        - Total active jobs
        - Pipeline value
        - Overdue jobs count
        - Average days in system
    
    FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize BEFORE try
    conn = None    # ✅ Initialize BEFORE try
    
    try:
        timeframe_months = int(request.args.get('timeframe_months', -6))
        
        query = """
        SELECT 
            COUNT(jt.TicketID) as TotalJobs,
            ISNULL(SUM(jt.Cost), 0) as PipelineValue,
            SUM(CASE WHEN o.DateRequired < GETDATE() THEN 1 ELSE 0 END) as OverdueJobs,
            ISNULL(AVG(DATEDIFF(day, o.OrderDate, GETDATE())), 0) as AvgDaysInSystem
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.InternalInvoiceComplete = 0
            AND jt.StageID != 10
            AND o.OrderDate >= DATEADD(month, %s, GETDATE())
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, [timeframe_months])
        
        row = cursor.fetchone()
        
        # ✅ Close cursor BEFORE processing results
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Process result AFTER closing connection
        metrics = {
            'total_jobs': row[0] or 0,
            'pipeline_value': float(row[1] or 0),
            'overdue_jobs': row[2] or 0,
            'avg_days_in_system': round(float(row[3] or 0), 1)
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:  # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# JOB DETAILS
# ============================================

@inhouse_kanban_bp.route('/jobs/<int:ticket_id>', methods=['GET'])
def get_job_details(ticket_id):
    """
    Get detailed information for a specific job
    
    FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize BEFORE try
    conn = None    # ✅ Initialize BEFORE try
    
    try:
        query = """
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
            
            ISNULL(pt.[Desc], '') as PaperType,
            ISNULL(gsm.[DESC], '') as GSM,
            ISNULL(ps.[Desc], '') as PaperSize,
            ISNULL(jt.Pages, 0) as Pages,
            ISNULL(jtype.[Desc], '') as JobType,
            ISNULL(bt.BindTypeDesc, '') as BindType,
            
            ISNULL(jt.FrontCelloMatt, 0) as FrontCelloMatt,
            ISNULL(jt.FrontCelloGloss, 0) as FrontCelloGloss,
            ISNULL(jt.BackCelloMatt, 0) as BackCelloMatt,
            ISNULL(jt.BackCelloGloss, 0) as BackCelloGloss,
            ISNULL(jt.FoldDesc, '') as FoldDesc,
            ISNULL(jt.StitchYes, 0) as StitchYes,
            ISNULL(jt.RingBind, 0) as RingBind,
            ISNULL(jt.PerfectBind, 0) as PerfectBind,
            ISNULL(jt.Books, 0) as Books,
            
            ISNULL(jt.TicketNotes, '') as ProductionNotes,
            ISNULL(o.ClientOrderNum, '') as ClientOrderNum,
            ISNULL(st.ShippingDesc, 'N/A') as ShippingDesc,
            
            ISNULL(o.InvoicingBusinessID, 0) as InvoicingBusinessID,
            ISNULL(b.[BusinessName], '') as InvoicingBusiness,
            
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
            
            (
                SELECT COUNT(*) 
                FROM Orders o2 
                WHERE o2.ClientName = o.ClientName 
                AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
            ) as CustomerOrderCount,
            
            (
                SELECT SUM(CAST(jt2.Cost as DECIMAL(10,2))) 
                FROM JobTickets jt2 
                INNER JOIN Orders o2 ON jt2.OrderID = o2.OrderID
                WHERE o2.ClientName = o.ClientName 
                AND o2.OrderDate >= DATEADD(month, -12, GETDATE())
            ) as CustomerLifetimeValue
            
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
        
        WHERE jt.TicketID = %s
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, [ticket_id])
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        
        # ✅ Close cursor BEFORE checking result
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Check result AFTER closing connection
        if not row:
            return jsonify({'error': 'Job not found'}), 404
        
        # Process result
        job = {}
        for idx, col in enumerate(columns):
            value = row[idx]
            if isinstance(value, datetime):
                value = value.isoformat()
            # Convert decimal/numeric types to float for JSON serialization
            elif hasattr(value, '__float__'):
                value = float(value)
            job[col] = value
        
        # Add calculated fields (no database operations)
        job['AIPriorityScore'] = calculate_ai_priority_score(job)
        priority_info = get_priority_label_color(job['AIPriorityScore'])
        job.update(priority_info)
        
        tier_info = get_customer_tier(
            job.get('CustomerOrderCount', 0),
            job.get('CustomerLifetimeValue', 0)
        )
        job.update(tier_info)
        
        wip_info = get_wip_status(job.get('DaysInSystem', 0))
        job.update(wip_info)
        
        # FIELD MAPPING: Map database fields to frontend expectations
        # Combine paper fields
        paper_parts = []
        if job.get('PaperType'): paper_parts.append(job['PaperType'])
        if job.get('GSM'): paper_parts.append(job['GSM'])
        job['Paper'] = ' '.join(paper_parts) if paper_parts else None
        
        # Map field names for frontend
        job['JobSize'] = job.get('PaperSize', '')
        job['Binding'] = job.get('BindType', '')
        job['Folding'] = job.get('FoldDesc', '')
        job['TicketNotes'] = job.get('ProductionNotes', '')
        job['Shipping'] = job.get('ShippingDesc', '')
        
        # Combine cello options into single field
        cello_parts = []
        if job.get('FrontCelloMatt'): cello_parts.append('Front Matt')
        if job.get('FrontCelloGloss'): cello_parts.append('Front Gloss')
        if job.get('BackCelloMatt'): cello_parts.append('Back Matt')
        if job.get('BackCelloGloss'): cello_parts.append('Back Gloss')
        job['Cello'] = ', '.join(cello_parts) if cello_parts else None
        
        # Stitching boolean to text
        job['Stitching'] = 'Yes' if job.get('StitchYes') else None
        
        return jsonify({
            'success': True,
            'job': job
        })
        
    except Exception as e:
        logger.error(f"Failed to get job details: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:  # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ============================================
# HEALTH CHECK
# ============================================

@inhouse_kanban_bp.route('/health', methods=['GET'])
def health():
    """
    Health check for InHousePrint Kanban routes
    
    FIXED: Proper cursor/connection management with finally block
    """
    cursor = None  # ✅ Initialize BEFORE try
    conn = None    # ✅ Initialize BEFORE try
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM JobTickets WHERE InternalInvoiceComplete = 0')
        active_jobs = cursor.fetchone()[0]
        
        # ✅ Close cursor BEFORE return
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'active_jobs': active_jobs,
            'server': DB_CONFIG['server'],
            'database_name': DB_CONFIG['database']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
    
    finally:  # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass