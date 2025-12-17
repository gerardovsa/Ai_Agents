"""
Business Intelligence Query Library for InHouse Print

This module provides pre-built, optimized SQL queries that the AI agent can request
via tool calls, similar to how the calculator tools work. Each query is designed
for common business intelligence tasks with proper parameter handling.

Architecture:
- Each query is a method that returns SQL string + metadata
- AI requests query by name and provides parameters
- System validates parameters and returns ready-to-execute SQL
- Results can be visualized with Plotly charts

Usage in tool_use_agent.py:
    from core.query_library import QueryLibrary
    
    query_lib = QueryLibrary(db_connection)
    result = query_lib.get_query("sales_trend_by_month", months=6)
    df = db.execute_query(result['sql'])
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import pandas as pd
import numpy as np


class QueryLibrary:
    """
    Pre-built query library for business intelligence
    Provides optimized, parameterized queries with metadata
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize query library
        
        Args:
            db_connection: Optional database connection for validation
        """
        self.db = db_connection
        self.query_catalog = self._build_query_catalog()
    
    def _build_query_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Build catalog of all available queries with metadata
        This is used by the AI to discover available queries
        """
        return {
            # ============================================
            # SALES & REVENUE ANALYSIS
            # ============================================
            "sales_trend_by_month": {
                "category": "Sales & Revenue",
                "description": "Monthly sales trends showing revenue, order count, and average order value over time",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 6)",
                        "default": 6,
                        "min": 1,
                        "max": 36
                    }
                },
                "returns": "Month, TotalRevenue, OrderCount, AvgOrderValue",
                "visualization": "line_chart",
                "best_for": "Identifying sales trends, seasonality, growth patterns"
            },
            
            "monthly_revenue_trend": {
                "category": "Sales & Revenue",
                "description": "Monthly revenue trend with order counts and average values",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to show (default: 24)",
                        "default": 24,
                        "min": 3,
                        "max": 36
                    }
                },
                "returns": "YearMonth, TotalRevenue, OrderCount, JobTicketCount, AvgJobValue, UnitsProduced",
                "visualization": "line_chart_dual_axis",
                "best_for": "Business performance tracking, seasonality analysis",
                "validated": True
            },
            
            "revenue_by_product_type": {
                "category": "Sales & Revenue",
                "description": "Revenue breakdown by product type (business cards, flyers, books, etc.)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12,
                        "min": 1,
                        "max": 36
                    },
                    "min_revenue": {
                        "type": "float",
                        "description": "Minimum revenue to include (default: 0)",
                        "default": 0
                    }
                },
                "returns": "ProductType, TotalRevenue, OrderCount, AvgPrice",
                "visualization": "bar_chart",
                "best_for": "Product performance analysis, identifying top products"
            },
            
            "revenue_by_customer": {
                "category": "Sales & Revenue",
                "description": "Top customers by revenue with order count and average order value",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top customers to return (default: 20)",
                        "default": 20,
                        "min": 5,
                        "max": 100
                    }
                },
                "returns": "CustomerName, TotalRevenue, OrderCount, AvgOrderValue, LastOrderDate",
                "visualization": "bar_chart",
                "best_for": "Customer profitability, account management, retention focus"
            },
            
            # ============================================
            # CUSTOMER ANALYTICS
            # ============================================
            "customer_retention_cohort": {
                "category": "Customer Analytics",
                "description": "Customer cohort analysis showing retention rates by first order month",
                "parameters": {
                    "cohort_months": {
                        "type": "integer",
                        "description": "Number of cohort months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "CohortMonth, CustomersCount, RetentionRate, ReturningCustomers",
                "visualization": "heatmap",
                "best_for": "Understanding customer loyalty, retention patterns"
            },
            
            "top_customers_detailed": {
                "category": "Customer Analytics",
                "description": "Top customers with full order history and product preferences",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 12)",
                        "default": 12
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of customers (default: 20)",
                        "default": 20,
                        "min": 5,
                        "max": 100
                    }
                },
                "returns": "ClientName, TotalRevenue, OrderCount, JobTicketCount, AvgJobValue, LastOrderDate, DaysSinceLastOrder, TopProduct",
                "visualization": "table_with_sparkline",
                "best_for": "Account management, customer relationship planning",
                "validated": True
            },
            
            "customer_order_frequency": {
                "category": "Customer Analytics",
                "description": "Customer segmentation by order frequency (one-time, occasional, regular, frequent)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Period to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "Segment, CustomerCount, TotalRevenue, AvgOrdersPerCustomer",
                "visualization": "pie_chart",
                "best_for": "Customer segmentation, marketing strategy"
            },
            
            "customer_product_preferences": {
                "category": "Customer Analytics",
                "description": "What products each customer orders most frequently",
                "parameters": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer name (use % for wildcard)",
                        "default": None
                    },
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "ClientName, ProductType, OrderCount, TotalQuantity, TotalRevenue, AvgPrice, LastOrderDate",
                "visualization": "grouped_bar",
                "best_for": "Personalized quoting, cross-sell recommendations",
                "validated": True
            },
            
            "customer_lifetime_value": {
                "category": "Customer Analytics",
                "description": "Customer lifetime value analysis with total spend and order history",
                "parameters": {
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum orders to include (default: 2)",
                        "default": 2
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top customers to return (default: 50)",
                        "default": 50
                    }
                },
                "returns": "CustomerName, LifetimeValue, OrderCount, FirstOrder, LastOrder, DaysSinceLastOrder",
                "visualization": "scatter_plot",
                "best_for": "High-value customer identification, account prioritization"
            },
            
            # ============================================
            # PRODUCT ANALYSIS
            # ============================================
            "product_performance_detail": {
                "category": "Product Analysis",
                "description": "Detailed product analysis with specifications, volumes, and pricing",
                "parameters": {
                    "product_type": {
                        "type": "string",
                        "description": "Product type to analyze (e.g., 'business cards', 'flyers')",
                        "default": None
                    },
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 6)",
                        "default": 6
                    }
                },
                "returns": "Product, Specification, OrderCount, TotalQuantity, AvgPrice, TotalRevenue",
                "visualization": "table_with_bar",
                "best_for": "Product portfolio optimization, pricing strategy"
            },
            
            "product_turnaround_benchmarks": {
                "category": "Product Analysis",
                "description": "Average production time by product type (OrderDate to InvoiceDate)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 6)",
                        "default": 6
                    }
                },
                "returns": "ProductType, AvgDays, MinDays, MaxDays, JobCount, ComplexityScore",
                "visualization": "horizontal_bar",
                "best_for": "Setting realistic delivery dates, quote accuracy",
                "validated": True
            },

            "high_value_jobs_list": {
                "category": "Product Analysis",
                "description": "List of high-value individual jobs (detailed specifications)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 12)",
                        "default": 12
                    },
                    "min_value": {
                        "type": "float",
                        "description": "Minimum job value (default: 5000)",
                        "default": 5000
                    }
                },
                "returns": "ClientName, JobDescription, JobValue, Quantity, OrderDate, ProductionNotes",
                "visualization": "table",
                "best_for": "Understanding premium job requirements, specialty pricing",
                "validated": True
            },

            "binding_finishing_analysis": {
                "category": "Product Analysis",
                "description": "Analysis of binding types and finishing options with pricing impact",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "BindType, JobCount, TotalRevenue, AvgJobValue, AvgPages",
                "visualization": "pie_chart",
                "best_for": "Finishing option recommendations, pricing strategy",
                "validated": True
            },
            
            "paper_stock_usage": {
                "category": "Product Analysis",
                "description": "Analysis of paper stock usage by type and GSM",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 12)",
                        "default": 12
                    }
                },
                "returns": "PaperType, GSM, OrderCount, TotalQuantity, AvgQuantityPerOrder",
                "visualization": "stacked_bar",
                "best_for": "Inventory planning, supplier negotiations"
            },
            
            "finishing_options_popularity": {
                "category": "Product Analysis",
                "description": "Analysis of finishing options (cellophane, binding, folding) popularity",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 12)",
                        "default": 12
                    }
                },
                "returns": "FinishingType, OrderCount, Percentage, AvgPrice",
                "visualization": "horizontal_bar",
                "best_for": "Service offering optimization, pricing finishing options"
            },
            
            # ============================================
            # OPERATIONAL METRICS
            # ============================================
            "production_turnaround_time": {
                "category": "Operational Metrics",
                "description": "Analysis of production turnaround times by urgency and product type",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 3)",
                        "default": 3
                    }
                },
                "returns": "UrgencyLevel, ProductType, AvgTurnaroundDays, OrderCount",
                "visualization": "grouped_bar",
                "best_for": "Production efficiency, capacity planning"
            },
            
            # ============================================
            # OPERATIONAL FLOW & PRODUCTION (VALIDATED)
            # ============================================
            "current_production_status": {
                "category": "Operational Flow",
                "description": "Real-time production status showing active jobs by stage with WIP counts",
                "parameters": {
                    "days_back": {
                        "type": "integer",
                        "description": "Days to look back for active jobs (default: 30)",
                        "default": 30,
                        "min": 1,
                        "max": 90
                    }
                },
                "returns": "StageName, JobCount, TotalValue, AvgDaysInStage, OldestJobDate",
                "visualization": "bar_chart",
                "best_for": "Real-time production monitoring, bottleneck detection",
                "validated": True
            },

            "overdue_jobs_alert": {
                "category": "Operational Flow",
                "description": "Critical alert list of overdue jobs past their DateRequired",
                "parameters": {
                    "include_completed": {
                        "type": "boolean",
                        "description": "Include completed stages (default: False)",
                        "default": False
                    }
                },
                "returns": "ClientName, JobDescription, DaysOverdue, CurrentStage, JobValue, DateRequired",
                "visualization": "table_alert",
                "best_for": "Daily production meetings, crisis management",
                "validated": True
            },

            "priority_work_queue": {
                "category": "Operational Flow",
                "description": "AI-calculated priority queue for production scheduling",
                "parameters": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Days ahead to forecast (default: 3)",
                        "default": 3,
                        "min": 1,
                        "max": 14
                    }
                },
                "returns": "TicketID, ClientName, JobDescription, PriorityScore, DueDate, CurrentStage, Urgency",
                "visualization": "sorted_table",
                "best_for": "Morning production kickoff, operator assignment",
                "validated": True
            },

            "bottleneck_detection": {
                "category": "Operational Flow",
                "description": "Identifies production bottlenecks with WIP limit violations",
                "parameters": {
                    "wip_threshold": {
                        "type": "integer",
                        "description": "WIP count to flag as bottleneck (default: 5)",
                        "default": 5,
                        "min": 3,
                        "max": 20
                    }
                },
                "returns": "StageName, CurrentWIP, RecommendedLimit, OverCapacity, AvgTimeInStage, Status",
                "visualization": "gauge_chart",
                "best_for": "Capacity planning, workflow optimization",
                "validated": True
            },

            "daily_capacity_forecast": {
                "category": "Operational Flow",
                "description": "7-day capacity forecast showing jobs due vs historical capacity",
                "parameters": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Days to forecast (default: 7)",
                        "default": 7,
                        "min": 1,
                        "max": 30
                    }
                },
                "returns": "DueDate, DayOfWeek, JobsDue, DigitalJobs, SignageJobs, BinderyJobs, CapacityStatus",
                "visualization": "stacked_bar",
                "best_for": "Weekly planning, intake management",
                "validated": True
            },

            "production_stage_flow": {
                "category": "Operational Flow",
                "description": "Job flow through production stages (last 30 days movement)",
                "parameters": {
                    "days": {
                        "type": "integer",
                        "description": "Days to analyze (default: 30)",
                        "default": 30
                    }
                },
                "returns": "FromStage, ToStage, JobCount, AvgDaysToMove, BottleneckFlag",
                "visualization": "sankey_diagram",
                "best_for": "Process flow analysis, identifying handoff delays",
                "validated": True
            },

            "urgency_level_distribution": {
                "category": "Operational Flow",
                "description": "Distribution of jobs by production urgency (Before Lunch, COB, 48hr, etc.)",
                "parameters": {
                    "days": {
                        "type": "integer",
                        "description": "Days to analyze (default: 30)",
                        "default": 30
                    }
                },
                "returns": "UrgencyLevel, Priority, JobCount, TotalValue, AvgJobValue, PercentOfJobs",
                "visualization": "horizontal_bar",
                "best_for": "Understanding turnaround pressure, capacity stress",
                "validated": True
            },

            "job_complexity_analysis": {
                "category": "Operational Flow",
                "description": "Job complexity scoring for production time estimation",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 6)",
                        "default": 6
                    }
                },
                "returns": "ProductType, AvgJobValue, AvgQuantity, ComplexityScore, AvgTurnaroundDays",
                "visualization": "scatter_plot",
                "best_for": "AI scheduling, production time estimation",
                "validated": True
            },
            
            # ============================================
            # PRODUCTION PLANNING (NEW - COMPREHENSIVE)
            # ============================================
            "daily_production_plan": {
                "category": "Production Planning",
                "description": "Daily production planning report for digital workflow - prioritizes jobs by due date, urgency, and stage. Calculates production time estimates and identifies bottlenecks.",
                "parameters": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to plan (1=today+tomorrow, 2=today+tomorrow+day after)",
                        "default": 2,
                        "min": 1,
                        "max": 7
                    },
                    "min_ticket_id": {
                        "type": "integer",
                        "description": "Minimum ticket ID to include (use recent tickets instead of InternalInvoiceComplete for performance)",
                        "default": 72680
                    },
                    "stages": {
                        "type": "string",
                        "description": "Comma-separated stage IDs to include (4=9110, 5=Other Digital, 6=OutSource, 7=Cello, 8=Bindery, 11=Ready)",
                        "default": "4,5,6,7,8,11"
                    }
                },
                "returns": "TicketID, OrderID, ClientName, QTY, JobType, ShortJobDesc, StageID, StageDescription, Cost, DaysUntilDue, DueDate, UrgencyLevel, UrgencyColor, UrgencyDescription, ShippingDesc, ProductionNotes, EstimatedHours, PriorityScore, PriorityBand, CustomerTier, OrderDate, DaysInSystem",
                "visualization": "kanban_board",
                "best_for": "Daily production kickoff, task prioritization, operator assignment",
                "validated": True
            },
            
            "stage_capacity_report": {
                "category": "Production Planning",
                "description": "Calculate available capacity for each production stage - shows hours needed vs hours available, identifies overloaded stages",
                "parameters": {
                    "min_ticket_id": {
                        "type": "integer",
                        "description": "Minimum ticket ID for recent jobs",
                        "default": 72680
                    },
                    "work_hours_per_day": {
                        "type": "integer",
                        "description": "Available work hours per day per stage",
                        "default": 8,
                        "min": 4,
                        "max": 16
                    },
                    "stages": {
                        "type": "string",
                        "description": "Comma-separated stage IDs to analyze",
                        "default": "4,5,6,7,8,11"
                    }
                },
                "returns": "StageID, StageDescription, JobCount, TotalHoursNeeded, HoursAvailableToday, CapacityUtilization, Status, JobsOverdue, JobsDueToday, JobsDueTomorrow, AvgHoursPerJob, HighestPriorityJob",
                "visualization": "gauge_chart",
                "best_for": "Capacity planning, identifying overloaded stages, resource allocation",
                "validated": True
            },
            
            "weekly_production_forecast": {
                "category": "Production Planning",
                "description": "7-day production forecast showing daily workload, due dates, and resource requirements",
                "parameters": {
                    "min_ticket_id": {
                        "type": "integer",
                        "description": "Minimum ticket ID for recent jobs",
                        "default": 72680
                    },
                    "stages": {
                        "type": "string",
                        "description": "Comma-separated stage IDs to forecast",
                        "default": "4,5,6,7,8,11"
                    }
                },
                "returns": "DueDate, DayOfWeek, DaysFromToday, JobCount, TotalHoursNeeded, TotalValue, OverdueCount, Stage4Hours, Stage5Hours, Stage7Hours, Stage8Hours, CriticalJobs, HighValueJobs, TopClient",
                "visualization": "stacked_bar",
                "best_for": "Weekly planning, workload distribution, intake management",
                "validated": True
            },
            
            "bottleneck_detection_advanced": {
                "category": "Production Planning",
                "description": "Identifies production bottlenecks - stages with overload, delays, or resource constraints. Provides actionable recommendations.",
                "parameters": {
                    "min_ticket_id": {
                        "type": "integer",
                        "description": "Minimum ticket ID for recent jobs",
                        "default": 72680
                    },
                    "capacity_threshold": {
                        "type": "float",
                        "description": "Capacity utilization % to flag as bottleneck (0.85 = 85%)",
                        "default": 0.85,
                        "min": 0.5,
                        "max": 1.0
                    },
                    "stages": {
                        "type": "string",
                        "description": "Comma-separated stage IDs to analyze",
                        "default": "4,5,6,7,8,11"
                    }
                },
                "returns": "StageID, StageDescription, IsBottleneck, BottleneckScore, JobCount, HoursNeeded, HoursAvailable, Utilization, AvgDaysInStage, OverdueJobs, DelayRisk, RecommendedAction",
                "visualization": "horizontal_bar",
                "best_for": "Bottleneck identification, process optimization, crisis management",
                "validated": True
            },
            
            "order_size_distribution": {
                "category": "Operational Metrics",
                "description": "Distribution of orders by size ranges (quantity)",
                "parameters": {
                    "product_type": {
                        "type": "string",
                        "description": "Optional product type filter",
                        "default": None
                    },
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 12)",
                        "default": 12
                    }
                },
                "returns": "QuantityRange, OrderCount, TotalRevenue, AvgPrice",
                "visualization": "histogram",
                "best_for": "Understanding order patterns, pricing tiers"
            },
            
            "day_of_week_patterns": {
                "category": "Operational Metrics",
                "description": "Order intake patterns by day of week (last 6 months)",
                "parameters": {
                    "weeks": {
                        "type": "integer",
                        "description": "Weeks to analyze (default: 26)",
                        "default": 26
                    }
                },
                "returns": "DayOfWeek, DayNumber, AvgOrders, AvgJobTickets, AvgRevenue, FlyerCount, BookCount, SignageCount",
                "visualization": "grouped_bar",
                "best_for": "Staffing optimization, capacity planning",
                "validated": True
            },
            
            "daily_order_volume": {
                "category": "Operational Metrics",
                "description": "Daily order volume with day-of-week patterns",
                "parameters": {
                    "weeks": {
                        "type": "integer",
                        "description": "Number of weeks to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "DayOfWeek, AvgOrders, TotalOrders, PeakOrders",
                "visualization": "line_chart",
                "best_for": "Staffing optimization, workload planning"
            },
            
            "quarterly_performance": {
                "category": "Sales & Revenue",
                "description": "Quarterly revenue comparison with growth rates",
                "parameters": {
                    "quarters": {
                        "type": "integer",
                        "description": "Number of quarters (default: 8)",
                        "default": 8,
                        "min": 4,
                        "max": 12
                    }
                },
                "returns": "Quarter, Year, TotalRevenue, OrderCount, AvgOrderValue, GrowthRate",
                "visualization": "bar_chart_with_line",
                "best_for": "Executive reporting, trend analysis",
                "validated": True
            },
            
            # ============================================
            # FINANCIAL ANALYSIS
            # ============================================
            "profit_margin_by_product": {
                "category": "Financial Analysis",
                "description": "Estimated profit margins by product type (requires cost data)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 6)",
                        "default": 6
                    }
                },
                "returns": "ProductType, Revenue, EstimatedCost, EstimatedProfit, MarginPercentage",
                "visualization": "waterfall_chart",
                "best_for": "Profitability analysis, pricing strategy"
            },
            
            "quote_conversion_rate": {
                "category": "Financial Analysis",
                "description": "Quote-to-order conversion rates by product and customer",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 6)",
                        "default": 6
                    }
                },
                "returns": "Period, QuotesGiven, OrdersReceived, ConversionRate, LostRevenue",
                "visualization": "funnel_chart",
                "best_for": "Sales effectiveness, pricing competitiveness"
            },
            
            # ============================================
            # BUSINESS DIVISION ANALYSIS
            # ============================================
            "apg_workflow_status": {
                "category": "Business Divisions",
                "description": "APG (American Printing Group) workflow status by stage",
                "parameters": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default: 30)",
                        "default": 30
                    }
                },
                "returns": "WorkflowStage, JobCount, AvgTimeInStage, OldestJob",
                "visualization": "funnel_chart",
                "best_for": "APG production monitoring, bottleneck identification"
            },
            
            "publishing_projects_pipeline": {
                "category": "Business Divisions",
                "description": "Freeda Publishing projects pipeline and status",
                "parameters": {
                    "status_filter": {
                        "type": "string",
                        "description": "Filter by status (e.g., 'Active', 'Complete')",
                        "default": None
                    }
                },
                "returns": "ProjectName, Status, StartDate, EstimatedCompletion, DaysInProgress",
                "visualization": "gantt_chart",
                "best_for": "Publishing project management, timeline tracking"
            },
            
            "perfect_bound_books_analysis": {
                "category": "Business Divisions",
                "description": "Perfect Bound Books division analysis with costing details",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 6)",
                        "default": 6
                    }
                },
                "returns": "PageRange, OrderCount, AvgCostPerBook, TotalRevenue",
                "visualization": "scatter_plot",
                "best_for": "Book printing optimization, cost analysis"
            },
            
            # ============================================
            # COMPARATIVE ANALYSIS
            # ============================================
            "year_over_year_comparison": {
                "category": "Comparative Analysis",
                "description": "Year-over-year comparison of key metrics",
                "parameters": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to compare ('revenue', 'orders', 'customers')",
                        "default": "revenue"
                    }
                },
                "returns": "Month, CurrentYear, PreviousYear, PercentageChange, Difference",
                "visualization": "line_chart_dual",
                "best_for": "Growth analysis, performance benchmarking"
            },
            
            "product_cross_sell_analysis": {
                "category": "Comparative Analysis",
                "description": "Products frequently ordered together by same customer",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months (default: 12)",
                        "default": 12
                    },
                    "min_occurrences": {
                        "type": "integer",
                        "description": "Minimum co-occurrences (default: 3)",
                        "default": 3
                    }
                },
                "returns": "Product1, Product2, CoOccurrences, CrossSellRate",
                "visualization": "network_graph",
                "best_for": "Cross-selling opportunities, bundling strategy"
            },
            
            # ============================================
            # PERFORMANCE & SLA TRACKING (NEW)
            # ============================================
            "on_time_delivery_rate": {
                "category": "Performance & SLA",
                "description": "Monthly on-time delivery performance tracking (InvoiceDate vs DateRequired)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12,
                        "min": 1,
                        "max": 36
                    }
                },
                "returns": "Month, TotalOrders, OnTimeOrders, OnTimePercentage, AvgDaysLateOrEarly",
                "visualization": "line_chart",
                "best_for": "SLA monitoring, service quality tracking, customer satisfaction",
                "validated": True
            },
            
            "customer_deadline_realism": {
                "category": "Performance & SLA",
                "description": "Customer deadline analysis showing who sets realistic vs unrealistic lead times",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum orders to include customer (default: 5)",
                        "default": 5
                    }
                },
                "returns": "ClientName, TotalOrders, AvgLeadTimeDays, OnTimeRate, DeadlineRealism",
                "visualization": "scatter_plot",
                "best_for": "Customer education, expectation management, pricing rush jobs",
                "validated": True
            },
            
            # ============================================
            # UPSELL & REVENUE OPTIMIZATION (NEW)
            # ============================================
            "finishing_upsell_analysis": {
                "category": "Upsell & Revenue",
                "description": "Finishing options adoption rates and price impact by product type",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "ProductType, TotalJobs, CelloAdoptionRate, AvgPriceWithCello, AvgPriceNoCello, CelloValueAdd",
                "visualization": "horizontal_bar",
                "best_for": "Upsell training, pricing strategy, revenue optimization",
                "validated": True
            },
            
            "boolean_flags_summary": {
                "category": "Upsell & Revenue",
                "description": "Comprehensive summary of all finishing option flags (cello, fold, stitch, etc.)",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "FlagName, JobsWithFlag, AdoptionRate, AvgPriceWith, AvgPriceWithout, PriceImpact, TotalRevenue",
                "visualization": "table_with_bar",
                "best_for": "Understanding finishing options usage, identifying upsell opportunities",
                "validated": True
            },
            
            "rush_pricing_impact": {
                "category": "Upsell & Revenue",
                "description": "Analysis of pricing by urgency level to validate rush pricing strategy",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    },
                    "product_filter": {
                        "type": "string",
                        "description": "Optional product type filter (default: None)",
                        "default": None
                    }
                },
                "returns": "UrgencyLevel, ProductType, JobCount, AvgPrice, AvgPricePerUnit, PricePremium",
                "visualization": "grouped_bar",
                "best_for": "Rush pricing strategy, dynamic pricing, urgency premiums",
                "validated": True
            },
            
            "fold_type_analysis": {
                "category": "Upsell & Revenue",
                "description": "Analysis of all fold types ordered with frequency and pricing",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "FoldDesc, JobCount, AvgPrice, TotalRevenue, CommonProduct",
                "visualization": "table",
                "best_for": "Standardizing fold options, equipment planning, quick quote suggestions",
                "validated": True
            },
            
            # ============================================
            # OPERATIONAL OPTIMIZATION (NEW)
            # ============================================
            "department_workload_balance": {
                "category": "Operational Optimization",
                "description": "Workload distribution across departments (Digital, Signage, Pre-Production)",
                "parameters": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default: 30)",
                        "default": 30
                    }
                },
                "returns": "Department, ActiveJobs, TotalValue, AvgDaysInDept, OldestJob",
                "visualization": "horizontal_bar",
                "best_for": "Resource allocation, hiring decisions, capacity balancing",
                "validated": True
            },
            
            "popular_specifications": {
                "category": "Operational Optimization",
                "description": "Most frequently ordered product specifications for quick quote building",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 6)",
                        "default": 6
                    },
                    "product_type": {
                        "type": "string",
                        "description": "Optional product type filter (default: None)",
                        "default": None
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum order count to include (default: 5)",
                        "default": 5
                    }
                },
                "returns": "ProductType, PaperSize, PaperType, GSM, BindType, OrderCount, AvgPrice, TotalRevenue",
                "visualization": "table",
                "best_for": "Quick quote builder, inventory planning, customer preferences",
                "validated": True
            },
            
            # ============================================
            # CUSTOMER BEHAVIOR ANALYSIS (NEW)
            # ============================================
            "customer_reorder_prediction": {
                "category": "Customer Behavior",
                "description": "Predict customers due for reorder based on historical patterns",
                "parameters": {
                    "days_overdue": {
                        "type": "integer",
                        "description": "Days past average reorder cycle (default: 7)",
                        "default": 7
                    }
                },
                "returns": "ClientName, LastOrderDate, DaysSinceLastOrder, AvgReorderCycle, DaysOverdue, LastProduct",
                "visualization": "table_alert",
                "best_for": "Proactive customer outreach, retention campaigns, sales follow-up",
                "validated": True
            },
            
            "customer_reorder_prediction_business": {
                "category": "Customer Analytics",
                "description": "Identifies commercial business customers (printing, signage, marketing) overdue for reorders. Excludes book publishing. Focuses on recent, actionable opportunities for sales outreach campaigns.",
                "parameters": {
                    "top_n": {
                        "type": "integer",
                        "description": "Number of customers to return (default: 50)",
                        "default": 50,
                        "min": 10,
                        "max": 200
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum historical orders (2=new repeats, 5+=loyal) (default: 2)",
                        "default": 2,
                        "min": 2,
                        "max": 10
                    },
                    "min_days_since": {
                        "type": "integer",
                        "description": "Minimum days since last order (default: 90)",
                        "default": 90,
                        "min": 30,
                        "max": 365
                    },
                    "max_years_back": {
                        "type": "integer",
                        "description": "How far back to look (2=recent, actionable) (default: 2)",
                        "default": 2,
                        "min": 1,
                        "max": 5
                    }
                },
                "returns": "ClientName, LastOrderDate, DaysSinceLastOrder, AvgOrderCycle, DaysOverdue, LastProduct, LastOrderValue, TotalOrders, JobType",
                "visualization": "table_alert",
                "best_for": "Weekly sales outreach, monthly campaigns, high-risk customer alerts. Use for commercial printing customers (business cards, flyers, signage)",
                "validated": True
            },
            
            "customer_reorder_prediction_publishing": {
                "category": "Customer Analytics",
                "description": "Identifies book publishing customers (authors, publishers) overdue for book reprints. Focuses on Perfect Bound, Spiral Bound, and Casebound products with longer reorder cycles.",
                "parameters": {
                    "top_n": {
                        "type": "integer",
                        "description": "Number of authors/publishers to return (default: 30)",
                        "default": 30,
                        "min": 10,
                        "max": 100
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum print runs (2=reprinted once, 3+=proven seller) (default: 2)",
                        "default": 2,
                        "min": 2,
                        "max": 10
                    },
                    "min_days_since": {
                        "type": "integer",
                        "description": "Minimum days since last print run (default: 180)",
                        "default": 180,
                        "min": 90,
                        "max": 730
                    },
                    "max_years_back": {
                        "type": "integer",
                        "description": "How far back to look (3 years for book cycles) (default: 3)",
                        "default": 3,
                        "min": 2,
                        "max": 5
                    }
                },
                "returns": "ClientName, LastOrderDate, DaysSinceLastOrder, AvgReprintCycle, DaysOverdue, LastProduct, LastOrderValue, Pages, LastQuantity, TotalPrintRuns, JobType",
                "visualization": "table_alert",
                "best_for": "Quarterly reprint campaigns, seasonal pre-campaigns, bestseller VIP programs. Use for book authors and publishers",
                "validated": True
            },
            
            "reorder_opportunities_by_product": {
                "category": "Sales & Revenue Optimization",
                "description": "Identifies customers overdue for reorders of specific product types. Enables targeted product-specific campaigns (e.g., 'Business Card Refresh', 'Spring Signage Push').",
                "parameters": {
                    "product_type": {
                        "type": "string",
                        "description": "Specific product or NULL for all products (e.g., 'Business Cards - Double Sided', 'Corflute', 'Flyers - Double Sided'). NULL = all products (default: NULL)",
                        "default": None,
                        "optional": True
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of customers to return (default: 50)",
                        "default": 50,
                        "min": 10,
                        "max": 200
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum orders of this specific product (default: 2)",
                        "default": 2,
                        "min": 2,
                        "max": 10
                    },
                    "min_days_since": {
                        "type": "integer",
                        "description": "Minimum days since last order (default: 60)",
                        "default": 60,
                        "min": 30,
                        "max": 365
                    },
                    "max_years_back": {
                        "type": "integer",
                        "description": "How far back to look (default: 2)",
                        "default": 2,
                        "min": 1,
                        "max": 5
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "How to prioritize results: 'overdue', 'value', 'frequency' (default: 'overdue')",
                        "default": "overdue",
                        "options": ["overdue", "value", "frequency"]
                    }
                },
                "returns": "ClientName, ProductType, LastOrderDate, DaysSinceLastOrder, TypicalReorderCycle, DaysOverdue, TotalOrders, AvgOrderValue, LastOrderValue, LastProductSpec",
                "visualization": "table_alert",
                "best_for": "Product-specific campaigns (business card refresh, spring signage push, sticker reorder automation), monthly campaign calendar. Use to target specific products like business cards, corflutes, stickers, flyers",
                "validated": True
            },
            
            "product_bundle_opportunities": {
                "category": "Customer Behavior",
                "description": "Products frequently ordered together for cross-sell recommendations",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    },
                    "min_co_occurrence": {
                        "type": "integer",
                        "description": "Minimum times products ordered together (default: 5)",
                        "default": 5
                    }
                },
                "returns": "Product1, Product2, CoOccurrences, UniqueCustomers, BundleOpportunity",
                "visualization": "network_graph",
                "best_for": "Bundle creation, cross-sell strategy, package deals",
                "validated": True
            },
            
            # ============================================
            # SPECIFICATION INTELLIGENCE (NEW)
            # ============================================
            "paper_gsm_popularity": {
                "category": "Specification Intelligence",
                "description": "Paper GSM usage by product type for inventory forecasting",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "PaperType, GSM, ProductType, OrderCount, TotalQuantity, AvgPrice",
                "visualization": "heatmap",
                "best_for": "Inventory management, supplier negotiations, stock forecasting",
                "validated": True
            },
            
            "binding_by_page_count": {
                "category": "Specification Intelligence",
                "description": "Binding type recommendations based on page count analysis",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 12)",
                        "default": 12
                    }
                },
                "returns": "PageRange, BindType, OrderCount, AvgPrice, PercentOfRange",
                "visualization": "stacked_bar",
                "best_for": "Binding recommendations, calculator validation, quote accuracy",
                "validated": True
            },
            
            # ============================================
            # AI EXPORT & ANALYSIS (NEW - October 2025)
            # ============================================
            "conversation_data_export": {
                "category": "AI Export & Analysis",
                "description": "Export complete conversation session data for AI analysis - includes all messages, queries, results, and metadata",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to export (optional, defaults to current session)",
                        "default": None
                    },
                    "include_sql": {
                        "type": "boolean",
                        "description": "Include SQL queries in export (default: True)",
                        "default": True
                    },
                    "include_results": {
                        "type": "boolean",
                        "description": "Include query results (default: True)",
                        "default": True
                    }
                },
                "returns": "SessionID, MessageID, MessageType, Content, Timestamp, SQLQuery, ResultRows",
                "visualization": "json_export",
                "best_for": "AI conversation analysis, session review, external analysis",
                "validated": True
            },
            
            "dashboard_snapshot_export": {
                "category": "AI Export & Analysis",
                "description": "Export current dashboard state with all active queries and results for AI analysis",
                "parameters": {
                    "section_filter": {
                        "type": "string",
                        "description": "Filter by section: workflow, client, financial, division, capacity, timeline, quality, all (default: all)",
                        "default": "all"
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format: json, csv, markdown (default: json)",
                        "default": "json"
                    }
                },
                "returns": "SectionName, QueryName, DataSummary, RecordCount, LastUpdated",
                "visualization": "json_export",
                "best_for": "Dashboard state capture, AI-powered insights, trend analysis",
                "validated": True
            },
            
            "session_query_history": {
                "category": "AI Export & Analysis",
                "description": "Get history of all queries executed in current session with performance metrics",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to analyze (optional)",
                        "default": None
                    },
                    "min_duration_ms": {
                        "type": "integer",
                        "description": "Filter queries slower than N milliseconds (default: 0)",
                        "default": 0
                    }
                },
                "returns": "QueryID, QueryName, ExecutionTime, RowsReturned, Timestamp, Success",
                "visualization": "table",
                "best_for": "Performance analysis, query optimization, session debugging",
                "validated": True
            },
            
            "ai_insights_summary": {
                "category": "AI Export & Analysis",
                "description": "Generate AI-ready summary of business insights based on recent data - perfect for external AI analysis",
                "parameters": {
                    "insight_focus": {
                        "type": "string",
                        "description": "Focus area: sales, operations, customers, products, financial (default: all)",
                        "default": "all"
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Days of data to analyze (default: 30)",
                        "default": 30
                    }
                },
                "returns": "InsightCategory, KeyMetric, CurrentValue, Trend, Context, Recommendation",
                "visualization": "markdown_report",
                "best_for": "Executive briefings, AI-powered strategy, trend identification",
                "validated": True
            },
            
            # ============================================
            # STOCK MANAGEMENT (NEW - October 2025)
            # ============================================
            
            "stock_inventory_master": {
                "category": "Stock Management",
                "description": "Complete stock master inventory with pricing, markups, stock levels, and reorder information",
                "parameters": {
                    "status_filter": {
                        "type": "string",
                        "description": "Filter by status: all, critical, low, ok, inactive (default: all)",
                        "default": "all"
                    },
                    "stock_type": {
                        "type": "string",
                        "description": "Filter by stock type (default: all)",
                        "default": "all"
                    }
                },
                "returns": "StockID, StockType, Size, GSM, CostPer1000, Markup, FinalPrice, StockLevel, ReorderPoint, Status, LastUsed, Usage30d",
                "visualization": "data_table",
                "best_for": "Inventory management, stock monitoring, pricing control",
                "validated": False
            },
            
            "stock_usage_analytics": {
                "category": "Stock Management",
                "description": "Stock usage patterns with forecasting for next 30 days based on historical consumption",
                "parameters": {
                    "days_back": {
                        "type": "integer",
                        "description": "Historical days to analyze (default: 90)",
                        "default": 90
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top stocks to show (default: 20)",
                        "default": 20
                    }
                },
                "returns": "StockType, TotalUsage, AvgDailyUsage, Trend, ForecastNext30Days, CurrentStock, DaysUntilEmpty",
                "visualization": "bar_chart_horizontal",
                "best_for": "Demand forecasting, inventory planning, usage patterns",
                "validated": False
            },
            
            "stock_reorder_alerts": {
                "category": "Stock Management",
                "description": "List of stocks that need reordering based on current levels and usage patterns",
                "parameters": {
                    "urgency": {
                        "type": "string",
                        "description": "Filter by urgency: all, critical, moderate, upcoming (default: all)",
                        "default": "all"
                    }
                },
                "returns": "StockType, CurrentLevel, ReorderPoint, DaysUntilEmpty, SuggestedOrderQty, EstimatedCost, LastOrderDate",
                "visualization": "data_table",
                "best_for": "Purchase planning, stock replenishment, budget forecasting",
                "validated": False
            },
            
            "stock_pricing_profitability": {
                "category": "Stock Management",
                "description": "Analyze profitability by stock type showing markup performance and margin contribution",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Months to analyze (default: 6)",
                        "default": 6
                    }
                },
                "returns": "StockType, TotalRevenue, TotalCost, GrossProfit, MarginPercent, OrderCount, AvgMarkup",
                "visualization": "scatter_plot",
                "best_for": "Pricing strategy, margin optimization, profitability analysis",
                "validated": False
            },
            
            "client_stock_preferences": {
                "category": "Stock Management",
                "description": "Customer stock preferences and reorder patterns for intelligent recommendations",
                "parameters": {
                    "months": {
                        "type": "integer",
                        "description": "Historical months to analyze (default: 12)",
                        "default": 12
                    },
                    "min_orders": {
                        "type": "integer",
                        "description": "Minimum orders to include client (default: 3)",
                        "default": 3
                    }
                },
                "returns": "ClientName, PreferredStocks, OrderFrequency, AvgOrderSize, LastOrderDate, PredictedReorderDate",
                "visualization": "data_table",
                "best_for": "Customer intelligence, proactive sales, inventory anticipation",
                "validated": False
            },
            
            "stock_cost_trends": {
                "category": "Stock Management",
                "description": "Historical cost trends for stocks showing supplier price changes over time",
                "parameters": {
                    "stock_type": {
                        "type": "string",
                        "description": "Specific stock type to analyze (default: all top 10)",
                        "default": "all"
                    },
                    "months": {
                        "type": "integer",
                        "description": "Months of history (default: 24)",
                        "default": 24
                    }
                },
                "returns": "YearMonth, StockType, CostPer1000, ChangePercent, SupplierName",
                "visualization": "line_chart",
                "best_for": "Cost monitoring, supplier negotiation, budget planning",
                "validated": False
            },
            
            # ============================================
            # CALCULATOR PRICING MANAGEMENT
            # ============================================
            "get_pricing_constant": {
                "category": "Calculator Pricing Management",
                "description": "Get complete details for a pricing parameter including base value, all calculator overrides, and variance statistics",
                "parameters": {
                    "parameter_name": {
                        "type": "string",
                        "description": "Name of the pricing parameter (e.g., 'impos_setup', 'markup_multiplier')",
                        "required": True
                    },
                    "calculator_name": {
                        "type": "string",
                        "description": "Optional: Filter to specific calculator (e.g., 'BollardSigns', 'BusinessCards')",
                        "default": None
                    }
                },
                "returns": "parameter_name, base_value, data_type, override_count, calculator_name, override_value, variance_pct, min_value, max_value, mean_value, median_value",
                "visualization": "table_with_stats",
                "best_for": "Understanding parameter pricing across calculators, identifying price variations, checking override values before updates",
                "validated": True
            },
            
            "get_calculator_config": {
                "category": "Calculator Pricing Management",
                "description": "Get complete pricing configuration for a calculator including all parameters used, active overrides, and product options",
                "parameters": {
                    "calculator_name": {
                        "type": "string",
                        "description": "Name of calculator (e.g., 'BollardSigns', 'BusinessCards', 'PerfectBoundBooks')",
                        "required": True
                    },
                    "include_product_options": {
                        "type": "boolean",
                        "description": "Include product options with choices (default: true)",
                        "default": True
                    }
                },
                "returns": "calculator_name, calculator_file, parameters_used, active_overrides, product_options, option_choices",
                "visualization": "nested_table",
                "best_for": "Full calculator audit, verifying configuration, preparing for calculator updates, debugging pricing issues",
                "validated": True
            },
            
            "get_product_options_for_calculator": {
                "category": "Calculator Pricing Management",
                "description": "Get all product options with choices for a specific calculator, including prices and price types",
                "parameters": {
                    "calculator_name": {
                        "type": "string",
                        "description": "Name of calculator",
                        "required": True
                    },
                    "include_inactive": {
                        "type": "boolean",
                        "description": "Include inactive options (default: false)",
                        "default": False
                    }
                },
                "returns": "option_name, option_type, choice_value, choice_label, price, price_type, is_default, display_order",
                "visualization": "grouped_table",
                "best_for": "Reviewing customer-facing options, checking option prices, verifying product configurations",
                "validated": True
            },
            
            "find_high_variance_parameters": {
                "category": "Calculator Pricing Management",
                "description": "Find pricing parameters with high variance across calculators (indicates significant price differences)",
                "parameters": {
                    "variance_threshold": {
                        "type": "float",
                        "description": "Minimum variance percentage to include (default: 100)",
                        "default": 100.0
                    },
                    "min_calculators": {
                        "type": "integer",
                        "description": "Minimum number of calculators using parameter (default: 3)",
                        "default": 3
                    }
                },
                "returns": "parameter_name, base_value, variance_pct, min_value, max_value, calculator_count, calculators_list",
                "visualization": "bar_chart",
                "best_for": "Identifying pricing inconsistencies, finding parameters needing standardization, audit review",
                "validated": True
            },
            
            "get_parameter_usage_map": {
                "category": "Calculator Pricing Management",
                "description": "Show which calculators use which pricing parameters - useful for impact analysis before parameter changes",
                "parameters": {
                    "parameter_name": {
                        "type": "string",
                        "description": "Optional: Filter to specific parameter",
                        "default": None
                    },
                    "min_calculators": {
                        "type": "integer",
                        "description": "Minimum number of calculators to include (default: 2)",
                        "default": 2
                    }
                },
                "returns": "parameter_name, calculator_count, calculator_names, has_overrides, override_count",
                "visualization": "network_graph",
                "best_for": "Impact analysis before changes, understanding parameter dependencies, finding shared parameters",
                "validated": True
            },
            
            "search_product_options": {
                "category": "Calculator Pricing Management",
                "description": "Search product options by name, type, or calculator - useful for finding specific options across all calculators",
                "parameters": {
                    "search_term": {
                        "type": "string",
                        "description": "Search term for option name (partial match, case-insensitive)",
                        "default": None
                    },
                    "calculator_name": {
                        "type": "string",
                        "description": "Filter to specific calculator",
                        "default": None
                    },
                    "option_type": {
                        "type": "string",
                        "description": "Filter by option type (select, radio, checkbox, etc.)",
                        "default": None
                    }
                },
                "returns": "option_name, option_type, calculator_name, choice_count, has_prices, price_range",
                "visualization": "table",
                "best_for": "Finding options across calculators, discovering similar configurations, bulk option analysis",
                "validated": True
            },
            
            "get_option_price_variance": {
                "category": "Calculator Pricing Management",
                "description": "Find product options with high price variance across choices - identifies options with wide price ranges",
                "parameters": {
                    "calculator_name": {
                        "type": "string",
                        "description": "Optional: Filter to specific calculator",
                        "default": None
                    },
                    "min_choices": {
                        "type": "integer",
                        "description": "Minimum number of choices (default: 3)",
                        "default": 3
                    }
                },
                "returns": "option_name, calculator_name, choice_count, min_price, max_price, avg_price, price_range, variance_pct",
                "visualization": "bar_chart",
                "best_for": "Reviewing pricing spreads, identifying premium vs standard options, price audit",
                "validated": True
            }
        }
    
    def get_available_queries(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available queries with metadata
        
        Args:
            category: Optional category filter
            
        Returns:
            List of query definitions with metadata
        """
        queries = []
        for query_name, query_def in self.query_catalog.items():
            if category is None or query_def['category'] == category:
                queries.append({
                    "name": query_name,
                    **query_def
                })
        return queries
    
    def get_query_categories(self) -> List[str]:
        """Get list of all query categories"""
        categories = set()
        for query_def in self.query_catalog.values():
            categories.add(query_def['category'])
        return sorted(list(categories))
    
    def get_query_definition(self, query_name: str) -> Dict[str, Any]:
        """
        Get definition for a specific query
        
        Args:
            query_name: Name of the query
            
        Returns:
            Query definition with metadata
        """
        if query_name not in self.query_catalog:
            raise ValueError(f"Query '{query_name}' not found in catalog")
        
        return {
            "name": query_name,
            **self.query_catalog[query_name]
        }
    
    def build_query(self, query_name: str, **parameters) -> Dict[str, Any]:
        """
        Build SQL query with provided parameters
        
        Args:
            query_name: Name of the query to build
            **parameters: Query parameters
            
        Returns:
            Dictionary with 'sql', 'parameters', 'metadata'
        """
        if query_name not in self.query_catalog:
            raise ValueError(f"Query '{query_name}' not found in catalog")
        
        query_def = self.query_catalog[query_name]
        
        # Validate and apply default parameters
        validated_params = self._validate_parameters(query_name, parameters)
        
        # Build SQL based on query name
        sql = self._generate_sql(query_name, validated_params)
        
        return {
            "query_name": query_name,
            "sql": sql,
            "parameters": validated_params,
            "metadata": {
                "category": query_def['category'],
                "description": query_def['description'],
                "visualization": query_def['visualization'],
                "returns": query_def['returns']
            }
        }
    
    # ============================================
    # EXECUTION + FORMAT LAYER (NEW)
    # ============================================
    
    def execute_query(self, query_name: str, **parameters) -> Dict[str, Any]:
        """
        Execute query and return formatted results with metadata
        
        This is the PRIMARY method for AI agents - it handles everything:
        - SQL generation
        - Execution
        - Data formatting (currency, dates, percentages)
        - Error handling
        - Result summary
        
        Args:
            query_name: Name of the query to execute
            **parameters: Query parameters
            
        Returns:
            Dictionary with:
                - 'data': Formatted pandas DataFrame
                - 'summary': Human-readable summary
                - 'metadata': Query metadata + execution stats
                - 'success': Boolean execution status
                - 'error': Error message if failed
        """
        try:
            # Check database connection
            if self.db is None:
                return {
                    'success': False,
                    'error': 'No database connection available',
                    'data': pd.DataFrame(),
                    'summary': 'Database connection required'
                }
            
            # Build query
            query_result = self.build_query(query_name, **parameters)
            sql = query_result['sql']
            metadata = query_result['metadata']
            
            # Execute query
            start_time = datetime.now()
            df = self.db.execute_query(sql)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Handle empty results
            if df is None or df.empty:
                return {
                    'success': True,
                    'data': pd.DataFrame(),
                    'summary': f"Query '{query_name}' returned no results",
                    'metadata': {
                        **metadata,
                        'row_count': 0,
                        'execution_time_seconds': execution_time
                    }
                }
            
            # Format the DataFrame
            formatted_df = self._format_dataframe(df, metadata)
            
            # Generate summary
            summary = self._generate_summary(formatted_df, query_name, metadata)
            
            # Calculate data quality metrics
            quality_metrics = self._calculate_quality_metrics(formatted_df)
            
            return {
                'success': True,
                'data': formatted_df,
                'summary': summary,
                'metadata': {
                    **metadata,
                    'query_name': query_name,
                    'parameters': parameters,
                    'row_count': len(formatted_df),
                    'column_count': len(formatted_df.columns),
                    'execution_time_seconds': round(execution_time, 3),
                    'data_quality': quality_metrics
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': pd.DataFrame(),
                'summary': f"Error executing query '{query_name}': {str(e)}",
                'metadata': {
                    'query_name': query_name,
                    'parameters': parameters
                }
            }
    
    def _format_dataframe(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> pd.DataFrame:
        """
        Auto-format DataFrame columns based on metadata and data types
        
        Args:
            df: Raw DataFrame from SQL query
            metadata: Query metadata with column information
            
        Returns:
            Formatted DataFrame with proper types and display formats
        """
        formatted_df = df.copy()
        
        # Get column names and hints from metadata
        returns_str = metadata.get('returns', '')
        column_hints = self._parse_column_hints(returns_str)
        
        for col in formatted_df.columns:
            col_lower = col.lower()
            
            # Format currency columns
            if any(keyword in col_lower for keyword in ['revenue', 'cost', 'price', 'value', 'total', 'avg']):
                if formatted_df[col].dtype in ['float64', 'int64']:
                    # Keep numeric for calculations, but add formatted string column
                    formatted_df[f'{col}_Formatted'] = formatted_df[col].apply(
                        lambda x: f"${x:,.2f}" if pd.notna(x) else 'N/A'
                    )
            
            # Format percentage columns
            elif any(keyword in col_lower for keyword in ['percent', 'rate', 'ratio', '%']):
                if formatted_df[col].dtype in ['float64', 'int64']:
                    formatted_df[f'{col}_Formatted'] = formatted_df[col].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else 'N/A'
                    )
            
            # Format date columns
            elif any(keyword in col_lower for keyword in ['date', 'time', 'day']):
                try:
                    formatted_df[col] = pd.to_datetime(formatted_df[col])
                    formatted_df[f'{col}_Formatted'] = formatted_df[col].dt.strftime('%b %d, %Y')
                except:
                    pass  # Not a date column
            
            # Format count/quantity columns (no decimals)
            elif any(keyword in col_lower for keyword in ['count', 'quantity', 'qty', 'number']):
                if formatted_df[col].dtype in ['float64', 'int64']:
                    formatted_df[f'{col}_Formatted'] = formatted_df[col].apply(
                        lambda x: f"{int(x):,}" if pd.notna(x) else 'N/A'
                    )
        
        return formatted_df
    
    def _parse_column_hints(self, returns_str: str) -> Dict[str, str]:
        """
        Parse column hints from returns metadata string
        
        Args:
            returns_str: Comma-separated column names from metadata
            
        Returns:
            Dictionary mapping column names to type hints
        """
        hints = {}
        columns = [col.strip() for col in returns_str.split(',')]
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['revenue', 'cost', 'price', 'value']):
                hints[col] = 'currency'
            elif any(keyword in col_lower for keyword in ['percent', 'rate']):
                hints[col] = 'percentage'
            elif any(keyword in col_lower for keyword in ['date', 'time']):
                hints[col] = 'date'
            elif any(keyword in col_lower for keyword in ['count', 'quantity']):
                hints[col] = 'integer'
        
        return hints
    
    def _generate_summary(self, df: pd.DataFrame, query_name: str, metadata: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of query results
        
        Args:
            df: Formatted DataFrame
            query_name: Name of the query
            metadata: Query metadata
            
        Returns:
            Summary string for AI agent
        """
        if df.empty:
            return f"Query '{query_name}' returned no results."
        
        row_count = len(df)
        category = metadata.get('category', 'Unknown')
        
        summary_parts = [
            f"**{query_name}** ({category})",
            f"Found {row_count:,} {'record' if row_count == 1 else 'records'}"
        ]
        
        # Add key metrics based on column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:3]:  # Show top 3 numeric columns
            col_lower = col.lower()
            
            if 'revenue' in col_lower or 'value' in col_lower or 'cost' in col_lower:
                total = df[col].sum()
                summary_parts.append(f"Total {col}: ${total:,.2f}")
            
            elif 'count' in col_lower or 'quantity' in col_lower:
                total = df[col].sum()
                summary_parts.append(f"Total {col}: {int(total):,}")
            
            elif 'percent' in col_lower or 'rate' in col_lower:
                avg = df[col].mean()
                summary_parts.append(f"Average {col}: {avg:.1f}%")
        
        return " | ".join(summary_parts)
    
    def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate data quality metrics for the results
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        if df.empty:
            return {
                'completeness': 0.0,
                'null_percentages': {},
                'data_types': {}
            }
        
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = ((total_cells - null_cells) / total_cells * 100) if total_cells > 0 else 0
        
        null_percentages = {}
        for col in df.columns:
            if not col.endswith('_Formatted'):  # Skip formatted columns
                null_pct = (df[col].isnull().sum() / len(df) * 100) if len(df) > 0 else 0
                if null_pct > 0:
                    null_percentages[col] = round(null_pct, 1)
        
        data_types = {col: str(df[col].dtype) for col in df.columns if not col.endswith('_Formatted')}
        
        return {
            'completeness_percentage': round(completeness, 1),
            'null_columns': null_percentages,
            'data_types': data_types,
            'total_rows': len(df),
            'total_columns': len([c for c in df.columns if not c.endswith('_Formatted')])
        }
    
    def execute_query_batch(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple queries in batch and return combined results
        
        Args:
            queries: List of dicts with 'query_name' and 'parameters'
            
        Returns:
            Dictionary with results for each query
        """
        results = {}
        total_start = datetime.now()
        
        for query_spec in queries:
            query_name = query_spec.get('query_name')
            parameters = query_spec.get('parameters', {})
            
            if query_name:
                result = self.execute_query(query_name, **parameters)
                results[query_name] = result
        
        total_time = (datetime.now() - total_start).total_seconds()
        
        return {
            'batch_results': results,
            'total_queries': len(queries),
            'successful': sum(1 for r in results.values() if r.get('success')),
            'failed': sum(1 for r in results.values() if not r.get('success')),
            'total_execution_time_seconds': round(total_time, 3)
        }
    
    def _validate_parameters(self, query_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and apply defaults to parameters
        
        Args:
            query_name: Name of the query
            parameters: User-provided parameters
            
        Returns:
            Validated parameters with defaults applied
        """
        query_def = self.query_catalog[query_name]
        validated = {}
        
        for param_name, param_def in query_def['parameters'].items():
            if param_name in parameters:
                value = parameters[param_name]
                
                # Type validation
                expected_type = param_def['type']
                if expected_type == 'integer' and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parameter '{param_name}' must be an integer")
                
                elif expected_type == 'float' and not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parameter '{param_name}' must be a number")
                
                elif expected_type == 'string' and not isinstance(value, str):
                    value = str(value)
                
                # Range validation
                if 'min' in param_def and value < param_def['min']:
                    raise ValueError(f"Parameter '{param_name}' must be >= {param_def['min']}")
                if 'max' in param_def and value > param_def['max']:
                    raise ValueError(f"Parameter '{param_name}' must be <= {param_def['max']}")
                
                validated[param_name] = value
            else:
                # Apply default if available
                if 'default' in param_def:
                    validated[param_name] = param_def['default']
        
        return validated
    
    def _generate_sql(self, query_name: str, parameters: Dict[str, Any]) -> str:
        """
        Generate SQL for the specified query with parameters
        
        Args:
            query_name: Name of the query
            parameters: Validated parameters
            
        Returns:
            SQL string ready to execute
        """
        # Calculate date ranges
        today = datetime.now()
        
        # Route to appropriate SQL generator
        if query_name == "sales_trend_by_month":
            return self._sql_sales_trend_by_month(parameters)
        elif query_name == "revenue_by_product_type":
            return self._sql_revenue_by_product_type(parameters)
        elif query_name == "revenue_by_customer":
            return self._sql_revenue_by_customer(parameters)
        elif query_name == "customer_retention_cohort":
            return self._sql_customer_retention_cohort(parameters)
        elif query_name == "customer_order_frequency":
            return self._sql_customer_order_frequency(parameters)
        elif query_name == "customer_lifetime_value":
            return self._sql_customer_lifetime_value(parameters)
        elif query_name == "product_performance_detail":
            return self._sql_product_performance_detail(parameters)
        elif query_name == "paper_stock_usage":
            return self._sql_paper_stock_usage(parameters)
        elif query_name == "finishing_options_popularity":
            return self._sql_finishing_options_popularity(parameters)
        elif query_name == "production_turnaround_time":
            return self._sql_production_turnaround_time(parameters)
        elif query_name == "order_size_distribution":
            return self._sql_order_size_distribution(parameters)
        elif query_name == "daily_order_volume":
            return self._sql_daily_order_volume(parameters)
        elif query_name == "apg_workflow_status":
            return self._sql_apg_workflow_status(parameters)
        elif query_name == "publishing_projects_pipeline":
            return self._sql_publishing_projects_pipeline(parameters)
        elif query_name == "perfect_bound_books_analysis":
            return self._sql_perfect_bound_books_analysis(parameters)
        elif query_name == "year_over_year_comparison":
            return self._sql_year_over_year_comparison(parameters)
        
        # OPERATIONAL FLOW QUERIES (NEW - VALIDATED)
        elif query_name == "current_production_status":
            return self._sql_current_production_status(parameters)
        elif query_name == "overdue_jobs_alert":
            return self._sql_overdue_jobs_alert(parameters)
        elif query_name == "priority_work_queue":
            return self._sql_priority_work_queue(parameters)
        elif query_name == "bottleneck_detection":
            return self._sql_bottleneck_detection(parameters)
        elif query_name == "daily_capacity_forecast":
            return self._sql_daily_capacity_forecast(parameters)
        elif query_name == "urgency_level_distribution":
            return self._sql_urgency_level_distribution(parameters)
        elif query_name == "job_complexity_analysis":
            return self._sql_job_complexity_analysis(parameters)
        
        # PRODUCTION PLANNING QUERIES (NEW - COMPREHENSIVE)
        elif query_name == "daily_production_plan":
            return self._sql_daily_production_plan(parameters)
        elif query_name == "stage_capacity_report":
            return self._sql_stage_capacity_report(parameters)
        elif query_name == "weekly_production_forecast":
            return self._sql_weekly_production_forecast(parameters)
        elif query_name == "bottleneck_detection_advanced":
            return self._sql_bottleneck_detection_advanced(parameters)
        
        # CUSTOMER ANALYTICS (UPDATED - VALIDATED)
        elif query_name == "top_customers_detailed":
            return self._sql_top_customers_detailed(parameters)
        elif query_name == "customer_product_preferences":
            return self._sql_customer_product_preferences(parameters)
        
        # PRODUCT ANALYSIS (UPDATED - VALIDATED)
        elif query_name == "product_turnaround_benchmarks":
            return self._sql_product_turnaround_benchmarks(parameters)
        elif query_name == "high_value_jobs_list":
            return self._sql_high_value_jobs_list(parameters)
        elif query_name == "binding_finishing_analysis":
            return self._sql_binding_finishing_analysis(parameters)
        
        # TIME-BASED PATTERNS (VALIDATED)
        elif query_name == "monthly_revenue_trend":
            return self._sql_monthly_revenue_trend(parameters)
        elif query_name == "day_of_week_patterns":
            return self._sql_day_of_week_patterns(parameters)
        elif query_name == "quarterly_performance":
            return self._sql_quarterly_performance(parameters)
        
        # PERFORMANCE & SLA TRACKING (NEW - VALIDATED)
        elif query_name == "on_time_delivery_rate":
            return self._sql_on_time_delivery_rate(parameters)
        elif query_name == "customer_deadline_realism":
            return self._sql_customer_deadline_realism(parameters)
        
        # UPSELL & REVENUE OPTIMIZATION (NEW - VALIDATED)
        elif query_name == "finishing_upsell_analysis":
            return self._sql_finishing_upsell_analysis(parameters)
        elif query_name == "boolean_flags_summary":
            return self._sql_boolean_flags_summary(parameters)
        elif query_name == "rush_pricing_impact":
            return self._sql_rush_pricing_impact(parameters)
        elif query_name == "fold_type_analysis":
            return self._sql_fold_type_analysis(parameters)
        
        # OPERATIONAL OPTIMIZATION (NEW - VALIDATED)
        elif query_name == "department_workload_balance":
            return self._sql_department_workload_balance(parameters)
        elif query_name == "popular_specifications":
            return self._sql_popular_specifications(parameters)
        
        # CUSTOMER BEHAVIOR ANALYSIS (NEW - VALIDATED)
        elif query_name == "customer_reorder_prediction":
            return self._sql_customer_reorder_prediction(parameters)
        elif query_name == "customer_reorder_prediction_business":
            return self._sql_customer_reorder_prediction_business(parameters)
        elif query_name == "customer_reorder_prediction_publishing":
            return self._sql_customer_reorder_prediction_publishing(parameters)
        elif query_name == "reorder_opportunities_by_product":
            return self._sql_reorder_opportunities_by_product(parameters)
        elif query_name == "product_bundle_opportunities":
            return self._sql_product_bundle_opportunities(parameters)
        
        # SPECIFICATION INTELLIGENCE (NEW - VALIDATED)
        elif query_name == "paper_gsm_popularity":
            return self._sql_paper_gsm_popularity(parameters)
        elif query_name == "binding_by_page_count":
            return self._sql_binding_by_page_count(parameters)
        
        # STOCK MANAGEMENT QUERIES (NEW - PRODUCTION DB)
        elif query_name == "stock_usage_analytics":
            days = parameters.get('days', parameters.get('days_back', 90))
            top_n = parameters.get('top_n', 20)
            return self._sql_stock_usage_analytics(days_back=days, top_n=top_n)
        elif query_name == "stock_reorder_alerts":
            urgency = parameters.get('urgency', 'all')
            return self._sql_stock_reorder_alerts(urgency=urgency)
        elif query_name == "stock_pricing_profitability":
            # Accept either 'days' or 'months' parameter, convert days to months
            if 'days' in parameters:
                months = max(1, parameters['days'] // 30)
            else:
                months = parameters.get('months', 6)
            return self._sql_stock_pricing_profitability(months=months)
        
        # CALCULATOR PRICING MANAGEMENT QUERIES (NEW - SUPABASE POSTGRESQL)
        elif query_name == "get_pricing_constant":
            return self._sql_get_pricing_constant(parameters)
        elif query_name == "get_calculator_config":
            return self._sql_get_calculator_config(parameters)
        elif query_name == "get_product_options_for_calculator":
            return self._sql_get_product_options_for_calculator(parameters)
        elif query_name == "find_high_variance_parameters":
            return self._sql_find_high_variance_parameters(parameters)
        elif query_name == "get_parameter_usage_map":
            return self._sql_get_parameter_usage_map(parameters)
        elif query_name == "search_product_options":
            return self._sql_search_product_options(parameters)
        elif query_name == "get_option_price_variance":
            return self._sql_get_option_price_variance(parameters)
        
        else:
            raise NotImplementedError(f"SQL generator for '{query_name}' not yet implemented")
    
    # ============================================
    # SQL GENERATORS FOR EACH QUERY
    # ============================================
    
    def _sql_sales_trend_by_month(self, params: Dict[str, Any]) -> str:
        """Generate SQL for monthly sales trends"""
        months = params['months']
        return f"""
        SELECT 
            FORMAT(o.OrderDate, 'yyyy-MM') AS Month,
            COUNT(DISTINCT o.OrderID) AS OrderCount,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgOrderValue
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY FORMAT(o.OrderDate, 'yyyy-MM')
        ORDER BY Month DESC
        """
    
    def _sql_revenue_by_product_type(self, params: Dict[str, Any]) -> str:
        """Generate SQL for revenue by product type"""
        months = params['months']
        min_revenue = params['min_revenue']
        return f"""
        SELECT 
            jtype.[Desc] AS ProductType,
            COUNT(DISTINCT jt.TicketID) AS OrderCount,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgPrice
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY jtype.[Desc]
        HAVING SUM(jt.Cost) >= {min_revenue}
        ORDER BY TotalRevenue DESC
        """
    
    def _sql_revenue_by_customer(self, params: Dict[str, Any]) -> str:
        """Generate SQL for top customers by revenue"""
        months = params['months']
        top_n = params['top_n']
        return f"""
        SELECT TOP {top_n}
            o.ClientName AS CustomerName,
            COUNT(DISTINCT o.OrderID) AS OrderCount,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgOrderValue,
            MAX(o.OrderDate) AS LastOrderDate,
            DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY o.ClientName
        ORDER BY TotalRevenue DESC
        """
    
    def _sql_customer_retention_cohort(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer cohort retention analysis"""
        cohort_months = params['cohort_months']
        return f"""
        WITH FirstOrders AS (
            SELECT 
                o.ClientName,
                MIN(o.OrderDate) AS FirstOrderDate,
                FORMAT(MIN(o.OrderDate), 'yyyy-MM') AS CohortMonth
            FROM Orders o
            GROUP BY o.ClientName
        ),
        CustomerOrders AS (
            SELECT 
                fo.ClientName,
                fo.CohortMonth,
                o.OrderDate,
                DATEDIFF(MONTH, fo.FirstOrderDate, o.OrderDate) AS MonthsSinceFirst
            FROM FirstOrders fo
            INNER JOIN Orders o ON fo.ClientName = o.ClientName
        )
        SELECT 
            CohortMonth,
            COUNT(DISTINCT ClientName) AS CustomersCount,
            COUNT(DISTINCT CASE WHEN MonthsSinceFirst > 0 THEN ClientName END) AS ReturningCustomers,
            CAST(COUNT(DISTINCT CASE WHEN MonthsSinceFirst > 0 THEN ClientName END) * 100.0 / 
                 COUNT(DISTINCT ClientName) AS DECIMAL(5,2)) AS RetentionRate
        FROM CustomerOrders
        WHERE CohortMonth >= FORMAT(DATEADD(MONTH, -{cohort_months}, GETDATE()), 'yyyy-MM')
        GROUP BY CohortMonth
        ORDER BY CohortMonth DESC
        """
    
    def _sql_customer_order_frequency(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer order frequency segmentation"""
        months = params['months']
        return f"""
        WITH CustomerFrequency AS (
            SELECT 
                o.ClientName,
                COUNT(DISTINCT o.OrderID) AS OrderCount,
                SUM(jt.Cost) AS TotalRevenue
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            GROUP BY o.ClientName
        )
        SELECT 
            CASE 
                WHEN OrderCount = 1 THEN 'One-time'
                WHEN OrderCount BETWEEN 2 AND 3 THEN 'Occasional'
                WHEN OrderCount BETWEEN 4 AND 10 THEN 'Regular'
                ELSE 'Frequent'
            END AS Segment,
            COUNT(*) AS CustomerCount,
            SUM(TotalRevenue) AS TotalRevenue,
            AVG(OrderCount) AS AvgOrdersPerCustomer
        FROM CustomerFrequency
        GROUP BY 
            CASE 
                WHEN OrderCount = 1 THEN 'One-time'
                WHEN OrderCount BETWEEN 2 AND 3 THEN 'Occasional'
                WHEN OrderCount BETWEEN 4 AND 10 THEN 'Regular'
                ELSE 'Frequent'
            END
        ORDER BY 
            CASE Segment
                WHEN 'One-time' THEN 1
                WHEN 'Occasional' THEN 2
                WHEN 'Regular' THEN 3
                WHEN 'Frequent' THEN 4
            END
        """
    
    def _sql_customer_lifetime_value(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer lifetime value analysis"""
        min_orders = params['min_orders']
        top_n = params['top_n']
        return f"""
        SELECT TOP {top_n}
            o.ClientName AS CustomerName,
            SUM(jt.Cost) AS LifetimeValue,
            COUNT(DISTINCT o.OrderID) AS OrderCount,
            MIN(o.OrderDate) AS FirstOrder,
            MAX(o.OrderDate) AS LastOrder,
            DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder,
            DATEDIFF(DAY, MIN(o.OrderDate), MAX(o.OrderDate)) AS CustomerLifespanDays
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        WHERE jt.Cost IS NOT NULL
        GROUP BY o.ClientName
        HAVING COUNT(DISTINCT o.OrderID) >= {min_orders}
        ORDER BY LifetimeValue DESC
        """
    
    def _sql_product_performance_detail(self, params: Dict[str, Any]) -> str:
        """Generate SQL for detailed product performance"""
        months = params['months']
        product_filter = params.get('product_type')
        
        product_where = ""
        if product_filter:
            product_where = f"AND jtype.[Desc] LIKE '%{product_filter}%'"
        
        return f"""
        SELECT 
            jtype.[Desc] AS ProductType,
            ps.[Desc] AS PaperSize,
            pt.[Desc] AS PaperType,
            gsm.[DESC] AS GSM,
            COUNT(*) AS OrderCount,
            SUM(jt.QTY) AS TotalQuantity,
            AVG(jt.Cost) AS AvgPrice,
            SUM(jt.Cost) AS TotalRevenue
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            {product_where}
        GROUP BY jtype.[Desc], ps.[Desc], pt.[Desc], gsm.[DESC]
        ORDER BY TotalRevenue DESC
        """
    
    def _sql_paper_stock_usage(self, params: Dict[str, Any]) -> str:
        """Generate SQL for paper stock usage analysis"""
        months = params['months']
        return f"""
        SELECT 
            pt.[Desc] AS PaperType,
            gsm.[DESC] AS GSM,
            COUNT(*) AS OrderCount,
            SUM(jt.QTY) AS TotalQuantity,
            AVG(jt.QTY) AS AvgQuantityPerOrder
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND pt.[Desc] IS NOT NULL
            AND gsm.[DESC] IS NOT NULL
        GROUP BY pt.[Desc], gsm.[DESC]
        ORDER BY OrderCount DESC
        """
    
    def _sql_finishing_options_popularity(self, params: Dict[str, Any]) -> str:
        """Generate SQL for finishing options popularity"""
        months = params['months']
        return f"""
        WITH FinishingCounts AS (
            SELECT 
                'Cello Gloss Front' AS FinishingType,
                COUNT(*) AS OrderCount,
                AVG(jt.Cost) AS AvgPrice
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.FrontCelloGloss = 1
            
            UNION ALL
            
            SELECT 
                'Cello Matt Front',
                COUNT(*),
                AVG(jt.Cost)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.FrontCelloMatt = 1
            
            UNION ALL
            
            SELECT 
                'Perfect Bind',
                COUNT(*),
                AVG(jt.Cost)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.PerfectBind = 1
            
            UNION ALL
            
            SELECT 
                'Ring Bind',
                COUNT(*),
                AVG(jt.Cost)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.RingBind = 1
        )
        SELECT 
            FinishingType,
            OrderCount,
            CAST(OrderCount * 100.0 / SUM(OrderCount) OVER () AS DECIMAL(5,2)) AS Percentage,
            AvgPrice
        FROM FinishingCounts
        WHERE OrderCount > 0
        ORDER BY OrderCount DESC
        """
    
    def _sql_production_turnaround_time(self, params: Dict[str, Any]) -> str:
        """Generate SQL for production turnaround analysis"""
        months = params['months']
        return f"""
        SELECT 
            cs.ColourDesc AS UrgencyLevel,
            jtype.[Desc] AS ProductType,
            COUNT(*) AS OrderCount,
            AVG(DATEDIFF(DAY, o.OrderDate, COALESCE(o.DateCompleted, GETDATE()))) AS AvgTurnaroundDays
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
        GROUP BY cs.ColourDesc, jtype.[Desc]
        ORDER BY cs.OrderPriority, AvgTurnaroundDays
        """
    
    def _sql_order_size_distribution(self, params: Dict[str, Any]) -> str:
        """Generate SQL for order size distribution"""
        months = params['months']
        product_filter = params.get('product_type')
        
        product_where = ""
        if product_filter:
            product_where = f"AND jtype.[Desc] LIKE '%{product_filter}%'"
        
        return f"""
        SELECT 
            CASE 
                WHEN jt.QTY < 100 THEN '0-100'
                WHEN jt.QTY < 500 THEN '100-500'
                WHEN jt.QTY < 1000 THEN '500-1000'
                WHEN jt.QTY < 5000 THEN '1000-5000'
                ELSE '5000+'
            END AS QuantityRange,
            COUNT(*) AS OrderCount,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgPrice
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.QTY IS NOT NULL
            AND jt.Cost IS NOT NULL
            {product_where}
        GROUP BY 
            CASE 
                WHEN jt.QTY < 100 THEN '0-100'
                WHEN jt.QTY < 500 THEN '100-500'
                WHEN jt.QTY < 1000 THEN '500-1000'
                WHEN jt.QTY < 5000 THEN '1000-5000'
                ELSE '5000+'
            END
        ORDER BY 
            CASE QuantityRange
                WHEN '0-100' THEN 1
                WHEN '100-500' THEN 2
                WHEN '500-1000' THEN 3
                WHEN '1000-5000' THEN 4
                WHEN '5000+' THEN 5
            END
        """
    
    def _sql_daily_order_volume(self, params: Dict[str, Any]) -> str:
        """Generate SQL for daily order volume patterns"""
        weeks = params['weeks']
        return f"""
        SELECT 
            DATENAME(WEEKDAY, o.OrderDate) AS DayOfWeek,
            DATEPART(WEEKDAY, o.OrderDate) AS DayNumber,
            COUNT(*) AS TotalOrders,
            AVG(CAST(COUNT(*) AS FLOAT)) OVER (PARTITION BY DATENAME(WEEKDAY, o.OrderDate)) AS AvgOrders,
            MAX(COUNT(*)) OVER (PARTITION BY DATENAME(WEEKDAY, o.OrderDate)) AS PeakOrders
        FROM Orders o
        WHERE o.OrderDate >= DATEADD(WEEK, -{weeks}, GETDATE())
        GROUP BY DATENAME(WEEKDAY, o.OrderDate), DATEPART(WEEKDAY, o.OrderDate), CAST(o.OrderDate AS DATE)
        ORDER BY DayNumber
        """
    
    def _sql_apg_workflow_status(self, params: Dict[str, Any]) -> str:
        """Generate SQL for APG workflow status"""
        days = params['days']
        return f"""
        SELECT 
            ajs.StageName AS WorkflowStage,
            COUNT(*) AS JobCount,
            AVG(DATEDIFF(DAY, ajt.CreatedDate, GETDATE())) AS AvgTimeInStage,
            MIN(ajt.CreatedDate) AS OldestJob
        FROM APGJobTicket ajt
        LEFT JOIN APGJobStage ajs ON ajt.CurrentStageID = ajs.StageID
        WHERE ajt.CreatedDate >= DATEADD(DAY, -{days}, GETDATE())
            AND ajt.CompletedDate IS NULL
        GROUP BY ajs.StageName
        ORDER BY JobCount DESC
        """
    
    def _sql_publishing_projects_pipeline(self, params: Dict[str, Any]) -> str:
        """Generate SQL for publishing projects pipeline"""
        status_filter = params.get('status_filter')
        
        status_where = ""
        if status_filter:
            status_where = f"AND pct.TypeName = '{status_filter}'"
        
        return f"""
        SELECT 
            pp.ProjectName,
            pct.TypeName AS Status,
            pp.StartDate,
            pp.EstimatedCompletionDate AS EstimatedCompletion,
            DATEDIFF(DAY, pp.StartDate, COALESCE(pp.ActualCompletionDate, GETDATE())) AS DaysInProgress
        FROM PublishingProject pp
        LEFT JOIN PublishingCaseType pct ON pp.CurrentCaseTypeID = pct.CaseTypeID
        WHERE pp.StartDate IS NOT NULL
            {status_where}
        ORDER BY pp.StartDate DESC
        """
    
    def _sql_perfect_bound_books_analysis(self, params: Dict[str, Any]) -> str:
        """Generate SQL for Perfect Bound Books analysis"""
        months = params['months']
        return f"""
        SELECT 
            CASE 
                WHEN pbb.Pages < 50 THEN '0-50 pages'
                WHEN pbb.Pages < 100 THEN '50-100 pages'
                WHEN pbb.Pages < 200 THEN '100-200 pages'
                ELSE '200+ pages'
            END AS PageRange,
            COUNT(*) AS OrderCount,
            AVG(pbb.CostPerBook) AS AvgCostPerBook,
            SUM(pbb.TotalCost) AS TotalRevenue
        FROM PerfectBBOrder pbb
        WHERE pbb.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND pbb.Pages IS NOT NULL
        GROUP BY 
            CASE 
                WHEN pbb.Pages < 50 THEN '0-50 pages'
                WHEN pbb.Pages < 100 THEN '50-100 pages'
                WHEN pbb.Pages < 200 THEN '100-200 pages'
                ELSE '200+ pages'
            END
        ORDER BY OrderCount DESC
        """
    
    def _sql_year_over_year_comparison(self, params: Dict[str, Any]) -> str:
        """Generate SQL for year-over-year comparison"""
        metric = params['metric']
        
        if metric == 'revenue':
            value_column = "SUM(jt.Cost)"
        elif metric == 'orders':
            value_column = "COUNT(DISTINCT o.OrderID)"
        else:  # customers
            value_column = "COUNT(DISTINCT o.ClientName)"
        
        return f"""
        WITH MonthlyData AS (
            SELECT 
                YEAR(o.OrderDate) AS Year,
                MONTH(o.OrderDate) AS Month,
                {value_column} AS Value
            FROM Orders o
            LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate >= DATEADD(YEAR, -2, GETDATE())
            GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
        )
        SELECT 
            Month,
            MAX(CASE WHEN Year = YEAR(GETDATE()) THEN Value END) AS CurrentYear,
            MAX(CASE WHEN Year = YEAR(GETDATE()) - 1 THEN Value END) AS PreviousYear,
            CAST((MAX(CASE WHEN Year = YEAR(GETDATE()) THEN Value END) - 
                  MAX(CASE WHEN Year = YEAR(GETDATE()) - 1 THEN Value END)) * 100.0 / 
                  NULLIF(MAX(CASE WHEN Year = YEAR(GETDATE()) - 1 THEN Value END), 0) AS DECIMAL(10,2)) AS PercentageChange,
            (MAX(CASE WHEN Year = YEAR(GETDATE()) THEN Value END) - 
             MAX(CASE WHEN Year = YEAR(GETDATE()) - 1 THEN Value END)) AS Difference
        FROM MonthlyData
        GROUP BY Month
        ORDER BY Month
        """
    
    # ============================================
    # NEW VALIDATED SQL GENERATORS
    # ============================================
    
    def _sql_current_production_status(self, params: Dict[str, Any]) -> str:
        """Generate SQL for real-time production status"""
        days_back = params['days_back']
        return f"""
        SELECT 
            js.[Desc] AS StageName,
            jt.StageID,
            COUNT(jt.TicketID) AS JobCount,
            SUM(jt.Cost) AS TotalValue,
            AVG(DATEDIFF(DAY, o.OrderDate, GETDATE())) AS AvgDaysInStage,
            MIN(o.OrderDate) AS OldestJobDate,
            -- Status indicator
            CASE 
                WHEN COUNT(jt.TicketID) >= 8 THEN 'CRITICAL'
                WHEN COUNT(jt.TicketID) >= 5 THEN 'WARNING'
                ELSE 'OK'
            END AS Status
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobStage js ON jt.StageID = js.StageID
        WHERE jt.StageID NOT IN (9, 10)  -- Exclude completed stages
            AND o.OrderDate >= DATEADD(DAY, -{days_back}, GETDATE())
        GROUP BY js.[Desc], jt.StageID
        ORDER BY JobCount DESC
        """

    def _sql_overdue_jobs_alert(self, params: Dict[str, Any]) -> str:
        """Generate SQL for overdue jobs alert"""
        include_completed = params.get('include_completed', False)
        
        stage_filter = ""
        if not include_completed:
            stage_filter = "AND jt.StageID NOT IN (9, 10)"
        
        return f"""
        SELECT 
            o.ClientName,
            jt.ShortJobDesc AS JobDescription,
            DATEDIFF(DAY, o.DateRequired, GETDATE()) AS DaysOverdue,
            js.[Desc] AS CurrentStage,
            jt.Cost AS JobValue,
            o.DateRequired,
            cs.ColourDesc AS Urgency,
            jt.TicketNotes AS SpecialInstructions
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobStage js ON jt.StageID = js.StageID
        LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
        WHERE o.DateRequired < CAST(GETDATE() AS DATE)
            {stage_filter}
        ORDER BY DaysOverdue DESC, jt.Cost DESC
        """

    def _sql_priority_work_queue(self, params: Dict[str, Any]) -> str:
        """Generate SQL for AI priority work queue"""
        days_ahead = params['days_ahead']
        return f"""
        SELECT TOP 50
            jt.TicketID,
            o.ClientName,
            jt.ShortJobDesc AS JobDescription,
            jt.Cost AS JobValue,
            o.DateRequired AS DueDate,
            js.[Desc] AS CurrentStage,
            cs.ColourDesc AS Urgency,
            cs.OrderPriority,
            DATEDIFF(DAY, GETDATE(), o.DateRequired) AS DaysUntilDue,
            -- Priority score calculation
            (
                (7 - COALESCE(cs.OrderPriority, 5)) * 40 +  -- Urgency (40%)
                (CASE 
                    WHEN jt.Cost >= 5000 THEN 10
                    WHEN jt.Cost >= 1000 THEN 7
                    WHEN jt.Cost >= 500 THEN 5
                    WHEN jt.Cost >= 100 THEN 3
                    ELSE 1
                END) * 20 +  -- Value (20%)
                (CASE 
                    WHEN o.DateRequired < CAST(GETDATE() AS DATE) 
                    THEN DATEDIFF(DAY, o.DateRequired, GETDATE()) * 5
                    ELSE 0
                END) * 30  -- Overdue penalty (30%)
            ) AS PriorityScore
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
        LEFT JOIN JobStage js ON jt.StageID = js.StageID
        WHERE jt.StageID NOT IN (9, 10)  -- Active jobs only
            AND o.DateRequired <= DATEADD(DAY, {days_ahead}, GETDATE())
        ORDER BY PriorityScore DESC
        """

    def _sql_bottleneck_detection(self, params: Dict[str, Any]) -> str:
        """Generate SQL for bottleneck detection"""
        wip_threshold = params['wip_threshold']
        return f"""
        SELECT 
            js.[Desc] AS StageName,
            COUNT(jt.TicketID) AS CurrentWIP,
            {wip_threshold} AS RecommendedLimit,
            COUNT(jt.TicketID) - {wip_threshold} AS OverCapacity,
            AVG(DATEDIFF(DAY, o.OrderDate, GETDATE())) AS AvgTimeInStage,
            SUM(jt.Cost) AS TotalValue,
            -- Status indicator
            CASE 
                WHEN COUNT(jt.TicketID) > {wip_threshold} THEN 'OVER_CAPACITY'
                WHEN COUNT(jt.TicketID) = {wip_threshold} THEN 'AT_CAPACITY'
                ELSE 'OK'
            END AS Status
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobStage js ON jt.StageID = js.StageID
        WHERE jt.StageID NOT IN (9, 10)
            AND o.OrderDate >= DATEADD(DAY, -30, GETDATE())
        GROUP BY js.[Desc], jt.StageID
        HAVING COUNT(jt.TicketID) > 0
        ORDER BY CurrentWIP DESC
        """

    def _sql_daily_capacity_forecast(self, params: Dict[str, Any]) -> str:
        """Generate SQL for capacity forecast"""
        days_ahead = params['days_ahead']
        return f"""
        SELECT 
            o.DateRequired AS DueDate,
            DATENAME(WEEKDAY, o.DateRequired) AS DayOfWeek,
            COUNT(jt.TicketID) AS JobsDue,
            SUM(jt.Cost) AS TotalValue,
            -- By department (based on StageID ranges)
            SUM(CASE WHEN jt.StageID IN (4,5,11) THEN 1 ELSE 0 END) AS DigitalJobs,
            SUM(CASE WHEN jt.StageID IN (12,13,14,15) THEN 1 ELSE 0 END) AS SignageJobs,
            SUM(CASE WHEN jt.StageID = 8 THEN 1 ELSE 0 END) AS BinderyJobs,
            -- Capacity indicator (based on historical averages)
            CASE 
                WHEN COUNT(jt.TicketID) > 15 THEN 'OVERBOOKED'
                WHEN COUNT(jt.TicketID) > 10 THEN 'BUSY'
                ELSE 'NORMAL'
            END AS CapacityStatus
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE o.DateRequired BETWEEN CAST(GETDATE() AS DATE) 
                AND DATEADD(DAY, {days_ahead}, GETDATE())
            AND jt.StageID NOT IN (9, 10)
        GROUP BY o.DateRequired
        ORDER BY o.DateRequired
        """

    def _sql_urgency_level_distribution(self, params: Dict[str, Any]) -> str:
        """Generate SQL for urgency distribution analysis"""
        days = params['days']
        return f"""
        SELECT 
            cs.ColourDesc AS UrgencyLevel,
            cs.OrderPriority AS Priority,
            COUNT(jt.TicketID) AS JobCount,
            SUM(jt.Cost) AS TotalValue,
            AVG(jt.Cost) AS AvgJobValue,
            CAST(COUNT(jt.TicketID) * 100.0 / 
                 SUM(COUNT(jt.TicketID)) OVER() AS DECIMAL(5,2)) AS PercentOfJobs
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
        WHERE o.OrderDate >= DATEADD(DAY, -{days}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY cs.ColourDesc, cs.OrderPriority
        HAVING COUNT(jt.TicketID) > 0
        ORDER BY cs.OrderPriority
        """

    def _sql_job_complexity_analysis(self, params: Dict[str, Any]) -> str:
        """Generate SQL for job complexity scoring"""
        months = params['months']
        return f"""
        SELECT 
            jtype.[Desc] AS ProductType,
            COUNT(jt.TicketID) AS JobCount,
            AVG(jt.Cost) AS AvgJobValue,
            AVG(jt.QTY) AS AvgQuantity,
            -- Complexity score formula
            (AVG(jt.Cost) * AVG(jt.QTY)) / 1000 AS ComplexityScore,
            AVG(DATEDIFF(DAY, o.OrderDate, 
                COALESCE(o.InvoiceDate, GETDATE()))) AS AvgTurnaroundDays
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            AND jt.QTY IS NOT NULL
        GROUP BY jtype.[Desc]
        HAVING COUNT(jt.TicketID) >= 5  -- Minimum sample size
        ORDER BY ComplexityScore DESC
        """

    # ============================================================================
    # PRODUCTION PLANNING SQL METHODS (NEW - COMPREHENSIVE)
    # ============================================================================
    
    def _sql_daily_production_plan(self, params: Dict[str, Any]) -> str:
        """Generate SQL for daily production planning report"""
        days_ahead = params['days_ahead']
        min_ticket_id = params['min_ticket_id']
        stages = params['stages']
        
        return f"""
        -- ============================================================================
        -- DAILY PRODUCTION PLANNING QUERY
        -- ============================================================================
        -- Purpose: Generate actionable daily production plan for digital workflow
        -- Focus: Jobs due today + next {days_ahead} days, sorted by priority and stage
        -- Performance: Uses ticket ID range instead of InternalInvoiceComplete flag
        -- ============================================================================

        WITH ActiveJobs AS (
            -- Get all active jobs with full specifications
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
                
                -- Job specifications
                ISNULL(jtype.[Desc], 'Unknown') as JobType,
                ISNULL(pt.[Desc], '') as PaperType,
                ISNULL(gsm.[DESC], '') as GSM,
                ISNULL(ps.[Desc], '') as PaperSize,
                ISNULL(jt.Pages, 0) as Pages,
                
                -- Finishing flags for time estimates
                CASE 
                    WHEN (jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                          jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1) THEN 1
                    ELSE 0
                END as HasCello,
                
                CASE 
                    WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' THEN 1
                    ELSE 0
                END as HasFolding,
                
                ISNULL(jt.StitchYes, 0) as HasStitching,
                ISNULL(jt.RingBind, 0) as HasRingBind,
                ISNULL(jt.PerfectBind, 0) as HasPerfectBind,
                
                -- Production notes
                ISNULL(jt.TicketNotes, '') as ProductionNotes,
                
                -- Shipping
                ISNULL(st.ShippingDesc, 'N/A') as ShippingDesc,
                
                -- Urgency from ColourStatus
                ISNULL(cs.ColourValue, '#FFFFFF') as UrgencyColor,
                ISNULL(cs.ColourDesc, 'Not Set') as UrgencyDescription,
                ISNULL(cs.OrderPriority, 999) as UrgencyPriority,
                
                -- Date calculations
                DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
                DATEDIFF(day, o.OrderDate, GETDATE()) as DaysInSystem,
                
                -- Customer metrics for tier
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
            
            -- Lookup table JOINs
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
            LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
            LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
            LEFT JOIN ShippingType st ON o.ShippingType = st.ShippingID
            LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
            
            WHERE 
                -- Performance optimization: Use ticket ID instead of InternalInvoiceComplete
                jt.TicketID >= {min_ticket_id}
                
                -- Focus on digital production stages
                AND jt.StageID IN ({stages})
                
                -- Exclude completed stage
                AND jt.StageID != 10
                
                -- Focus on jobs due soon
                AND o.DateRequired <= DATEADD(day, {days_ahead}, GETDATE())
        ),

        ProductionEstimates AS (
            -- Calculate production time estimates
            SELECT 
                *,
                
                -- Base production time (hours) based on job type and quantity
                CASE 
                    -- Business Cards: ~500 per hour
                    WHEN JobType LIKE '%Business Card%' THEN (QTY / 500.0)
                    
                    -- Flyers/Leaflets: ~1000 per hour (single-sided), ~600 per hour (double-sided)
                    WHEN JobType LIKE '%Flyer%' OR JobType LIKE '%Leaflet%' THEN 
                        CASE 
                            WHEN JobType LIKE '%Double%' THEN (QTY / 600.0)
                            ELSE (QTY / 1000.0)
                        END
                    
                    -- Books: ~20 per hour (complex), ~40 per hour (simple)
                    WHEN JobType LIKE '%Book%' OR JobType LIKE '%Booklet%' THEN 
                        CASE 
                            WHEN HasPerfectBind = 1 THEN (QTY / 20.0)
                            WHEN HasStitching = 1 THEN (QTY / 40.0)
                            ELSE (QTY / 30.0)
                        END
                    
                    -- Custom/Other: estimate based on quantity
                    ELSE (QTY / 500.0)
                END 
                +
                -- Add finishing time
                (CASE WHEN HasCello = 1 THEN (QTY / 1000.0) ELSE 0 END) +  -- Cello: ~1000/hour
                (CASE WHEN HasFolding = 1 THEN (QTY / 800.0) ELSE 0 END) +  -- Folding: ~800/hour
                (CASE WHEN HasStitching = 1 THEN (QTY / 600.0) ELSE 0 END)  -- Stitching: ~600/hour
                
                AS EstimatedHours,
                
                -- Priority Score (0-999)
                (
                    -- Due date urgency (0-400)
                    CASE 
                        WHEN DaysUntilDue < 0 THEN 400  -- Overdue
                        WHEN DaysUntilDue = 0 THEN 350  -- Due today
                        WHEN DaysUntilDue = 1 THEN 300  -- Due tomorrow
                        WHEN DaysUntilDue = 2 THEN 200  -- Day after
                        ELSE 100
                    END
                    +
                    -- Job value (0-200)
                    CASE 
                        WHEN Cost >= 2000 THEN 200
                        WHEN Cost >= 1000 THEN 150
                        WHEN Cost >= 500 THEN 100
                        ELSE 50
                    END
                    +
                    -- Customer tier (0-200)
                    CASE 
                        WHEN CustomerOrderCount >= 50 THEN 200  -- VIP
                        WHEN CustomerOrderCount >= 20 THEN 150  -- Premium
                        WHEN CustomerOrderCount >= 5 THEN 100   -- Regular
                        ELSE 50  -- New
                    END
                    +
                    -- Urgency priority from ColourStatus (0-150)
                    CASE 
                        WHEN UrgencyPriority <= 1 THEN 150  -- "Before Lunch" urgency
                        WHEN UrgencyPriority <= 3 THEN 100  -- "Before COB" urgency
                        WHEN UrgencyPriority <= 5 THEN 50   -- "48 Hour" urgency
                        ELSE 0
                    END
                    +
                    -- Days in system penalty (0-50)
                    CASE 
                        WHEN DaysInSystem > 14 THEN 50
                        WHEN DaysInSystem > 7 THEN 25
                        ELSE 0
                    END
                ) AS PriorityScore
                
            FROM ActiveJobs
        )

        -- Final output with priority bands
        SELECT 
            TicketID,
            OrderID,
            ClientName,
            QTY,
            JobType,
            ShortJobDesc,
            StageID,
            StageDescription,
            Cost,
            DaysUntilDue,
            CONVERT(VARCHAR(10), DateRequired, 120) as DueDate,
            
            -- Urgency levels
            CASE 
                WHEN DaysUntilDue < 0 THEN 'OVERDUE'
                WHEN DaysUntilDue = 0 THEN 'DUE TODAY'
                WHEN DaysUntilDue = 1 THEN 'DUE TOMORROW'
                WHEN DaysUntilDue = 2 THEN 'DUE IN 2 DAYS'
                ELSE 'FUTURE'
            END as UrgencyLevel,
            
            UrgencyColor,
            UrgencyDescription,
            ShippingDesc,
            ProductionNotes,
            
            -- Production planning data
            ROUND(EstimatedHours, 2) as EstimatedHours,
            PriorityScore,
            
            CASE 
                WHEN PriorityScore >= 800 THEN 'CRITICAL'
                WHEN PriorityScore >= 600 THEN 'HIGH'
                WHEN PriorityScore >= 400 THEN 'MEDIUM'
                WHEN PriorityScore >= 200 THEN 'NORMAL'
                ELSE 'LOW'
            END as PriorityBand,
            
            -- Customer tier
            CASE 
                WHEN CustomerOrderCount >= 50 THEN 'VIP'
                WHEN CustomerOrderCount >= 20 THEN 'Premium'
                WHEN CustomerOrderCount >= 5 THEN 'Regular'
                ELSE 'New'
            END as CustomerTier,
            
            CONVERT(VARCHAR(10), OrderDate, 120) as OrderDate,
            DaysInSystem

        FROM ProductionEstimates

        -- Sort by priority for production planning
        ORDER BY 
            PriorityScore DESC,
            DaysUntilDue ASC,
            StageID ASC
        """

    def _sql_stage_capacity_report(self, params: Dict[str, Any]) -> str:
        """Generate SQL for stage capacity analysis"""
        min_ticket_id = params['min_ticket_id']
        work_hours_per_day = params['work_hours_per_day']
        stages = params['stages']
        
        return f"""
        -- ============================================================================
        -- STAGE CAPACITY REPORT
        -- ============================================================================
        -- Purpose: Show production capacity vs demand for each stage
        -- Identifies: Overloaded stages, available capacity, bottlenecks
        -- ============================================================================

        WITH StageJobs AS (
            -- Get all active jobs with time estimates
            SELECT 
                jt.TicketID,
                jt.StageID,
                js.[Desc] as StageDescription,
                o.ClientName,
                jt.QTY,
                ISNULL(jtype.[Desc], 'Unknown') as JobType,
                jt.ShortJobDesc,
                CAST(jt.Cost as DECIMAL(10,2)) as Cost,
                DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
                
                -- Finishing flags
                CASE 
                    WHEN (jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                          jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1) THEN 1
                    ELSE 0
                END as HasCello,
                
                CASE 
                    WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' THEN 1
                    ELSE 0
                END as HasFolding,
                
                ISNULL(jt.StitchYes, 0) as HasStitching,
                ISNULL(jt.PerfectBind, 0) as HasPerfectBind,
                
                -- Urgency priority
                ISNULL(cs.OrderPriority, 999) as UrgencyPriority,
                
                -- Calculate production time (hours)
                CASE 
                    -- Business Cards: ~500 per hour
                    WHEN jtype.[Desc] LIKE '%Business Card%' THEN (jt.QTY / 500.0)
                    
                    -- Flyers: ~600-1000 per hour
                    WHEN jtype.[Desc] LIKE '%Flyer%' OR jtype.[Desc] LIKE '%Leaflet%' THEN 
                        CASE 
                            WHEN jtype.[Desc] LIKE '%Double%' THEN (jt.QTY / 600.0)
                            ELSE (jt.QTY / 1000.0)
                        END
                    
                    -- Books: ~20-40 per hour
                    WHEN jtype.[Desc] LIKE '%Book%' OR jtype.[Desc] LIKE '%Booklet%' THEN 
                        CASE 
                            WHEN jt.PerfectBind = 1 THEN (jt.QTY / 20.0)
                            WHEN jt.StitchYes = 1 THEN (jt.QTY / 40.0)
                            ELSE (jt.QTY / 30.0)
                        END
                    
                    -- Custom/Other
                    ELSE (jt.QTY / 500.0)
                END 
                +
                -- Add finishing time
                (CASE WHEN jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                           jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1 
                      THEN (jt.QTY / 1000.0) ELSE 0 END) +
                (CASE WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' 
                      THEN (jt.QTY / 800.0) ELSE 0 END) +
                (CASE WHEN jt.StitchYes = 1 THEN (jt.QTY / 600.0) ELSE 0 END)
                
                AS EstimatedHours,
                
                -- Priority score for ranking
                (
                    CASE 
                        WHEN DATEDIFF(day, GETDATE(), o.DateRequired) < 0 THEN 400
                        WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 0 THEN 350
                        WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 1 THEN 300
                        ELSE 100
                    END
                    +
                    CASE 
                        WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 2000 THEN 200
                        WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 1000 THEN 150
                        ELSE 50
                    END
                    +
                    CASE 
                        WHEN cs.OrderPriority <= 1 THEN 150
                        WHEN cs.OrderPriority <= 3 THEN 100
                        ELSE 0
                    END
                ) AS PriorityScore
                
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            INNER JOIN JobStage js ON jt.StageID = js.StageID
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
            
            WHERE 
                jt.TicketID >= {min_ticket_id}
                AND jt.StageID IN ({stages})
                AND jt.StageID != 10  -- Exclude completed
                AND o.DateRequired <= DATEADD(day, 7, GETDATE())  -- Next week only
        ),

        StageCapacity AS (
            -- Aggregate by stage
            SELECT 
                StageID,
                StageDescription,
                COUNT(*) as JobCount,
                SUM(EstimatedHours) as TotalHoursNeeded,
                AVG(EstimatedHours) as AvgHoursPerJob,
                
                -- Urgency breakdown
                COUNT(CASE WHEN DaysUntilDue < 0 THEN 1 END) as JobsOverdue,
                COUNT(CASE WHEN DaysUntilDue = 0 THEN 1 END) as JobsDueToday,
                COUNT(CASE WHEN DaysUntilDue = 1 THEN 1 END) as JobsDueTomorrow,
                
                -- Highest priority job
                MAX(PriorityScore) as HighestPriority
                
            FROM StageJobs
            GROUP BY StageID, StageDescription
        )

        -- Final report with capacity analysis
        SELECT 
            sc.StageID,
            sc.StageDescription,
            sc.JobCount,
            ROUND(sc.TotalHoursNeeded, 1) as TotalHoursNeeded,
            {work_hours_per_day} as HoursAvailableToday,
            
            -- Capacity utilization percentage
            ROUND((sc.TotalHoursNeeded / {work_hours_per_day}) * 100, 0) as CapacityUtilization,
            
            -- Status indicator
            CASE 
                WHEN sc.TotalHoursNeeded > ({work_hours_per_day} * 1.5) THEN 'CRITICAL OVERLOAD'
                WHEN sc.TotalHoursNeeded > {work_hours_per_day} THEN 'OVER CAPACITY'
                WHEN sc.TotalHoursNeeded > ({work_hours_per_day} * 0.8) THEN 'HIGH LOAD'
                WHEN sc.TotalHoursNeeded > ({work_hours_per_day} * 0.5) THEN 'NORMAL'
                ELSE 'LOW LOAD'
            END as Status,
            
            -- Hours over/under capacity
            ROUND(sc.TotalHoursNeeded - {work_hours_per_day}, 1) as HoursOverUnder,
            
            -- Urgency breakdown
            sc.JobsOverdue,
            sc.JobsDueToday,
            sc.JobsDueTomorrow,
            
            ROUND(sc.AvgHoursPerJob, 1) as AvgHoursPerJob,
            sc.HighestPriority as HighestPriorityScore,
            
            -- Get details of highest priority job
            (
                SELECT TOP 1 
                    'T:' + CAST(TicketID AS VARCHAR) + ' - ' + 
                    ClientName + ' (' + CAST(ROUND(EstimatedHours, 1) AS VARCHAR) + 'h)'
                FROM StageJobs sj
                WHERE sj.StageID = sc.StageID
                ORDER BY PriorityScore DESC
            ) as HighestPriorityJob

        FROM StageCapacity sc

        ORDER BY 
            CASE 
                WHEN sc.TotalHoursNeeded > ({work_hours_per_day} * 1.5) THEN 1
                WHEN sc.TotalHoursNeeded > {work_hours_per_day} THEN 2
                WHEN sc.TotalHoursNeeded > ({work_hours_per_day} * 0.8) THEN 3
                ELSE 4
            END,
            sc.TotalHoursNeeded DESC
        """

    def _sql_weekly_production_forecast(self, params: Dict[str, Any]) -> str:
        """Generate SQL for 7-day production forecast"""
        min_ticket_id = params['min_ticket_id']
        stages = params['stages']
        
        return f"""
        -- ============================================================================
        -- WEEKLY PRODUCTION FORECAST (7 DAYS)
        -- ============================================================================
        -- Purpose: Daily breakdown of production workload for next 7 days
        -- Shows: Due dates, hours needed per stage, critical jobs, value
        -- ============================================================================

        WITH DailyJobs AS (
            -- Get all jobs with production estimates
            SELECT 
                jt.TicketID,
                jt.StageID,
                js.[Desc] as StageDescription,
                o.ClientName,
                o.DateRequired,
                CAST(o.DateRequired AS DATE) as DueDate,
                DATEDIFF(day, GETDATE(), o.DateRequired) as DaysFromToday,
                DATENAME(weekday, o.DateRequired) as DayOfWeek,
                
                jt.QTY,
                ISNULL(jtype.[Desc], 'Unknown') as JobType,
                CAST(jt.Cost as DECIMAL(10,2)) as Cost,
                
                ISNULL(cs.ColourDesc, 'Not Set') as UrgencyDescription,
                ISNULL(cs.OrderPriority, 999) as UrgencyPriority,
                
                -- Calculate production time (same formula as before)
                CASE 
                    WHEN jtype.[Desc] LIKE '%Business Card%' THEN (jt.QTY / 500.0)
                    WHEN jtype.[Desc] LIKE '%Flyer%' OR jtype.[Desc] LIKE '%Leaflet%' THEN 
                        CASE 
                            WHEN jtype.[Desc] LIKE '%Double%' THEN (jt.QTY / 600.0)
                            ELSE (jt.QTY / 1000.0)
                        END
                    WHEN jtype.[Desc] LIKE '%Book%' OR jtype.[Desc] LIKE '%Booklet%' THEN 
                        CASE 
                            WHEN jt.PerfectBind = 1 THEN (jt.QTY / 20.0)
                            WHEN jt.StitchYes = 1 THEN (jt.QTY / 40.0)
                            ELSE (jt.QTY / 30.0)
                        END
                    ELSE (jt.QTY / 500.0)
                END 
                +
                (CASE WHEN jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                           jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1 
                      THEN (jt.QTY / 1000.0) ELSE 0 END) +
                (CASE WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' 
                      THEN (jt.QTY / 800.0) ELSE 0 END) +
                (CASE WHEN jt.StitchYes = 1 THEN (jt.QTY / 600.0) ELSE 0 END)
                AS EstimatedHours,
                
                -- Priority classification
                CASE 
                    WHEN DATEDIFF(day, GETDATE(), o.DateRequired) < 0 THEN 'OVERDUE'
                    WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 0 THEN 'DUE TODAY'
                    WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 1 THEN 'DUE TOMORROW'
                    ELSE 'FUTURE'
                END as UrgencyLevel,
                
                -- High value flag
                CASE WHEN CAST(jt.Cost as DECIMAL(10,2)) >= 1000 THEN 1 ELSE 0 END as IsHighValue
                
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            INNER JOIN JobStage js ON jt.StageID = js.StageID
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
            
            WHERE 
                jt.TicketID >= {min_ticket_id}
                AND jt.StageID IN ({stages})
                AND jt.StageID != 10
                AND o.DateRequired >= CAST(GETDATE() AS DATE)  -- Today onwards
                AND o.DateRequired <= DATEADD(day, 7, GETDATE())  -- Next 7 days
        )

        -- Aggregate by due date
        SELECT 
            DueDate,
            DayOfWeek,
            DaysFromToday,
            
            -- Job counts
            COUNT(*) as JobCount,
            COUNT(CASE WHEN UrgencyLevel = 'OVERDUE' THEN 1 END) as OverdueCount,
            
            -- Time estimates
            ROUND(SUM(EstimatedHours), 1) as TotalHoursNeeded,
            ROUND(AVG(EstimatedHours), 1) as AvgHoursPerJob,
            
            -- Value
            SUM(Cost) as TotalValue,
            COUNT(CASE WHEN IsHighValue = 1 THEN 1 END) as HighValueJobs,
            
            -- Stage breakdown
            ROUND(SUM(CASE WHEN StageID = 4 THEN EstimatedHours ELSE 0 END), 1) as Stage4Hours,
            ROUND(SUM(CASE WHEN StageID = 5 THEN EstimatedHours ELSE 0 END), 1) as Stage5Hours,
            ROUND(SUM(CASE WHEN StageID = 7 THEN EstimatedHours ELSE 0 END), 1) as Stage7Hours,
            ROUND(SUM(CASE WHEN StageID = 8 THEN EstimatedHours ELSE 0 END), 1) as Stage8Hours,
            ROUND(SUM(CASE WHEN StageID = 11 THEN EstimatedHours ELSE 0 END), 1) as Stage11Hours,
            
            -- Critical jobs count (high priority or high value)
            COUNT(CASE WHEN UrgencyPriority <= 3 OR IsHighValue = 1 THEN 1 END) as CriticalJobs,
            
            -- Top client by value for that day
            (
                SELECT TOP 1 ClientName
                FROM DailyJobs dj2
                WHERE dj2.DueDate = dj.DueDate
                GROUP BY ClientName
                ORDER BY SUM(Cost) DESC
            ) as TopClient,
            
            -- Workload indicator
            CASE 
                WHEN SUM(EstimatedHours) > 12 THEN 'OVERLOADED'
                WHEN SUM(EstimatedHours) > 8 THEN 'BUSY'
                WHEN SUM(EstimatedHours) > 5 THEN 'NORMAL'
                ELSE 'LIGHT'
            END as WorkloadStatus

        FROM DailyJobs dj

        GROUP BY DueDate, DayOfWeek, DaysFromToday

        ORDER BY DueDate
        """

    def _sql_bottleneck_detection_advanced(self, params: Dict[str, Any]) -> str:
        """Generate SQL for advanced bottleneck detection"""
        min_ticket_id = params['min_ticket_id']
        capacity_threshold = params['capacity_threshold']
        stages = params['stages']
        
        return f"""
        -- ============================================================================
        -- BOTTLENECK DETECTION QUERY
        -- ============================================================================
        -- Purpose: Identify production bottlenecks and recommend actions
        -- Analyzes: Capacity, throughput, dwell time, overdue jobs
        -- ============================================================================

        WITH StageMetrics AS (
            -- Calculate detailed metrics per stage
            SELECT 
                jt.StageID,
                js.[Desc] as StageDescription,
                
                -- Job counts
                COUNT(*) as JobCount,
                COUNT(CASE WHEN DATEDIFF(day, GETDATE(), o.DateRequired) < 0 THEN 1 END) as OverdueJobs,
                COUNT(CASE WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 0 THEN 1 END) as DueTodayJobs,
                COUNT(CASE WHEN DATEDIFF(day, GETDATE(), o.DateRequired) = 1 THEN 1 END) as DueTomorrowJobs,
                
                -- Time metrics
                AVG(DATEDIFF(day, o.OrderDate, GETDATE())) as AvgDaysInStage,
                MAX(DATEDIFF(day, o.OrderDate, GETDATE())) as MaxDaysInStage,
                
                -- Production time needed
                SUM(
                    CASE 
                        WHEN jtype.[Desc] LIKE '%Business Card%' THEN (jt.QTY / 500.0)
                        WHEN jtype.[Desc] LIKE '%Flyer%' OR jtype.[Desc] LIKE '%Leaflet%' THEN 
                            CASE 
                                WHEN jtype.[Desc] LIKE '%Double%' THEN (jt.QTY / 600.0)
                                ELSE (jt.QTY / 1000.0)
                            END
                        WHEN jtype.[Desc] LIKE '%Book%' OR jtype.[Desc] LIKE '%Booklet%' THEN 
                            CASE 
                                WHEN jt.PerfectBind = 1 THEN (jt.QTY / 20.0)
                                WHEN jt.StitchYes = 1 THEN (jt.QTY / 40.0)
                                ELSE (jt.QTY / 30.0)
                            END
                        ELSE (jt.QTY / 500.0)
                    END 
                    +
                    (CASE WHEN jt.FrontCelloMatt = 1 OR jt.FrontCelloGloss = 1 OR 
                               jt.BackCelloMatt = 1 OR jt.BackCelloGloss = 1 
                          THEN (jt.QTY / 1000.0) ELSE 0 END) +
                    (CASE WHEN jt.FoldDesc IS NOT NULL AND jt.FoldDesc != '' 
                          THEN (jt.QTY / 800.0) ELSE 0 END) +
                    (CASE WHEN jt.StitchYes = 1 THEN (jt.QTY / 600.0) ELSE 0 END)
                ) as TotalHoursNeeded,
                
                -- Value metrics
                SUM(CAST(jt.Cost as DECIMAL(10,2))) as TotalValue,
                AVG(CAST(jt.Cost as DECIMAL(10,2))) as AvgJobValue,
                
                -- Priority metrics
                COUNT(CASE WHEN cs.OrderPriority <= 3 THEN 1 END) as HighPriorityJobs,
                
                -- Stage-specific capacity (hours per day)
                CASE 
                    WHEN jt.StageID = 4 THEN 8   -- Digital 9110 (1 machine, 8 hours)
                    WHEN jt.StageID = 5 THEN 16  -- Other Digital (2 machines, 8 hours each)
                    WHEN jt.StageID = 6 THEN 999 -- OutSource (unlimited)
                    WHEN jt.StageID = 7 THEN 6   -- Cello (manual, ~6 hours productive)
                    WHEN jt.StageID = 8 THEN 8   -- Bindery (1 person, 8 hours)
                    WHEN jt.StageID = 11 THEN 999 -- Ready to Print (no capacity limit)
                    ELSE 8
                END as HoursAvailablePerDay
                
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            INNER JOIN JobStage js ON jt.StageID = js.StageID
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
            
            WHERE 
                jt.TicketID >= {min_ticket_id}
                AND jt.StageID IN ({stages})
                AND jt.StageID != 10
                AND o.DateRequired <= DATEADD(day, 7, GETDATE())  -- Next week
            
            GROUP BY jt.StageID, js.[Desc]
        ),

        BottleneckAnalysis AS (
            -- Calculate bottleneck indicators
            SELECT 
                *,
                
                -- Capacity utilization
                CASE 
                    WHEN HoursAvailablePerDay = 999 THEN 0  -- Unlimited capacity
                    ELSE (TotalHoursNeeded / HoursAvailablePerDay)
                END as UtilizationRatio,
                
                -- Bottleneck score (0-100, higher = worse bottleneck)
                (
                    -- Capacity pressure (0-40 points)
                    CASE 
                        WHEN HoursAvailablePerDay = 999 THEN 0
                        WHEN (TotalHoursNeeded / HoursAvailablePerDay) >= 1.5 THEN 40
                        WHEN (TotalHoursNeeded / HoursAvailablePerDay) >= 1.2 THEN 30
                        WHEN (TotalHoursNeeded / HoursAvailablePerDay) >= {capacity_threshold} THEN 20
                        ELSE 0
                    END
                    +
                    -- Overdue pressure (0-30 points)
                    CASE 
                        WHEN OverdueJobs >= 5 THEN 30
                        WHEN OverdueJobs >= 3 THEN 20
                        WHEN OverdueJobs >= 1 THEN 10
                        ELSE 0
                    END
                    +
                    -- Dwell time pressure (0-20 points)
                    CASE 
                        WHEN AvgDaysInStage > 7 THEN 20
                        WHEN AvgDaysInStage > 5 THEN 15
                        WHEN AvgDaysInStage > 3 THEN 10
                        ELSE 0
                    END
                    +
                    -- Urgency pressure (0-10 points)
                    CASE 
                        WHEN (DueTodayJobs + DueTomorrowJobs) >= 5 THEN 10
                        WHEN (DueTodayJobs + DueTomorrowJobs) >= 3 THEN 5
                        ELSE 0
                    END
                ) as BottleneckScore
                
            FROM StageMetrics
        )

        -- Final bottleneck report with recommendations
        SELECT 
            StageID,
            StageDescription,
            
            -- Bottleneck flag
            CASE WHEN BottleneckScore >= 50 THEN 1 ELSE 0 END as IsBottleneck,
            BottleneckScore,
            
            -- Current status
            JobCount,
            ROUND(TotalHoursNeeded, 1) as HoursNeeded,
            HoursAvailablePerDay as HoursAvailable,
            ROUND(UtilizationRatio * 100, 0) as UtilizationPercent,
            
            -- Time metrics
            ROUND(AvgDaysInStage, 1) as AvgDaysInStage,
            MaxDaysInStage,
            
            -- Urgency
            OverdueJobs,
            DueTodayJobs,
            DueTomorrowJobs,
            HighPriorityJobs,
            
            -- Delay risk assessment
            CASE 
                WHEN BottleneckScore >= 70 THEN 'SEVERE - Delays inevitable'
                WHEN BottleneckScore >= 50 THEN 'HIGH - Significant delay risk'
                WHEN BottleneckScore >= 30 THEN 'MEDIUM - Monitor closely'
                WHEN BottleneckScore >= 15 THEN 'LOW - Some pressure'
                ELSE 'MINIMAL - On track'
            END as DelayRisk,
            
            -- Value at risk
            CAST(TotalValue as DECIMAL(10,2)) as ValueAtRisk,
            
            -- Recommended action
            CASE 
                WHEN BottleneckScore >= 70 THEN 
                    'URGENT: Add overtime/outsource immediately. Delay COB due dates. Escalate to management.'
                WHEN BottleneckScore >= 50 THEN 
                    'HIGH: Prioritize critical jobs. Consider overtime. Defer non-urgent work.'
                WHEN BottleneckScore >= 30 THEN 
                    'MEDIUM: Optimize workflow. Batch similar jobs. Monitor overdue items closely.'
                WHEN BottleneckScore >= 15 THEN 
                    'LOW: Continue monitoring. Maintain current pace. Watch for new urgent jobs.'
                ELSE 
                    'GOOD: Capacity available. Can accept new work. Maintain quality focus.'
            END as RecommendedAction,
            
            -- Specific issues
            CASE 
                WHEN OverdueJobs > 0 THEN 'Has ' + CAST(OverdueJobs as VARCHAR) + ' overdue jobs'
                WHEN UtilizationRatio > 1.5 THEN 'Severely over capacity (' + CAST(ROUND(UtilizationRatio * 100, 0) as VARCHAR) + '%)'
                WHEN AvgDaysInStage > 7 THEN 'Jobs dwelling too long (avg ' + CAST(ROUND(AvgDaysInStage, 1) as VARCHAR) + ' days)'
                WHEN DueTodayJobs + DueTomorrowJobs >= 5 THEN 'Many urgent jobs in queue'
                ELSE 'No critical issues'
            END as PrimaryIssue

        FROM BottleneckAnalysis

        ORDER BY BottleneckScore DESC, UtilizationRatio DESC
        """

    def _sql_top_customers_detailed(self, params: Dict[str, Any]) -> str:
        """Generate SQL for detailed top customers"""
        months = params['months']
        top_n = params['top_n']
        return f"""
        WITH CustomerStats AS (
            SELECT 
                o.ClientName,
                SUM(jt.Cost) AS TotalRevenue,
                COUNT(DISTINCT o.OrderID) AS OrderCount,
                COUNT(jt.TicketID) AS JobTicketCount,
                AVG(jt.Cost) AS AvgJobValue,
                MAX(o.OrderDate) AS LastOrderDate,
                DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            GROUP BY o.ClientName
        ),
        TopProducts AS (
            SELECT 
                o.ClientName,
                jtype.[Desc] AS TopProduct,
                ROW_NUMBER() OVER (PARTITION BY o.ClientName 
                                   ORDER BY COUNT(*) DESC) AS ProductRank
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            GROUP BY o.ClientName, jtype.[Desc]
        )
        SELECT TOP {top_n}
            cs.ClientName,
            cs.TotalRevenue,
            cs.OrderCount,
            cs.JobTicketCount,
            cs.AvgJobValue,
            cs.LastOrderDate,
            cs.DaysSinceLastOrder,
            tp.TopProduct
        FROM CustomerStats cs
        LEFT JOIN TopProducts tp ON cs.ClientName = tp.ClientName 
            AND tp.ProductRank = 1
        ORDER BY cs.TotalRevenue DESC
        """

    def _sql_customer_product_preferences(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer product preferences"""
        months = params['months']
        customer_name = params.get('customer_name')
        customer_filter = ""
        if customer_name:
            customer_filter = f"AND o.ClientName LIKE '%{customer_name}%'"
        
        return f"""
        SELECT 
            o.ClientName,
            jtype.[Desc] AS ProductType,
            COUNT(jt.TicketID) AS OrderCount,
            SUM(jt.QTY) AS TotalQuantity,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgPrice,
            MAX(o.OrderDate) AS LastOrderDate,
            -- Specifications summary
            STRING_AGG(DISTINCT ps.[Desc], ', ') AS CommonSizes,
            STRING_AGG(DISTINCT pt.[Desc], ', ') AS CommonPapers
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            {customer_filter}
        GROUP BY o.ClientName, jtype.[Desc]
        HAVING COUNT(jt.TicketID) >= 2  -- At least 2 orders
        ORDER BY o.ClientName, TotalRevenue DESC
        """

    def _sql_product_turnaround_benchmarks(self, params: Dict[str, Any]) -> str:
        """Generate SQL for product turnaround benchmarks"""
        months = params['months']
        return f"""
        SELECT 
            jtype.[Desc] AS ProductType,
            COUNT(jt.TicketID) AS JobCount,
            AVG(DATEDIFF(DAY, o.OrderDate, 
                COALESCE(o.InvoiceDate, GETDATE()))) AS AvgDays,
            MIN(DATEDIFF(DAY, o.OrderDate, 
                COALESCE(o.InvoiceDate, GETDATE()))) AS MinDays,
            MAX(DATEDIFF(DAY, o.OrderDate, 
                COALESCE(o.InvoiceDate, GETDATE()))) AS MaxDays,
            -- Complexity indicator
            (AVG(jt.Cost) * AVG(jt.QTY)) / 1000 AS ComplexityScore
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            AND o.InvoiceDate IS NOT NULL  -- Only completed jobs
        GROUP BY jtype.[Desc]
        HAVING COUNT(jt.TicketID) >= 10  -- Minimum sample
        ORDER BY AvgDays DESC
        """

    def _sql_high_value_jobs_list(self, params: Dict[str, Any]) -> str:
        """Generate SQL for high-value jobs list"""
        months = params['months']
        min_value = params['min_value']
        return f"""
        SELECT TOP 50
            o.ClientName,
            jt.ShortJobDesc AS JobDescription,
            jt.Cost AS JobValue,
            jt.QTY AS Quantity,
            o.OrderDate,
            jtype.[Desc] AS ProductType,
            ps.[Desc] AS PaperSize,
            pt.[Desc] AS PaperType,
            gsm.[DESC] AS GSM,
            bt.BindTypeDesc AS BindType,
            jt.TicketNotes AS ProductionNotes
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        INNER JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost >= {min_value}
        ORDER BY jt.Cost DESC
        """

    def _sql_binding_finishing_analysis(self, params: Dict[str, Any]) -> str:
        """Generate SQL for binding and finishing analysis"""
        months = params['months']
        return f"""
        SELECT 
            bt.BindTypeDesc AS BindType,
            COUNT(jt.TicketID) AS JobCount,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgJobValue,
            AVG(jt.Pages) AS AvgPages
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            AND bt.BindTypeDesc IS NOT NULL
        GROUP BY bt.BindTypeDesc
        ORDER BY TotalRevenue DESC
        """

    def _sql_monthly_revenue_trend(self, params: Dict[str, Any]) -> str:
        """Generate SQL for monthly revenue trend"""
        months = params['months']
        return f"""
        SELECT 
            FORMAT(o.OrderDate, 'yyyy-MM') AS YearMonth,
            YEAR(o.OrderDate) AS Year,
            MONTH(o.OrderDate) AS Month,
            SUM(jt.Cost) AS TotalRevenue,
            COUNT(DISTINCT o.OrderID) AS OrderCount,
            COUNT(jt.TicketID) AS JobTicketCount,
            AVG(jt.Cost) AS AvgJobValue,
            SUM(jt.QTY) AS UnitsProduced
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY FORMAT(o.OrderDate, 'yyyy-MM'), YEAR(o.OrderDate), MONTH(o.OrderDate)
        ORDER BY Year DESC, Month DESC
        """

    def _sql_day_of_week_patterns(self, params: Dict[str, Any]) -> str:
        """Generate SQL for day of week patterns"""
        weeks = params['weeks']
        return f"""
        SELECT 
            DATENAME(WEEKDAY, o.OrderDate) AS DayOfWeek,
            DATEPART(WEEKDAY, o.OrderDate) AS DayNumber,
            COUNT(DISTINCT o.OrderID) AS TotalOrders,
            COUNT(jt.TicketID) AS TotalJobTickets,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Cost) AS AvgJobValue,
            -- Product type breakdown
            SUM(CASE WHEN jtype.[Desc] LIKE '%Flyer%' THEN 1 ELSE 0 END) AS FlyerCount,
            SUM(CASE WHEN jtype.[Desc] LIKE '%Book%' OR jtype.[Desc] LIKE '%Bound%' 
                     THEN 1 ELSE 0 END) AS BookCount,
            SUM(CASE WHEN jtype.[Desc] LIKE '%Corflute%' OR jtype.[Desc] LIKE '%Sign%' 
                     THEN 1 ELSE 0 END) AS SignageCount
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(WEEK, -{weeks}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY DATENAME(WEEKDAY, o.OrderDate), DATEPART(WEEKDAY, o.OrderDate)
        ORDER BY DayNumber
        """

    def _sql_quarterly_performance(self, params: Dict[str, Any]) -> str:
        """Generate SQL for quarterly performance"""
        quarters = params['quarters']
        months_back = quarters * 3
        return f"""
        WITH QuarterlyData AS (
            SELECT 
                YEAR(o.OrderDate) AS Year,
                DATEPART(QUARTER, o.OrderDate) AS Quarter,
                SUM(jt.Cost) AS TotalRevenue,
                COUNT(DISTINCT o.OrderID) AS OrderCount,
                AVG(jt.Cost) AS AvgOrderValue
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months_back}, GETDATE())
                AND jt.Cost IS NOT NULL
            GROUP BY YEAR(o.OrderDate), DATEPART(QUARTER, o.OrderDate)
        )
        SELECT 
            'Q' + CAST(Quarter AS VARCHAR) + ' ' + CAST(Year AS VARCHAR) AS Quarter,
            Year,
            Quarter AS QuarterNum,
            TotalRevenue,
            OrderCount,
            AvgOrderValue,
            -- Growth rate vs previous quarter
            CAST((TotalRevenue - LAG(TotalRevenue) OVER (ORDER BY Year, Quarter)) * 100.0 / 
                 NULLIF(LAG(TotalRevenue) OVER (ORDER BY Year, Quarter), 0) 
                 AS DECIMAL(10,2)) AS GrowthRate
        FROM QuarterlyData
        ORDER BY Year DESC, Quarter DESC
        """
    
    # ============================================
    # PERFORMANCE & SLA SQL GENERATORS (NEW)
    # ============================================
    
    def _sql_on_time_delivery_rate(self, params: Dict[str, Any]) -> str:
        """Generate SQL for on-time delivery rate tracking"""
        months = params['months']
        return f"""
        SELECT 
            FORMAT(o.OrderDate, 'yyyy-MM') AS Month,
            COUNT(*) AS TotalOrders,
            SUM(CASE WHEN o.InvoiceDate <= o.DateRequired THEN 1 ELSE 0 END) AS OnTimeOrders,
            CAST(SUM(CASE WHEN o.InvoiceDate <= o.DateRequired THEN 1 ELSE 0 END) * 100.0 / 
                 COUNT(*) AS DECIMAL(5,2)) AS OnTimePercentage,
            AVG(DATEDIFF(DAY, o.DateRequired, o.InvoiceDate)) AS AvgDaysLateOrEarly,
            -- Additional metrics
            SUM(CASE WHEN o.InvoiceDate > o.DateRequired THEN 1 ELSE 0 END) AS LateOrders,
            SUM(CASE WHEN o.InvoiceDate < o.DateRequired THEN 1 ELSE 0 END) AS EarlyOrders
        FROM Orders o
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND o.InvoiceDate IS NOT NULL
            AND o.DateRequired IS NOT NULL
            AND o.DateRequired > '2020-01-01'  -- Filter out invalid dates
        GROUP BY FORMAT(o.OrderDate, 'yyyy-MM')
        ORDER BY Month DESC
        """

    def _sql_customer_deadline_realism(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer deadline realism analysis"""
        months = params['months']
        min_orders = params['min_orders']
        return f"""
        SELECT 
            o.ClientName,
            COUNT(*) AS TotalOrders,
            AVG(DATEDIFF(DAY, o.OrderDate, o.DateRequired)) AS AvgLeadTimeDays,
            SUM(CASE WHEN o.InvoiceDate <= o.DateRequired THEN 1 ELSE 0 END) AS MetDeadline,
            CAST(SUM(CASE WHEN o.InvoiceDate <= o.DateRequired THEN 1 ELSE 0 END) * 100.0 / 
                 COUNT(*) AS DECIMAL(5,2)) AS OnTimeRate,
            AVG(DATEDIFF(DAY, o.DateRequired, o.InvoiceDate)) AS AvgDaysLateOrEarly,
            -- Realism Score
            CASE 
                WHEN AVG(DATEDIFF(DAY, o.OrderDate, o.DateRequired)) >= 7 THEN 'Realistic'
                WHEN AVG(DATEDIFF(DAY, o.OrderDate, o.DateRequired)) >= 3 THEN 'Tight'
                WHEN AVG(DATEDIFF(DAY, o.OrderDate, o.DateRequired)) >= 1 THEN 'Rush'
                ELSE 'Unrealistic'
            END AS DeadlineRealism,
            MAX(o.OrderDate) AS LastOrderDate
        FROM Orders o
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND o.InvoiceDate IS NOT NULL
            AND o.DateRequired IS NOT NULL
            AND o.DateRequired > '2020-01-01'
        GROUP BY o.ClientName
        HAVING COUNT(*) >= {min_orders}
        ORDER BY OnTimeRate ASC, AvgLeadTimeDays ASC
        """
    
    # ============================================
    # UPSELL & REVENUE SQL GENERATORS (NEW)
    # ============================================
    
    def _sql_finishing_upsell_analysis(self, params: Dict[str, Any]) -> str:
        """Generate SQL for finishing options upsell analysis"""
        months = params['months']
        return f"""
        SELECT 
            jtype.[Desc] AS ProductType,
            COUNT(*) AS TotalJobs,
            SUM(CASE WHEN jt.CelloYes = 1 THEN 1 ELSE 0 END) AS WithCello,
            SUM(CASE WHEN jt.FoldYes = 1 THEN 1 ELSE 0 END) AS WithFolding,
            SUM(CASE WHEN jt.StitchYes = 1 THEN 1 ELSE 0 END) AS WithStitch,
            -- Cello adoption rate
            CAST(SUM(CASE WHEN jt.CelloYes = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 COUNT(*) AS DECIMAL(5,2)) AS CelloAdoptionRate,
            -- Price impact
            AVG(CASE WHEN jt.CelloYes = 1 THEN jt.Cost END) AS AvgPriceWithCello,
            AVG(CASE WHEN jt.CelloYes = 0 OR jt.CelloYes IS NULL THEN jt.Cost END) AS AvgPriceNoCello,
            AVG(CASE WHEN jt.CelloYes = 1 THEN jt.Cost END) - 
            AVG(CASE WHEN jt.CelloYes = 0 OR jt.CelloYes IS NULL THEN jt.Cost END) AS CelloValueAdd,
            -- Revenue
            SUM(CASE WHEN jt.CelloYes = 1 THEN jt.Cost ELSE 0 END) AS RevenueWithCello
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
        GROUP BY jtype.[Desc]
        HAVING COUNT(*) >= 20  -- Minimum sample size
        ORDER BY CelloAdoptionRate DESC
        """

    def _sql_boolean_flags_summary(self, params: Dict[str, Any]) -> str:
        """Generate SQL for comprehensive boolean flags summary"""
        months = params['months']
        return f"""
        WITH FlagStats AS (
            SELECT 
                'CelloYes' AS FlagName,
                SUM(CASE WHEN jt.CelloYes = 1 THEN 1 ELSE 0 END) AS JobsWithFlag,
                COUNT(*) AS TotalJobs,
                AVG(CASE WHEN jt.CelloYes = 1 THEN jt.Cost END) AS AvgPriceWith,
                AVG(CASE WHEN jt.CelloYes = 0 OR jt.CelloYes IS NULL THEN jt.Cost END) AS AvgPriceWithout,
                SUM(CASE WHEN jt.CelloYes = 1 THEN jt.Cost ELSE 0 END) AS TotalRevenue
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'FrontCelloGloss',
                SUM(CASE WHEN jt.FrontCelloGloss = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.FrontCelloGloss = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.FrontCelloGloss = 0 OR jt.FrontCelloGloss IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.FrontCelloGloss = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'FrontCelloMatt',
                SUM(CASE WHEN jt.FrontCelloMatt = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.FrontCelloMatt = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.FrontCelloMatt = 0 OR jt.FrontCelloMatt IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.FrontCelloMatt = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'FoldYes',
                SUM(CASE WHEN jt.FoldYes = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.FoldYes = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.FoldYes = 0 OR jt.FoldYes IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.FoldYes = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'StitchYes',
                SUM(CASE WHEN jt.StitchYes = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.StitchYes = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.StitchYes = 0 OR jt.StitchYes IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.StitchYes = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'BackCelloMatt',
                SUM(CASE WHEN jt.BackCelloMatt = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.BackCelloMatt = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.BackCelloMatt = 0 OR jt.BackCelloMatt IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.BackCelloMatt = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'BackCelloGloss',
                SUM(CASE WHEN jt.BackCelloGloss = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.BackCelloGloss = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.BackCelloGloss = 0 OR jt.BackCelloGloss IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.BackCelloGloss = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'Books',
                SUM(CASE WHEN jt.Books = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.Books = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.Books = 0 OR jt.Books IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.Books = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'PerfectBind',
                SUM(CASE WHEN jt.PerfectBind = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.PerfectBind = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.PerfectBind = 0 OR jt.PerfectBind IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.PerfectBind = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'RingBind',
                SUM(CASE WHEN jt.RingBind = 1 THEN 1 ELSE 0 END),
                COUNT(*),
                AVG(CASE WHEN jt.RingBind = 1 THEN jt.Cost END),
                AVG(CASE WHEN jt.RingBind = 0 OR jt.RingBind IS NULL THEN jt.Cost END),
                SUM(CASE WHEN jt.RingBind = 1 THEN jt.Cost ELSE 0 END)
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jt.Cost IS NOT NULL
        )
        SELECT 
            FlagName,
            JobsWithFlag,
            CAST(JobsWithFlag * 100.0 / TotalJobs AS DECIMAL(5,2)) AS AdoptionRate,
            AvgPriceWith,
            AvgPriceWithout,
            AvgPriceWith - AvgPriceWithout AS PriceImpact,
            CAST((AvgPriceWith - AvgPriceWithout) * 100.0 / NULLIF(AvgPriceWithout, 0) AS DECIMAL(5,2)) AS PriceImpactPercent,
            TotalRevenue
        FROM FlagStats
        WHERE JobsWithFlag > 0
        ORDER BY AdoptionRate DESC
        """

    def _sql_rush_pricing_impact(self, params: Dict[str, Any]) -> str:
        """Generate SQL for rush pricing impact analysis"""
        months = params['months']
        product_filter = params.get('product_filter')
        
        product_where = ""
        if product_filter:
            product_where = f"AND jtype.[Desc] LIKE '%{product_filter}%'"
        
        return f"""
        SELECT 
            cs.ColourDesc AS UrgencyLevel,
            cs.OrderPriority,
            jtype.[Desc] AS ProductType,
            COUNT(*) AS JobCount,
            AVG(jt.Cost) AS AvgPrice,
            AVG(jt.QTY) AS AvgQuantity,
            -- Price per unit
            AVG(jt.Cost / NULLIF(jt.QTY, 0)) AS AvgPricePerUnit,
            -- Revenue
            SUM(jt.Cost) AS TotalRevenue
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            AND jt.QTY > 0
            {product_where}
        GROUP BY cs.ColourDesc, cs.OrderPriority, jtype.[Desc]
        HAVING COUNT(*) >= 10
        ORDER BY cs.OrderPriority, ProductType
        """

    def _sql_fold_type_analysis(self, params: Dict[str, Any]) -> str:
        """Generate SQL for fold type analysis"""
        months = params['months']
        return f"""
        SELECT 
            jt.FoldDesc,
            COUNT(*) AS JobCount,
            AVG(jt.Cost) AS AvgPrice,
            SUM(jt.Cost) AS TotalRevenue,
            jtype.[Desc] AS CommonProduct,
            AVG(jt.QTY) AS AvgQuantity
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.FoldDesc IS NOT NULL
            AND jt.FoldDesc <> ''
            AND jt.Cost IS NOT NULL
        GROUP BY jt.FoldDesc, jtype.[Desc]
        HAVING COUNT(*) >= 3
        ORDER BY JobCount DESC
        """
    
    # ============================================
    # OPERATIONAL OPTIMIZATION SQL GENERATORS (NEW)
    # ============================================
    
    def _sql_department_workload_balance(self, params: Dict[str, Any]) -> str:
        """Generate SQL for department workload balance"""
        days = params['days']
        return f"""
        SELECT 
            CASE 
                WHEN jt.StageID IN (1,2,3,11) THEN 'Pre-Production'
                WHEN jt.StageID IN (4,5,6,7,8) THEN 'Digital Department'
                WHEN jt.StageID IN (12,13,14,15) THEN 'Signage Department'
                WHEN jt.StageID IN (9,10) THEN 'Complete'
                ELSE 'Unknown'
            END AS Department,
            COUNT(*) AS ActiveJobs,
            SUM(jt.Cost) AS TotalValue,
            AVG(jt.Cost) AS AvgJobValue,
            AVG(DATEDIFF(DAY, o.OrderDate, GETDATE())) AS AvgDaysInDept,
            MIN(o.OrderDate) AS OldestJob,
            MAX(o.OrderDate) AS NewestJob
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE o.OrderDate >= DATEADD(DAY, -{days}, GETDATE())
        GROUP BY 
            CASE 
                WHEN jt.StageID IN (1,2,3,11) THEN 'Pre-Production'
                WHEN jt.StageID IN (4,5,6,7,8) THEN 'Digital Department'
                WHEN jt.StageID IN (12,13,14,15) THEN 'Signage Department'
                WHEN jt.StageID IN (9,10) THEN 'Complete'
                ELSE 'Unknown'
            END
        ORDER BY ActiveJobs DESC
        """

    def _sql_popular_specifications(self, params: Dict[str, Any]) -> str:
        """Generate SQL for popular product specifications"""
        months = params['months']
        product_filter = params.get('product_type')
        min_orders = params['min_orders']
        
        product_where = ""
        if product_filter:
            product_where = f"AND jtype.[Desc] LIKE '%{product_filter}%'"
        
        return f"""
        SELECT TOP 20
            jtype.[Desc] AS ProductType,
            ps.[Desc] AS PaperSize,
            pt.[Desc] AS PaperType,
            gsm.[DESC] AS GSM,
            bt.BindTypeDesc AS BindType,
            COUNT(*) AS OrderCount,
            AVG(jt.Cost) AS AvgPrice,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.QTY) AS AvgQuantity,
            -- Finishing options summary
            SUM(CASE WHEN jt.FrontCelloMatt = 1 THEN 1 ELSE 0 END) AS MattCelloCount,
            SUM(CASE WHEN jt.FrontCelloGloss = 1 THEN 1 ELSE 0 END) AS GlossCelloCount,
            SUM(CASE WHEN jt.FoldYes = 1 THEN 1 ELSE 0 END) AS FoldCount
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Cost IS NOT NULL
            {product_where}
        GROUP BY jtype.[Desc], ps.[Desc], pt.[Desc], gsm.[DESC], bt.BindTypeDesc
        HAVING COUNT(*) >= {min_orders}
        ORDER BY OrderCount DESC
        """
    
    # ============================================
    # CUSTOMER BEHAVIOR SQL GENERATORS (NEW)
    # ============================================
    
    def _sql_customer_reorder_prediction(self, params: Dict[str, Any]) -> str:
        """Generate SQL for customer reorder prediction"""
        days_overdue = params['days_overdue']
        return f"""
        WITH CustomerStats AS (
            SELECT 
                o.ClientName,
                COUNT(DISTINCT o.OrderID) AS TotalOrders,
                MAX(o.OrderDate) AS LastOrderDate,
                MIN(o.OrderDate) AS FirstOrderDate,
                DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder,
                DATEDIFF(DAY, MIN(o.OrderDate), MAX(o.OrderDate)) AS CustomerLifespanDays
            FROM Orders o
            WHERE o.OrderDate >= DATEADD(MONTH, -24, GETDATE())
            GROUP BY o.ClientName
            HAVING COUNT(DISTINCT o.OrderID) >= 3  -- At least 3 orders to establish pattern
        ),
        LastProduct AS (
            SELECT 
                o.ClientName,
                jt.ShortJobDesc AS LastProduct,
                jt.Cost AS LastOrderValue,
                ROW_NUMBER() OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate DESC) AS rn
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        )
        SELECT 
            cs.ClientName,
            cs.LastOrderDate,
            cs.DaysSinceLastOrder,
            cs.TotalOrders,
            -- Average reorder cycle
            CASE 
                WHEN cs.TotalOrders > 1 THEN cs.CustomerLifespanDays / (cs.TotalOrders - 1)
                ELSE NULL
            END AS AvgReorderCycleDays,
            -- Days overdue for reorder
            cs.DaysSinceLastOrder - 
            CASE 
                WHEN cs.TotalOrders > 1 THEN cs.CustomerLifespanDays / (cs.TotalOrders - 1)
                ELSE 0
            END AS DaysOverdue,
            lp.LastProduct,
            lp.LastOrderValue
        FROM CustomerStats cs
        LEFT JOIN LastProduct lp ON cs.ClientName = lp.ClientName AND lp.rn = 1
        WHERE cs.DaysSinceLastOrder - 
              CASE 
                  WHEN cs.TotalOrders > 1 THEN cs.CustomerLifespanDays / (cs.TotalOrders - 1)
                  ELSE 0
              END >= {days_overdue}
        ORDER BY DaysOverdue DESC
        """

    def _sql_customer_reorder_prediction_business(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for business customer reorder prediction
        Identifies commercial business customers (printing, signage, marketing) overdue for reorders.
        Excludes book publishing. Focuses on recent, actionable opportunities.
        """
        top_n = params['top_n']
        min_orders = params['min_orders']
        min_days_since = params['min_days_since']
        max_years_back = params['max_years_back']
        
        return f"""
        WITH CustomerOrderCycle AS (
            SELECT 
                o.ClientName,
                o.OrderDate,
                jt.ShortJobDesc AS LastProduct,
                jt.Cost AS LastOrderValue,
                jtype.[Desc] AS JobType,
                -- Calculate days since last order
                DATEDIFF(DAY, o.OrderDate, GETDATE()) AS DaysSinceLastOrder,
                -- Calculate average days between orders for each customer
                AVG(DATEDIFF(DAY, 
                    LAG(o.OrderDate) OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate),
                    o.OrderDate
                )) AS AvgDaysBetweenOrders,
                COUNT(*) OVER (PARTITION BY o.ClientName) AS TotalOrders,
                ROW_NUMBER() OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate DESC) AS OrderRank
            FROM JobTickets jt
            JOIN Orders o ON jt.OrderID = o.OrderID
            JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            WHERE 
                -- RECENCY FILTER: Only recent orders
                o.OrderDate >= DATEADD(YEAR, -{max_years_back}, GETDATE())
                -- FILTER FOR COMMERCIAL BUSINESS PRODUCTS ONLY
                AND jtype.[Desc] IN (
                    'Flyers - Double Sided',
                    'Flyers - Single Side', 
                    'Corflute',
                    'Business Cards - Double Sided',
                    'Business Cards - Single Side',
                    'Stickers - Wide Format',
                    'Stickers - Digital Print',
                    'Poster',
                    'PVC Display Sign',
                    'Screenboard',
                    'Pull Up Banner',
                    'Display Sign',
                    'Banner',
                    'ACM Panel',
                    'Pads - Single Side',
                    'NCR BOOKS',
                    'A Frame',
                    'Strut Card',
                    'Fridge Magnets',
                    'Saddle Stitched Book'
                )
                -- EXCLUDE BOOK PUBLISHING PRODUCTS
                AND jtype.[Desc] NOT IN (
                    'Perfect Bound Books',
                    'Casebound/Hardcover',
                    'Spiral Bound Book'
                )
                -- Only customers with at least minimum order count
                AND o.ClientName IN (
                    SELECT ClientName 
                    FROM Orders o2
                    JOIN JobTickets jt2 ON o2.OrderID = jt2.OrderID
                    JOIN JobType jt_filter ON jt2.JobTypeID = jt_filter.JobTypeID
                    WHERE o2.OrderDate >= DATEADD(YEAR, -{max_years_back}, GETDATE())
                      AND jt_filter.[Desc] IN (
                        'Flyers - Double Sided', 'Flyers - Single Side', 'Corflute',
                        'Business Cards - Double Sided', 'Business Cards - Single Side',
                        'Stickers - Wide Format', 'Stickers - Digital Print', 'Poster',
                        'PVC Display Sign', 'Screenboard', 'Pull Up Banner', 'Display Sign',
                        'Banner', 'ACM Panel', 'Pads - Single Side', 'NCR BOOKS',
                        'A Frame', 'Strut Card', 'Fridge Magnets', 'Saddle Stitched Book'
                    )
                    GROUP BY ClientName
                    HAVING COUNT(DISTINCT o2.OrderID) >= {min_orders}
                )
        )
        SELECT TOP ({top_n})
            ClientName,
            CONVERT(DATE, OrderDate) AS LastOrderDate,
            DaysSinceLastOrder,
            CAST(AvgDaysBetweenOrders AS INT) AS AvgOrderCycle,
            CAST((DaysSinceLastOrder - AvgDaysBetweenOrders) AS INT) AS DaysOverdue,
            LastProduct,
            CAST(LastOrderValue AS DECIMAL(10,2)) AS LastOrderValue,
            TotalOrders,
            JobType
        FROM CustomerOrderCycle
        WHERE 
            OrderRank = 1  -- Most recent order only
            AND AvgDaysBetweenOrders IS NOT NULL
            AND DaysSinceLastOrder > AvgDaysBetweenOrders  -- Overdue for reorder
            AND DaysSinceLastOrder >= {min_days_since}  -- Minimum days threshold
        ORDER BY (DaysSinceLastOrder - AvgDaysBetweenOrders) DESC
        """

    def _sql_customer_reorder_prediction_publishing(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for publishing customer reorder prediction
        Identifies book publishing customers (authors, publishers) overdue for book reprints.
        Focuses on Perfect Bound, Spiral Bound, and Casebound products.
        """
        top_n = params['top_n']
        min_orders = params['min_orders']
        min_days_since = params['min_days_since']
        max_years_back = params['max_years_back']
        
        return f"""
        WITH PublishingOrderCycle AS (
            SELECT 
                o.ClientName,
                o.OrderDate,
                jt.ShortJobDesc AS LastProduct,
                jt.Cost AS LastOrderValue,
                jtype.[Desc] AS JobType,
                jt.Pages,
                jt.QTY AS Quantity,
                -- Calculate days since last order
                DATEDIFF(DAY, o.OrderDate, GETDATE()) AS DaysSinceLastOrder,
                -- Calculate average days between orders (book reprints)
                AVG(DATEDIFF(DAY, 
                    LAG(o.OrderDate) OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate),
                    o.OrderDate
                )) AS AvgDaysBetweenOrders,
                COUNT(*) OVER (PARTITION BY o.ClientName) AS TotalPrintRuns,
                ROW_NUMBER() OVER (PARTITION BY o.ClientName ORDER BY o.OrderDate DESC) AS OrderRank
            FROM JobTickets jt
            JOIN Orders o ON jt.OrderID = o.OrderID
            JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            WHERE 
                -- RECENCY FILTER: Books have longer cycles
                o.OrderDate >= DATEADD(YEAR, -{max_years_back}, GETDATE())
                -- FILTER FOR BOOK PUBLISHING PRODUCTS ONLY
                AND (jtype.[Desc] IN (
                    'Perfect Bound Books',
                    'Casebound/Hardcover',
                    'Spiral Bound Book',
                    'Wire Bound Book'
                )
                OR (jtype.[Desc] = 'booklet' AND jt.Pages > 32)) -- Large booklets are likely books
                -- Only customers with at least minimum order count (reprints!)
                AND o.ClientName IN (
                    SELECT ClientName 
                    FROM Orders o2
                    JOIN JobTickets jt2 ON o2.OrderID = jt2.OrderID
                    JOIN JobType jt_filter ON jt2.JobTypeID = jt_filter.JobTypeID
                    WHERE o2.OrderDate >= DATEADD(YEAR, -{max_years_back}, GETDATE())
                      AND (jt_filter.[Desc] IN ('Perfect Bound Books', 'Casebound/Hardcover', 'Spiral Bound Book', 'Wire Bound Book')
                           OR (jt_filter.[Desc] = 'booklet' AND jt2.Pages > 32))
                    GROUP BY ClientName
                    HAVING COUNT(DISTINCT o2.OrderID) >= {min_orders}
                )
        )
        SELECT TOP ({top_n})
            ClientName,
            CONVERT(DATE, OrderDate) AS LastOrderDate,
            DaysSinceLastOrder,
            CAST(AvgDaysBetweenOrders AS INT) AS AvgReprintCycle,
            CAST((DaysSinceLastOrder - AvgDaysBetweenOrders) AS INT) AS DaysOverdue,
            LastProduct,
            CAST(LastOrderValue AS DECIMAL(10,2)) AS LastOrderValue,
            Pages,
            Quantity AS LastQuantity,
            TotalPrintRuns,
            JobType
        FROM PublishingOrderCycle
        WHERE 
            OrderRank = 1  -- Most recent order only
            AND AvgDaysBetweenOrders IS NOT NULL
            AND DaysSinceLastOrder > AvgDaysBetweenOrders  -- Overdue for reprint
            AND DaysSinceLastOrder >= {min_days_since}  -- Minimum days threshold
        ORDER BY (DaysSinceLastOrder - AvgDaysBetweenOrders) DESC
        """

    def _sql_reorder_opportunities_by_product(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for product-specific reorder opportunities
        Identifies customers overdue for reorders of specific product types.
        Enables targeted product-specific campaigns.
        """
        product_type = params.get('product_type')
        top_n = params['top_n']
        min_orders = params['min_orders']
        min_days_since = params['min_days_since']
        max_years_back = params['max_years_back']
        sort_by = params['sort_by']
        
        # Build product filter clause
        product_filter = ""
        if product_type:
            product_filter = f"AND (jtype.[Desc] = '{product_type}' OR '{product_type}' IS NULL)"
        else:
            product_filter = "AND (jtype.[Desc] = @product_type OR @product_type IS NULL)"
        
        # Build sort clause
        sort_clause = "(DaysSinceLastOrder - AvgDaysBetweenOrders)"
        if sort_by == 'value':
            sort_clause = "LastOrderValue"
        elif sort_by == 'frequency':
            sort_clause = "TotalOrders"
        
        return f"""
        WITH ProductOrderCycle AS (
            SELECT 
                o.ClientName,
                jtype.[Desc] AS ProductType,
                MAX(o.OrderDate) AS LastOrderDate,
                COUNT(DISTINCT o.OrderID) AS TotalOrders,
                AVG(jt.Cost) AS AvgOrderValue,
                MAX(jt.Cost) AS LastOrderValue,
                MAX(jt.ShortJobDesc) AS LastProductSpec,
                -- Calculate days since last order for this product type
                DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder,
                -- Calculate average days between orders for this product type
                AVG(DATEDIFF(DAY, 
                    LAG(o.OrderDate) OVER (PARTITION BY o.ClientName, jtype.[Desc] ORDER BY o.OrderDate),
                    o.OrderDate
                )) AS AvgDaysBetweenOrders
            FROM JobTickets jt
            JOIN Orders o ON jt.OrderID = o.OrderID
            JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            WHERE 
                -- RECENCY FILTER
                o.OrderDate >= DATEADD(YEAR, -{max_years_back}, GETDATE())
                -- PRODUCT FILTER (if specified)
                {product_filter}
            GROUP BY o.ClientName, jtype.[Desc]
            HAVING COUNT(DISTINCT o.OrderID) >= {min_orders}
        )
        SELECT TOP ({top_n})
            ClientName,
            ProductType,
            CONVERT(DATE, LastOrderDate) AS LastOrderDate,
            DaysSinceLastOrder,
            CAST(AvgDaysBetweenOrders AS INT) AS TypicalReorderCycle,
            CAST((DaysSinceLastOrder - AvgDaysBetweenOrders) AS INT) AS DaysOverdue,
            TotalOrders,
            CAST(AvgOrderValue AS DECIMAL(10,2)) AS AvgOrderValue,
            CAST(LastOrderValue AS DECIMAL(10,2)) AS LastOrderValue,
            LastProductSpec
        FROM ProductOrderCycle
        WHERE AvgDaysBetweenOrders IS NOT NULL
          AND DaysSinceLastOrder > AvgDaysBetweenOrders
          AND DaysSinceLastOrder >= {min_days_since}
        ORDER BY {sort_clause} DESC
        """

    def _sql_product_bundle_opportunities(self, params: Dict[str, Any]) -> str:
        """Generate SQL for product bundle cross-sell opportunities"""
        months = params['months']
        min_co_occurrence = params['min_co_occurrence']
        return f"""
        WITH CustomerProducts AS (
            SELECT DISTINCT
                o.ClientName,
                jtype.[Desc] AS ProductType
            FROM Orders o
            INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
            LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND jtype.[Desc] IS NOT NULL
        )
        SELECT 
            cp1.ProductType AS Product1,
            cp2.ProductType AS Product2,
            COUNT(DISTINCT cp1.ClientName) AS CoOccurrences,
            COUNT(DISTINCT cp1.ClientName) AS UniqueCustomers,
            CAST(COUNT(DISTINCT cp1.ClientName) * 100.0 / 
                 (SELECT COUNT(DISTINCT ClientName) FROM CustomerProducts WHERE ProductType = cp1.ProductType) 
                 AS DECIMAL(5,2)) AS CrossSellRate
        FROM CustomerProducts cp1
        INNER JOIN CustomerProducts cp2 
            ON cp1.ClientName = cp2.ClientName 
            AND cp1.ProductType < cp2.ProductType  -- Avoid duplicates
        GROUP BY cp1.ProductType, cp2.ProductType
        HAVING COUNT(DISTINCT cp1.ClientName) >= {min_co_occurrence}
        ORDER BY CoOccurrences DESC
        """
    
    # ============================================
    # SPECIFICATION INTELLIGENCE SQL GENERATORS (NEW)
    # ============================================
    
    def _sql_paper_gsm_popularity(self, params: Dict[str, Any]) -> str:
        """Generate SQL for paper GSM popularity analysis"""
        months = params['months']
        return f"""
        SELECT 
            pt.[Desc] AS PaperType,
            gsm.[DESC] AS GSM,
            jtype.[Desc] AS ProductType,
            COUNT(*) AS OrderCount,
            SUM(jt.QTY) AS TotalQuantity,
            AVG(jt.Cost) AS AvgPrice,
            SUM(jt.Cost) AS TotalRevenue
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND pt.[Desc] IS NOT NULL
            AND gsm.[DESC] IS NOT NULL
            AND jt.Cost IS NOT NULL
        GROUP BY pt.[Desc], gsm.[DESC], jtype.[Desc]
        HAVING COUNT(*) >= 3
        ORDER BY OrderCount DESC
        """

    def _sql_binding_by_page_count(self, params: Dict[str, Any]) -> str:
        """Generate SQL for binding recommendations by page count"""
        months = params['months']
        return f"""
        SELECT 
            CASE 
                WHEN jt.Pages < 20 THEN '0-20 pages'
                WHEN jt.Pages < 40 THEN '20-40 pages'
                WHEN jt.Pages < 60 THEN '40-60 pages'
                WHEN jt.Pages < 100 THEN '60-100 pages'
                WHEN jt.Pages < 200 THEN '100-200 pages'
                ELSE '200+ pages'
            END AS PageRange,
            bt.BindTypeDesc AS BindType,
            COUNT(*) AS OrderCount,
            AVG(jt.Cost) AS AvgPrice,
            SUM(jt.Cost) AS TotalRevenue,
            AVG(jt.Pages) AS AvgPages,
            -- Percentage of this page range
            CAST(COUNT(*) * 100.0 / 
                 SUM(COUNT(*)) OVER (PARTITION BY 
                     CASE 
                         WHEN jt.Pages < 20 THEN '0-20 pages'
                         WHEN jt.Pages < 40 THEN '20-40 pages'
                         WHEN jt.Pages < 60 THEN '40-60 pages'
                         WHEN jt.Pages < 100 THEN '60-100 pages'
                         WHEN jt.Pages < 200 THEN '100-200 pages'
                         ELSE '200+ pages'
                     END)
                 AS DECIMAL(5,2)) AS PercentOfRange
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
        WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            AND jt.Pages IS NOT NULL
            AND jt.Pages > 0
            AND bt.BindTypeDesc IS NOT NULL
            AND jt.Cost IS NOT NULL
        GROUP BY 
            CASE 
                WHEN jt.Pages < 20 THEN '0-20 pages'
                WHEN jt.Pages < 40 THEN '20-40 pages'
                WHEN jt.Pages < 60 THEN '40-60 pages'
                WHEN jt.Pages < 100 THEN '60-100 pages'
                WHEN jt.Pages < 200 THEN '100-200 pages'
                ELSE '200+ pages'
            END,
            bt.BindTypeDesc
        ORDER BY 
            CASE PageRange
                WHEN '0-20 pages' THEN 1
                WHEN '20-40 pages' THEN 2
                WHEN '40-60 pages' THEN 3
                WHEN '60-100 pages' THEN 4
                WHEN '100-200 pages' THEN 5
                WHEN '200+ pages' THEN 6
            END,
            OrderCount DESC
        """
    
    # ============================================
    # AI EXPORT & ANALYSIS SQL GENERATORS (NEW - October 2025)
    # ============================================
    
    def _sql_conversation_data_export(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for exporting conversation session data
        Note: This requires session tracking tables which may not exist yet
        Returns placeholder structure for implementation
        """
        session_id = params.get('session_id', 'current')
        include_sql = params.get('include_sql', True)
        include_results = params.get('include_results', True)
        
        # For now, return a metadata query showing available data
        # TODO: Implement proper session tracking tables
        return f"""
        SELECT 
            '{session_id}' AS SessionID,
            'N/A' AS MessageID,
            'system' AS MessageType,
            'Session tracking tables not yet implemented. Use session export from web interface.' AS Content,
            GETDATE() AS Timestamp,
            NULL AS SQLQuery,
            0 AS ResultRows
        """
    
    def _sql_dashboard_snapshot_export(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for dashboard snapshot export
        Provides summary of key business metrics for AI analysis
        """
        section_filter = params.get('section_filter', 'all')
        
        return """
        SELECT 
            'Business Overview' AS SectionName,
            'current_metrics' AS QueryName,
            CONCAT(
                'Total Orders: ', COUNT(DISTINCT o.OrderID), ', ',
                'Active Clients: ', COUNT(DISTINCT o.ClientID), ', ',
                'Revenue MTD: $', CAST(SUM(CASE WHEN MONTH(o.OrderDate) = MONTH(GETDATE()) THEN o.TotalCost ELSE 0 END) AS DECIMAL(10,2)), ', ',
                'Last Updated: ', CONVERT(VARCHAR, GETDATE(), 120)
            ) AS DataSummary,
            COUNT(*) AS RecordCount,
            GETDATE() AS LastUpdated
        FROM Orders o
        WHERE o.OrderDate >= DATEADD(MONTH, -12, GETDATE())
        
        UNION ALL
        
        SELECT 
            'Workflow Status' AS SectionName,
            'active_jobs' AS QueryName,
            CONCAT(
                'In Production: ', COUNT(CASE WHEN Complete = 0 THEN 1 END), ', ',
                'Overdue: ', COUNT(CASE WHEN Complete = 0 AND DateRequired < GETDATE() THEN 1 END)
            ) AS DataSummary,
            COUNT(*) AS RecordCount,
            GETDATE() AS LastUpdated
        FROM APGJobTicket
        
        UNION ALL
        
        SELECT 
            'Client Intelligence' AS SectionName,
            'top_clients' AS QueryName,
            CONCAT('Top 10 clients by revenue, Last 12 months') AS DataSummary,
            10 AS RecordCount,
            GETDATE() AS LastUpdated
        
        UNION ALL
        
        SELECT 
            'Financial Analysis' AS SectionName,
            'revenue_trends' AS QueryName,
            CONCAT('Monthly revenue trend, Last 12 months') AS DataSummary,
            12 AS RecordCount,
            GETDATE() AS LastUpdated
        """
    
    def _sql_session_query_history(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for session query history
        Note: Requires query logging tables
        Returns placeholder for implementation
        """
        session_id = params.get('session_id', 'current')
        min_duration = params.get('min_duration_ms', 0)
        
        return f"""
        SELECT 
            NEWID() AS QueryID,
            'sample_query' AS QueryName,
            {min_duration} AS ExecutionTime,
            100 AS RowsReturned,
            GETDATE() AS Timestamp,
            1 AS Success
        WHERE 1=0  -- No results, placeholder query
        -- TODO: Implement query logging tables
        """
    
    def _sql_ai_insights_summary(self, params: Dict[str, Any]) -> str:
        """
        Generate SQL for AI-ready insights summary
        Provides key business metrics and trends for AI analysis
        """
        insight_focus = params.get('insight_focus', 'all')
        days_back = params.get('days_back', 30)
        
        return f"""
        WITH RecentMetrics AS (
            SELECT 
                'Sales Performance' AS InsightCategory,
                'Total Revenue' AS KeyMetric,
                CAST(SUM(TotalCost) AS DECIMAL(10,2)) AS CurrentValue,
                CAST(
                    (SUM(TotalCost) - 
                     (SELECT SUM(TotalCost) FROM Orders 
                      WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                        AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE()))
                    ) * 100.0 / NULLIF(
                        (SELECT SUM(TotalCost) FROM Orders 
                         WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                           AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE())), 0)
                AS DECIMAL(5,2)) AS TrendPercent
            FROM Orders
            WHERE OrderDate >= DATEADD(DAY, -{days_back}, GETDATE())
            
            UNION ALL
            
            SELECT 
                'Customer Activity' AS InsightCategory,
                'Active Clients' AS KeyMetric,
                CAST(COUNT(DISTINCT ClientID) AS DECIMAL(10,2)),
                CAST(
                    (COUNT(DISTINCT ClientID) - 
                     (SELECT COUNT(DISTINCT ClientID) FROM Orders 
                      WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                        AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE()))
                    ) * 100.0 / NULLIF(
                        (SELECT COUNT(DISTINCT ClientID) FROM Orders 
                         WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                           AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE())), 0)
                AS DECIMAL(5,2))
            FROM Orders
            WHERE OrderDate >= DATEADD(DAY, -{days_back}, GETDATE())
            
            UNION ALL
            
            SELECT 
                'Order Volume' AS InsightCategory,
                'Order Count' AS KeyMetric,
                CAST(COUNT(*) AS DECIMAL(10,2)),
                CAST(
                    (COUNT(*) - 
                     (SELECT COUNT(*) FROM Orders 
                      WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                        AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE()))
                    ) * 100.0 / NULLIF(
                        (SELECT COUNT(*) FROM Orders 
                         WHERE OrderDate >= DATEADD(DAY, -{days_back * 2}, GETDATE()) 
                           AND OrderDate < DATEADD(DAY, -{days_back}, GETDATE())), 0)
                AS DECIMAL(5,2))
            FROM Orders
            WHERE OrderDate >= DATEADD(DAY, -{days_back}, GETDATE())
        )
        SELECT 
            InsightCategory,
            KeyMetric,
            CurrentValue,
            CASE 
                WHEN TrendPercent > 0 THEN 'Up ' + CAST(ABS(TrendPercent) AS VARCHAR) + '%'
                WHEN TrendPercent < 0 THEN 'Down ' + CAST(ABS(TrendPercent) AS VARCHAR) + '%'
                ELSE 'Stable'
            END AS Trend,
            CONCAT('Based on last ', {days_back}, ' days vs previous period') AS Context,
            CASE 
                WHEN TrendPercent > 10 THEN 'Strong growth - maintain momentum'
                WHEN TrendPercent > 0 THEN 'Positive trend - monitor closely'
                WHEN TrendPercent < -10 THEN 'Declining - investigate causes'
                WHEN TrendPercent < 0 THEN 'Slight decline - watch trends'
                ELSE 'Stable performance - optimize operations'
            END AS Recommendation
        FROM RecentMetrics
        ORDER BY InsightCategory
        """
    
    # ============================================
    # STOCK MANAGEMENT SQL GENERATORS (NEW - October 2025)
    # ============================================
    
    def _sql_stock_inventory_master(self, status_filter: str = 'all', stock_type: str = 'all') -> str:
        """Generate SQL for complete stock master inventory"""
        status_condition = ""
        if status_filter != 'all':
            status_condition = f"WHERE Status = '{status_filter}'"
        
        type_condition = ""
        if stock_type != 'all':
            type_condition = f"AND StockType = '{stock_type}'" if status_condition else f"WHERE StockType = '{stock_type}'"
        
        return f"""
        WITH StockUsage AS (
            SELECT 
                StockID,
                COUNT(*) AS Usage30d,
                MAX(DateUsed) AS LastUsed
            FROM OrderStockUsage
            WHERE DateUsed >= DATEADD(DAY, -30, GETDATE())
            GROUP BY StockID
        ),
        StockStatus AS (
            SELECT 
                s.StockID,
                s.StockType,
                s.Size,
                s.GSM,
                s.CostPer1000,
                s.MarkupPercent AS Markup,
                s.CostPer1000 * (1 + s.MarkupPercent/100.0) AS FinalPrice,
                ISNULL(s.CurrentStockLevel, 0) AS StockLevel,
                s.ReorderPoint,
                CASE 
                    WHEN ISNULL(s.CurrentStockLevel, 0) <= s.CriticalLevel THEN 'critical'
                    WHEN ISNULL(s.CurrentStockLevel, 0) <= s.ReorderPoint THEN 'low'
                    WHEN s.IsActive = 0 THEN 'inactive'
                    ELSE 'ok'
                END AS Status,
                ISNULL(u.LastUsed, '2020-01-01') AS LastUsed,
                ISNULL(u.Usage30d, 0) AS Usage30d
            FROM Quote_DigitalStocks s
            LEFT JOIN StockUsage u ON s.StockID = u.StockID
        )
        SELECT * FROM StockStatus
        {status_condition}
        {type_condition}
        ORDER BY Status DESC, StockType, GSM
        """
    
    def _sql_stock_usage_analytics(self, days_back: int = 90, top_n: int = 20) -> str:
        """
        Generate SQL for stock usage patterns based on JobTickets
        Analyzes actual GSM usage from production jobs
        """
        return f"""
        WITH StockUsage AS (
            -- Match JobTickets to stocks by GSM value
            SELECT 
                gsm.[DESC] AS GSMDesc,
                CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT) AS GSMValue,
                ds.StockID,
                dst.StockTypeDesc,
                ds.Length,
                ds.Width,
                ds.GSM AS StockGSM,
                COUNT(DISTINCT jt.TicketID) AS JobCount,
                SUM(jt.QTY) AS TotalQuantity,
                CAST(SUM(jt.QTY) * 1.0 / {days_back} AS DECIMAL(10,2)) AS AvgDailyUsage,
                CAST(SUM(jt.QTY) * 1.0 / {days_back} * 30 AS DECIMAL(10,2)) AS Forecast30Days,
                MIN(o.OrderDate) AS FirstOrderDate,
                MAX(o.OrderDate) AS LastOrderDate
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
            -- Match to stocks by GSM value
            LEFT JOIN Quote_DigitalStocks ds ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
            LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
            WHERE o.OrderDate >= DATEADD(DAY, -{days_back}, GETDATE())
                AND gsm.[DESC] IS NOT NULL
                AND ISNUMERIC(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '')) = 1
            GROUP BY 
                gsm.[DESC],
                CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT),
                ds.StockID,
                dst.StockTypeDesc,
                ds.Length,
                ds.Width,
                ds.GSM
        )
        SELECT TOP {top_n}
            StockID,
            StockTypeDesc,
            GSMValue,
            Length,
            Width,
            JobCount,
            TotalQuantity,
            AvgDailyUsage,
            Forecast30Days,
            CASE 
                WHEN AvgDailyUsage > 1000 THEN 'High Demand'
                WHEN AvgDailyUsage > 100 THEN 'Medium Demand'
                WHEN AvgDailyUsage > 0 THEN 'Low Demand'
                ELSE 'No Recent Usage'
            END AS DemandCategory,
            FirstOrderDate,
            LastOrderDate,
            DATEDIFF(DAY, LastOrderDate, GETDATE()) AS DaysSinceLastUse
        FROM StockUsage
        WHERE StockID IS NOT NULL
        ORDER BY TotalQuantity DESC
        """
    
    def _sql_stock_reorder_alerts(self, urgency: str = 'all') -> str:
        """
        Generate SQL for stock reorder alerts
        NOTE: Production database (Quote_DigitalStocks) only has pricing data.
        Returns empty result set since inventory management is in temp SQLite only.
        Use stock_database_cli.py --stock-status for actual inventory alerts.
        """
        return """
        SELECT 
            NULL AS StockType,
            NULL AS Size,
            NULL AS GSM,
            0 AS CurrentLevel,
            0 AS ReorderPoint,
            0 AS OptimalStockLevel,
            0 AS DaysUntilEmpty,
            0 AS SuggestedOrderQty,
            0.0 AS EstimatedCost,
            NULL AS LastOrderDate,
            'info' AS Urgency
        WHERE 1=0
        -- Production DB does not contain inventory levels (CurrentStockLevel, ReorderPoint, etc.)
        -- These fields only exist in temp SQLite database
        -- Use stock_database_cli.py for inventory management
        """
    
    def _sql_stock_pricing_profitability(self, months: int = 6) -> str:
        """
        Generate SQL for stock pricing profitability analysis
        Analyzes cost per thousand, markup, and sell prices for all stocks
        """
        return f"""
        WITH StockPricing AS (
            SELECT 
                ds.StockID,
                dst.StockTypeDesc,
                ds.GSM,
                ds.Length,
                ds.Width,
                ds.CostPerThousand,
                ISNULL(ds.Markup, 0) AS MarkupPercent,
                -- Calculate sell price with markup
                CAST(ds.CostPerThousand * (1 + ISNULL(ds.Markup, 0)/100.0) AS DECIMAL(18,4)) AS SellPricePerThousand,
                -- Calculate profit per thousand
                CAST((ds.CostPerThousand * (1 + ISNULL(ds.Markup, 0)/100.0)) - ds.CostPerThousand AS DECIMAL(18,4)) AS ProfitPerThousand,
                -- Calculate sheet size in SQM
                CAST((ds.Length * ds.Width / 1000000.0) AS DECIMAL(10,4)) AS SheetSizeSQM
            FROM Quote_DigitalStocks ds
            INNER JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
        ),
        UsageData AS (
            -- Get usage from JobTickets for the period
            SELECT 
                CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT) AS GSMValue,
                COUNT(DISTINCT jt.TicketID) AS JobCount,
                SUM(jt.QTY) AS TotalQuantity,
                SUM(jt.Cost) AS TotalRevenue
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
                AND gsm.[DESC] IS NOT NULL
                AND ISNUMERIC(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '')) = 1
            GROUP BY CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
        )
        SELECT 
            sp.StockID,
            sp.StockTypeDesc,
            sp.GSM,
            sp.Length,
            sp.Width,
            sp.CostPerThousand,
            sp.MarkupPercent,
            sp.SellPricePerThousand,
            sp.ProfitPerThousand,
            sp.SheetSizeSQM,
            ISNULL(ud.JobCount, 0) AS JobCount{months}Months,
            ISNULL(ud.TotalQuantity, 0) AS Quantity{months}Months,
            ISNULL(ud.TotalRevenue, 0) AS Revenue{months}Months,
            -- Calculate estimated profit based on usage
            CAST(ISNULL(ud.TotalQuantity, 0) * sp.ProfitPerThousand / 1000.0 AS DECIMAL(18,4)) AS EstimatedProfit,
            -- ROI percentage
            CASE 
                WHEN NULLIF(ud.TotalRevenue, 0) IS NOT NULL THEN 
                    CAST((ud.TotalRevenue - (ud.TotalQuantity * sp.CostPerThousand / 1000.0)) / ud.TotalRevenue * 100 AS DECIMAL(8,4))
                ELSE 0
            END AS MarginPercent
        FROM StockPricing sp
        LEFT JOIN UsageData ud ON sp.GSM = ud.GSMValue
        WHERE sp.CostPerThousand > 0
        ORDER BY ISNULL(ud.TotalRevenue, 0) DESC, sp.MarkupPercent DESC
        """
    
    def _sql_client_stock_preferences(self, months: int = 12, min_orders: int = 3) -> str:
        """Generate SQL for client stock preferences and predictions"""
        return f"""
        WITH ClientStockUsage AS (
            SELECT 
                c.ClientName,
                s.StockType,
                COUNT(DISTINCT o.OrderID) AS OrderCount,
                SUM(o.Quantity) AS TotalQuantity,
                MAX(o.OrderDate) AS LastOrderDate,
                AVG(DATEDIFF(DAY, LAG(o.OrderDate) OVER (PARTITION BY c.ClientID ORDER BY o.OrderDate), o.OrderDate)) AS AvgDaysBetweenOrders
            FROM Orders o
            JOIN Clients c ON o.ClientID = c.ClientID
            JOIN OrderItems oi ON o.OrderID = oi.OrderID
            JOIN Quote_DigitalStocks s ON oi.StockID = s.StockID
            WHERE o.OrderDate >= DATEADD(MONTH, -{months}, GETDATE())
            GROUP BY c.ClientName, c.ClientID, s.StockType
            HAVING COUNT(DISTINCT o.OrderID) >= {min_orders}
        ),
        ClientTopStocks AS (
            SELECT 
                ClientName,
                STRING_AGG(StockType, ', ') WITHIN GROUP (ORDER BY OrderCount DESC) AS PreferredStocks,
                SUM(OrderCount) AS TotalOrders,
                AVG(TotalQuantity) AS AvgOrderSize,
                MAX(LastOrderDate) AS LastOrderDate,
                AVG(AvgDaysBetweenOrders) AS AvgReorderCycle
            FROM ClientStockUsage
            GROUP BY ClientName
        )
        SELECT 
            ClientName,
            PreferredStocks,
            CASE 
                WHEN AvgReorderCycle <= 30 THEN 'Monthly'
                WHEN AvgReorderCycle <= 90 THEN 'Quarterly'
                WHEN AvgReorderCycle <= 180 THEN 'Semi-Annual'
                ELSE 'Annual'
            END AS OrderFrequency,
            AvgOrderSize,
            LastOrderDate,
            DATEADD(DAY, ISNULL(AvgReorderCycle, 30), LastOrderDate) AS PredictedReorderDate,
            DATEDIFF(DAY, LastOrderDate, GETDATE()) AS DaysSinceLastOrder
        FROM ClientTopStocks
        ORDER BY DaysSinceLastOrder DESC
        """
    
    def _sql_stock_cost_trends(self, stock_type: str = 'all', months: int = 24) -> str:
        """Generate SQL for historical stock cost trends"""
        type_filter = ""
        if stock_type != 'all':
            type_filter = f"WHERE s.StockType = '{stock_type}'"
        
        return f"""
        WITH MonthlyCosts AS (
            SELECT 
                FORMAT(h.PriceDate, 'yyyy-MM') AS YearMonth,
                s.StockType,
                AVG(h.CostPer1000) AS AvgCost,
                s.SupplierName
            FROM StockPriceHistory h
            JOIN Quote_DigitalStocks s ON h.StockID = s.StockID
            WHERE h.PriceDate >= DATEADD(MONTH, -{months}, GETDATE())
            {type_filter}
            GROUP BY FORMAT(h.PriceDate, 'yyyy-MM'), s.StockType, s.SupplierName
        )
        SELECT 
            YearMonth,
            StockType,
            AvgCost AS CostPer1000,
            CAST(
                (AvgCost - LAG(AvgCost) OVER (PARTITION BY StockType ORDER BY YearMonth)) 
                / NULLIF(LAG(AvgCost) OVER (PARTITION BY StockType ORDER BY YearMonth), 0) * 100
            AS DECIMAL(5,2)) AS ChangePercent,
            SupplierName
        FROM MonthlyCosts
        ORDER BY YearMonth DESC, StockType
        """
    
    # ============================================
    # VALIDATION AND STATUS METHODS
    # ============================================
    
    def get_validated_queries(self) -> List[str]:
        """Get list of queries that have been validated against real database"""
        validated = []
        for query_name, query_def in self.query_catalog.items():
            if query_def.get('validated', False):
                validated.append(query_name)
        return validated

    def get_query_status_report(self) -> Dict[str, Any]:
        """Get status report of query library"""
        total = len(self.query_catalog)
        validated = len(self.get_validated_queries())
        categories = {}
        for query_name, query_def in self.query_catalog.items():
            category = query_def['category']
            if category not in categories:
                categories[category] = {'total': 0, 'validated': 0}
            categories[category]['total'] += 1
            if query_def.get('validated', False):
                categories[category]['validated'] += 1
        
        return {
            'total_queries': total,
            'validated_queries': validated,
            'validation_rate': f"{validated/total*100:.1f}%",
            'categories': categories
        }
    
    # ============================================
    # CALCULATOR PRICING MANAGEMENT SQL GENERATORS
    # ============================================
    
    def _sql_get_pricing_constant(self, params: Dict[str, Any]) -> str:
        """Get pricing parameter with all overrides and statistics"""
        parameter_name = params['parameter_name']
        calculator_name = params.get('calculator_name')
        
        if calculator_name:
            # Filter to specific calculator
            return f"""
            SELECT 
                p.parameter_name,
                p.base_value,
                p.data_type,
                (p.value_statistics->>'variance_pct')::numeric AS variance_pct,
                (p.value_statistics->>'min')::numeric AS min_value,
                (p.value_statistics->>'max')::numeric AS max_value,
                (p.value_statistics->>'mean')::numeric AS mean_value,
                (p.value_statistics->>'median')::numeric AS median_value,
                o.calculator_name,
                o.value AS override_value,
                o.updated_at AS override_updated_at
            FROM calculator_pricing_parameters p
            LEFT JOIN calculator_parameter_overrides o 
                ON p.parameter_id = o.parameter_id 
                AND o.is_active = TRUE
            WHERE p.parameter_name = '{parameter_name}'
                AND p.is_active = TRUE
                AND (o.calculator_name = '{calculator_name}' OR o.calculator_name IS NULL)
            ORDER BY o.calculator_name NULLS FIRST;
            """
        else:
            # Show all calculator overrides
            return f"""
            SELECT 
                p.parameter_name,
                p.base_value,
                p.data_type,
                (p.value_statistics->>'variance_pct')::numeric AS variance_pct,
                (p.value_statistics->>'min')::numeric AS min_value,
                (p.value_statistics->>'max')::numeric AS max_value,
                (p.value_statistics->>'mean')::numeric AS mean_value,
                (p.value_statistics->>'median')::numeric AS median_value,
                COALESCE(
                    (SELECT COUNT(*) FROM calculator_parameter_overrides 
                     WHERE parameter_id = p.parameter_id AND is_active = TRUE),
                    0
                ) AS override_count,
                o.calculator_name,
                o.value AS override_value,
                o.updated_at AS override_updated_at
            FROM calculator_pricing_parameters p
            LEFT JOIN calculator_parameter_overrides o 
                ON p.parameter_id = o.parameter_id 
                AND o.is_active = TRUE
            WHERE p.parameter_name = '{parameter_name}'
                AND p.is_active = TRUE
            ORDER BY o.calculator_name;
            """
    
    def _sql_get_calculator_config(self, params: Dict[str, Any]) -> str:
        """Get complete calculator configuration"""
        calculator_name = params['calculator_name']
        include_product_options = params.get('include_product_options', True)
        
        if include_product_options:
            return f"""
            WITH calculator_params AS (
                SELECT 
                    c.calculator_name,
                    c.calculator_file,
                    jsonb_agg(DISTINCT p.parameter_name) AS parameters_used,
                    COUNT(DISTINCT p.parameter_id) AS parameter_count
                FROM calculators_registry c
                LEFT JOIN calculator_pricing_parameters p 
                    ON c.calculator_name = ANY(
                        SELECT jsonb_array_elements_text(p.used_by_calculators)
                    )
                WHERE c.calculator_name = '{calculator_name}'
                    AND c.is_active = TRUE
                GROUP BY c.calculator_name, c.calculator_file
            ),
            calculator_overrides AS (
                SELECT 
                    c.calculator_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'parameter_name', p.parameter_name,
                            'override_value', o.value,
                            'base_value', p.base_value,
                            'updated_at', o.updated_at
                        ) ORDER BY p.parameter_name
                    ) AS active_overrides,
                    COUNT(*) AS override_count
                FROM calculators_registry c
                INNER JOIN calculator_parameter_overrides o 
                    ON c.calculator_name = o.calculator_name
                INNER JOIN calculator_pricing_parameters p 
                    ON o.parameter_id = p.parameter_id
                WHERE c.calculator_name = '{calculator_name}'
                    AND o.is_active = TRUE
                    AND p.is_active = TRUE
                GROUP BY c.calculator_name
            ),
            calculator_options AS (
                SELECT 
                    c.calculator_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'option_name', po.option_name,
                            'option_type', po.option_type,
                            'choice_count', (
                                SELECT COUNT(*) 
                                FROM product_option_choices poc 
                                WHERE poc.option_id = po.option_id 
                                AND poc.is_active = TRUE
                            )
                        ) ORDER BY po.option_name
                    ) AS product_options,
                    COUNT(*) AS option_count
                FROM calculators_registry c
                INNER JOIN product_options po 
                    ON c.calculator_name = po.calculator_name
                WHERE c.calculator_name = '{calculator_name}'
                    AND po.is_active = TRUE
                GROUP BY c.calculator_name
            )
            SELECT 
                cp.calculator_name,
                cp.calculator_file,
                cp.parameters_used,
                cp.parameter_count,
                COALESCE(co.active_overrides, '[]'::jsonb) AS active_overrides,
                COALESCE(co.override_count, 0) AS override_count,
                COALESCE(copt.product_options, '[]'::jsonb) AS product_options,
                COALESCE(copt.option_count, 0) AS option_count
            FROM calculator_params cp
            LEFT JOIN calculator_overrides co ON cp.calculator_name = co.calculator_name
            LEFT JOIN calculator_options copt ON cp.calculator_name = copt.calculator_name;
            """
        else:
            return f"""
            WITH calculator_params AS (
                SELECT 
                    c.calculator_name,
                    c.calculator_file,
                    jsonb_agg(DISTINCT p.parameter_name) AS parameters_used,
                    COUNT(DISTINCT p.parameter_id) AS parameter_count
                FROM calculators_registry c
                LEFT JOIN calculator_pricing_parameters p 
                    ON c.calculator_name = ANY(
                        SELECT jsonb_array_elements_text(p.used_by_calculators)
                    )
                WHERE c.calculator_name = '{calculator_name}'
                    AND c.is_active = TRUE
                GROUP BY c.calculator_name, c.calculator_file
            ),
            calculator_overrides AS (
                SELECT 
                    c.calculator_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'parameter_name', p.parameter_name,
                            'override_value', o.value,
                            'base_value', p.base_value
                        ) ORDER BY p.parameter_name
                    ) AS active_overrides,
                    COUNT(*) AS override_count
                FROM calculators_registry c
                INNER JOIN calculator_parameter_overrides o 
                    ON c.calculator_name = o.calculator_name
                INNER JOIN calculator_pricing_parameters p 
                    ON o.parameter_id = p.parameter_id
                WHERE c.calculator_name = '{calculator_name}'
                    AND o.is_active = TRUE
                    AND p.is_active = TRUE
                GROUP BY c.calculator_name
            )
            SELECT 
                cp.calculator_name,
                cp.calculator_file,
                cp.parameters_used,
                cp.parameter_count,
                COALESCE(co.active_overrides, '[]'::jsonb) AS active_overrides,
                COALESCE(co.override_count, 0) AS override_count
            FROM calculator_params cp
            LEFT JOIN calculator_overrides co ON cp.calculator_name = co.calculator_name;
            """
    
    def _sql_get_product_options_for_calculator(self, params: Dict[str, Any]) -> str:
        """Get product options with choices for calculator"""
        calculator_name = params['calculator_name']
        include_inactive = params.get('include_inactive', False)
        
        active_filter = "" if include_inactive else "AND po.is_active = TRUE AND poc.is_active = TRUE"
        
        return f"""
        SELECT 
            po.option_name,
            po.option_type,
            poc.choice_value,
            poc.choice_label,
            poc.price,
            poc.price_type,
            poc.is_default,
            poc.display_order,
            po.created_at AS option_created,
            poc.created_at AS choice_created
        FROM product_options po
        INNER JOIN product_option_choices poc 
            ON po.option_id = poc.option_id
        WHERE po.calculator_name = '{calculator_name}'
            {active_filter}
        ORDER BY po.option_name, poc.display_order, poc.choice_value;
        """
    
    def _sql_find_high_variance_parameters(self, params: Dict[str, Any]) -> str:
        """Find parameters with high price variance"""
        variance_threshold = params.get('variance_threshold', 100.0)
        min_calculators = params.get('min_calculators', 3)
        
        return f"""
        SELECT 
            p.parameter_name,
            p.base_value,
            (p.value_statistics->>'variance_pct')::numeric AS variance_pct,
            (p.value_statistics->>'min')::numeric AS min_value,
            (p.value_statistics->>'max')::numeric AS max_value,
            (p.value_statistics->>'mean')::numeric AS mean_value,
            jsonb_array_length(p.used_by_calculators) AS calculator_count,
            p.used_by_calculators AS calculators_list
        FROM calculator_pricing_parameters p
        WHERE p.is_active = TRUE
            AND (p.value_statistics->>'variance_pct')::numeric >= {variance_threshold}
            AND jsonb_array_length(p.used_by_calculators) >= {min_calculators}
        ORDER BY (p.value_statistics->>'variance_pct')::numeric DESC;
        """
    
    def _sql_get_parameter_usage_map(self, params: Dict[str, Any]) -> str:
        """Show parameter usage across calculators"""
        parameter_name = params.get('parameter_name')
        min_calculators = params.get('min_calculators', 2)
        
        if parameter_name:
            return f"""
            SELECT 
                p.parameter_name,
                jsonb_array_length(p.used_by_calculators) AS calculator_count,
                p.used_by_calculators AS calculator_names,
                EXISTS(
                    SELECT 1 FROM calculator_parameter_overrides o 
                    WHERE o.parameter_id = p.parameter_id 
                    AND o.is_active = TRUE
                ) AS has_overrides,
                (
                    SELECT COUNT(*) FROM calculator_parameter_overrides o 
                    WHERE o.parameter_id = p.parameter_id 
                    AND o.is_active = TRUE
                ) AS override_count
            FROM calculator_pricing_parameters p
            WHERE p.parameter_name = '{parameter_name}'
                AND p.is_active = TRUE;
            """
        else:
            return f"""
            SELECT 
                p.parameter_name,
                jsonb_array_length(p.used_by_calculators) AS calculator_count,
                p.used_by_calculators AS calculator_names,
                EXISTS(
                    SELECT 1 FROM calculator_parameter_overrides o 
                    WHERE o.parameter_id = p.parameter_id 
                    AND o.is_active = TRUE
                ) AS has_overrides,
                (
                    SELECT COUNT(*) FROM calculator_parameter_overrides o 
                    WHERE o.parameter_id = p.parameter_id 
                    AND o.is_active = TRUE
                ) AS override_count
            FROM calculator_pricing_parameters p
            WHERE p.is_active = TRUE
                AND jsonb_array_length(p.used_by_calculators) >= {min_calculators}
            ORDER BY jsonb_array_length(p.used_by_calculators) DESC;
            """
    
    def _sql_search_product_options(self, params: Dict[str, Any]) -> str:
        """Search product options across calculators"""
        search_term = params.get('search_term')
        calculator_name = params.get('calculator_name')
        option_type = params.get('option_type')
        
        filters = []
        if search_term:
            filters.append(f"po.option_name ILIKE '%{search_term}%'")
        if calculator_name:
            filters.append(f"po.calculator_name = '{calculator_name}'")
        if option_type:
            filters.append(f"po.option_type = '{option_type}'")
        
        where_clause = "WHERE po.is_active = TRUE"
        if filters:
            where_clause += " AND " + " AND ".join(filters)
        
        return f"""
        SELECT 
            po.option_name,
            po.option_type,
            po.calculator_name,
            COUNT(poc.choice_id) AS choice_count,
            BOOL_OR(poc.price IS NOT NULL AND poc.price > 0) AS has_prices,
            CASE 
                WHEN MIN(poc.price) IS NOT NULL 
                THEN CONCAT('$', ROUND(MIN(poc.price)::numeric, 2), ' - $', ROUND(MAX(poc.price)::numeric, 2))
                ELSE 'No prices'
            END AS price_range
        FROM product_options po
        LEFT JOIN product_option_choices poc 
            ON po.option_id = poc.option_id 
            AND poc.is_active = TRUE
        {where_clause}
        GROUP BY po.option_id, po.option_name, po.option_type, po.calculator_name
        ORDER BY po.option_name;
        """
    
    def _sql_get_option_price_variance(self, params: Dict[str, Any]) -> str:
        """Find product options with high price variance"""
        calculator_name = params.get('calculator_name')
        min_choices = params.get('min_choices', 3)
        
        calculator_filter = f"AND po.calculator_name = '{calculator_name}'" if calculator_name else ""
        
        return f"""
        SELECT 
            po.option_name,
            po.calculator_name,
            COUNT(poc.choice_id) AS choice_count,
            MIN(poc.price) AS min_price,
            MAX(poc.price) AS max_price,
            AVG(poc.price) AS avg_price,
            MAX(poc.price) - MIN(poc.price) AS price_range,
            CASE 
                WHEN AVG(poc.price) > 0 
                THEN ROUND((STDDEV(poc.price) / AVG(poc.price) * 100)::numeric, 1)
                ELSE 0
            END AS variance_pct
        FROM product_options po
        INNER JOIN product_option_choices poc 
            ON po.option_id = poc.option_id
        WHERE po.is_active = TRUE
            AND poc.is_active = TRUE
            AND poc.price IS NOT NULL
            AND poc.price > 0
            {calculator_filter}
        GROUP BY po.option_id, po.option_name, po.calculator_name
        HAVING COUNT(poc.choice_id) >= {min_choices}
        ORDER BY variance_pct DESC;
        """


# ============================================
# HELPER FUNCTION FOR JSON EXPORT
# ============================================

def export_query_catalog_to_json(filepath: str = "query_catalog.json"):
    """Export query catalog to JSON file for documentation"""
    library = QueryLibrary()
    catalog = library.get_available_queries()
    
    with open(filepath, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"[SUCCESS] Query catalog exported to {filepath}")
    print(f"[INFO] Total queries: {len(catalog)}")
    
    categories = library.get_query_categories()
    for category in categories:
        count = len(library.get_available_queries(category))
        print(f"   - {category}: {count} queries")


if __name__ == "__main__":
    # Demo usage
    library = QueryLibrary()
    
    print("="*80)
    print("VALIDATED QUERY LIBRARY - STATUS REPORT")
    print("="*80)
    
    # Show validation status
    status = library.get_query_status_report()
    print(f"\n[INFO] Total Queries: {status['total_queries']}")
    print(f"[SUCCESS] Validated: {status['validated_queries']} ({status['validation_rate']})")
    print(f"\n[INFO] By Category:")
    for cat, stats in status['categories'].items():
        validated_pct = stats['validated']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"   {cat}: {stats['validated']}/{stats['total']} ({validated_pct:.0f}%)")
    
    # Show available categories
    categories = library.get_query_categories()
    print(f"\n[INFO] All Categories ({len(categories)}):")
    for cat in categories:
        queries = library.get_available_queries(cat)
        print(f"   - {cat}: {len(queries)} queries")
    
    # Show sample validated queries
    print("\n" + "="*80)
    print("TESTING VALIDATED QUERIES")
    print("="*80)
    
    # Test operational flow queries
    test_queries = [
        ("current_production_status", {"days_back": 30}),
        ("overdue_jobs_alert", {}),
        ("priority_work_queue", {"days_ahead": 3}),
        ("bottleneck_detection", {"wip_threshold": 5}),
        ("daily_capacity_forecast", {"days_ahead": 7}),
        ("monthly_revenue_trend", {"months": 12}),
        ("top_customers_detailed", {"months": 12, "top_n": 20}),
        ("product_turnaround_benchmarks", {"months": 6}),
        ("high_value_jobs_list", {"months": 12, "min_value": 5000}),
        ("binding_finishing_analysis", {"months": 12}),
        ("day_of_week_patterns", {"weeks": 26}),
        ("quarterly_performance", {"quarters": 8}),
    ]
    
    for query_name, params in test_queries:
        try:
            result = library.build_query(query_name, **params)
            validated_flag = "[VALIDATED]" if library.query_catalog[query_name].get('validated', False) else "[NOT VALIDATED]"
            print(f"\n{validated_flag}: {query_name}")
            print(f"   Category: {result['metadata']['category']}")
            print(f"   Visualization: {result['metadata']['visualization']}")
            print(f"   SQL length: {len(result['sql'])} chars")
        except Exception as e:
            print(f"\n[ERROR] {query_name}: {str(e)}")
    
    # Show sample query
    print("\n" + "="*80)
    print("Sample Query: current_production_status")
    print("="*80)
    result = library.build_query("current_production_status", days_back=30)
    print(f"Description: {result['metadata']['description']}")
    print(f"\nSQL:")
    print(result['sql'])
    
    # Export catalog
    print("\n"+"="*80)
    export_query_catalog_to_json()
    
    # ============================================
    # DEMONSTRATE EXECUTION LAYER (NEW)
    # ============================================
    print("\n" + "="*80)
    print("EXECUTION LAYER DEMONSTRATION")
    print("="*80)
    print("\n[INFO] Note: Execution layer requires database connection.")
    print("   When connected, use: library.execute_query(query_name, **params)")
    print("\n   Returns:")
    print("   - Formatted DataFrame (currency, dates, percentages)")
    print("   - Summary: 'Found X records | Total Revenue: $Y'")
    print("   - Data quality metrics (completeness, null%, types)")
    print("   - Execution time tracking")
    print("\n   Example usage:")
    print("   ```python")
    print("   from core.query_library import QueryLibrary")
    print("   from db_connector import InHousePrintDB")
    print("")
    print("   db = InHousePrintDB('config/database-config.json')")
    print("   library = QueryLibrary(db)")
    print("")
    print("   # Execute with automatic formatting")
    print("   result = library.execute_query('top_customers_detailed', months=12)")
    print("")
    print("   if result['success']:")
    print("       print(result['summary'])  # Human-readable summary")
    print("       df = result['data']        # Formatted DataFrame")
    print("       print(f'Quality: {result['metadata']['data_quality']['completeness_percentage']}%')")
    print("   ```")
    print("\n   Available formatted columns:")
    print("   - Revenue columns → TotalRevenue_Formatted = '$1,234.56'")
    print("   - Percentage columns → OnTimeRate_Formatted = '85.3%'")
    print("   - Date columns → OrderDate_Formatted = 'Oct 06, 2025'")
    print("   - Count columns → JobCount_Formatted = '1,234'")

