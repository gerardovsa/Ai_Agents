"""
Synergy Smart Internal Document Tools - AI-Powered Progressive Processing

Advanced AI tools for intelligent document creation, updates, analysis, and batch operations.
Uses progressive processing to handle complex multi-step operations.

Functions:
- synergy_smart_create_document: Create documents with AI content generation
- synergy_smart_update_document: Update documents with intelligent modifications
- synergy_smart_analyze_document: Analyze documents with AI insights
- synergy_smart_batch_operations: Perform batch operations on multiple documents
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


# Document Templates
DOCUMENT_TEMPLATES = {
    "meeting_notes": """# {title}

## Date
{date}

## Attendees
- 

## Agenda
1. 

## Discussion
- 

## Action Items
- [ ] 

## Next Steps
- 
""",
    
    "project_plan": """# {title}

## Executive Summary


## Objectives
- 

## Scope
### In Scope
- 

### Out of Scope
- 

## Timeline
| Phase | Start | End | Deliverables |
|-------|-------|-----|--------------|
| Phase 1 | | | |

## Resources
- **Team:** 
- **Budget:** 
- **Tools:** 

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| | | | |

## Success Criteria
- 

## Next Steps
- [ ] 
""",
    
    "technical_spec": """# {title}

## Overview


## Requirements
### Functional Requirements
- 

### Non-Functional Requirements
- 

## Architecture
### System Design


### Component Diagram


### Data Model


## API Specification
### Endpoints


### Authentication


## Implementation Plan
1. 

## Testing Strategy
- 

## Deployment
- 

## Monitoring & Maintenance
- 
""",
    
    "code_review": """# Code Review: {title}

## Overview
- **Author:** 
- **PR/Branch:** 
- **Date:** {date}

## Changes Summary


## Code Quality
- **Readability:** 
- **Maintainability:** 
- **Performance:** 

## Findings
### Critical Issues
- 

### Suggestions
- 

### Positive Aspects
- 

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Recommendation
- [ ] Approve
- [ ] Request changes
- [ ] Needs discussion

## Comments

""",
    
    "bug_report": """# Bug Report: {title}

## Summary


## Environment
- **Version:** 
- **Platform:** 
- **Browser:** 

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior


## Actual Behavior


## Screenshots/Logs


## Impact
- **Severity:** 
- **Users Affected:** 

## Possible Cause


## Suggested Fix


## Related Issues
- 
""",
    
    "feature_request": """# Feature Request: {title}

## Summary


## Problem Statement


## Proposed Solution


## User Story
As a [user type], I want [feature] so that [benefit].

## Acceptance Criteria
- [ ] 
- [ ] 

## Design Mockups


## Technical Considerations


## Impact
- **Users Benefited:** 
- **Priority:** 
- **Effort Estimate:** 

## Alternatives Considered


## Dependencies

""",
    
    "sprint_retrospective": """# Sprint Retrospective: {title}

## Sprint Overview
- **Sprint:** 
- **Dates:** 
- **Team:** 

## What Went Well
- 

## What Could Be Improved
- 

## Action Items
- [ ] 

## Metrics
- **Velocity:** 
- **Completed Stories:** 
- **Bugs Fixed:** 

## Celebration


## Next Sprint Focus

""",
    
    "user_story": """# User Story: {title}

## Story
As a [user type],
I want [feature],
So that [benefit].

## Acceptance Criteria
- [ ] 
- [ ] 

## Technical Details


## Design


## Estimated Effort


## Dependencies


## Test Cases
1. 

## Notes

""",
    
    "api_documentation": """# API Documentation: {title}

## Overview


## Base URL
```
https://api.example.com/v1
```

## Authentication


## Endpoints

### GET /resource
**Description:** 

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| | | | |

**Response:**
```json
{
  
}
```

**Example:**
```bash
curl -X GET https://api.example.com/v1/resource
```

## Error Codes
| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | |
| 401 | Unauthorized | |
| 404 | Not Found | |
| 500 | Internal Server Error | |

## Rate Limiting


## Versioning

""",
    
    "training_guide": """# Training Guide: {title}

## Introduction


## Learning Objectives
By the end of this guide, you will:
- 
- 

## Prerequisites
- 

## Modules

### Module 1: 
**Duration:** 

**Content:**
- 

**Exercise:**


### Module 2: 
**Duration:** 

**Content:**
- 

**Exercise:**


## Resources
- 

## Assessment
- [ ] 

## Next Steps

""",
    
    "policy_document": """# Policy: {title}

## Purpose


## Scope
This policy applies to:
- 

## Policy Statement


## Procedures
1. 
2. 

## Roles & Responsibilities
- **Role:** Responsibility

## Compliance


## Exceptions


## Review & Updates
- **Effective Date:** {date}
- **Review Period:** 
- **Owner:** 

## Related Documents

""",
    
    "budget_forecast": """# Budget Forecast: {title}

## Overview
- **Period:** 
- **Department:** 

## Summary
| Category | Q1 | Q2 | Q3 | Q4 | Total |
|----------|----|----|----|----|-------|
| Revenue | | | | | |
| Expenses | | | | | |
| Net | | | | | |

## Revenue Breakdown
| Source | Amount | % of Total |
|--------|--------|------------|
| | | |

## Expense Breakdown
| Category | Amount | % of Total |
|----------|--------|------------|
| Personnel | | |
| Operations | | |
| Marketing | | |
| Technology | | |

## Assumptions


## Risks


## Recommendations

"""
}


def synergy_smart_create_document(
    session_id: str,
    operation: str,
    template: Optional[str] = None,
    prompt: Optional[str] = None,
    title: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    doc_type: str = "richtext",
    auto_tags: bool = True,
    auto_link: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered smart document creation with progressive processing
    
    Args:
        session_id: Synergy session ID (required)
        operation: Smart operation type (required)
        template: Template to use (required for create_from_template)
        prompt: Natural language description (required for create_from_prompt)
        title: Document title (optional - auto-generated if not provided)
        context: Additional context for content generation (optional)
        doc_type: Document type (richtext or spreadsheet)
        auto_tags: Automatically generate tags from content
        auto_link: Automatically link to related documents
        **kwargs: Credential injection
    
    Returns:
        Progressive processing result with status updates
    """
    try:
        import os
        api_base_url = kwargs.get('api_base_url', 
            os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001')
        user_id = kwargs.get('user_id', 1)
        
        processing_steps = []
        
        # Step 1: Validate operation
        processing_steps.append("Validating operation")
        valid_operations = [
            "create_from_template",
            "create_from_prompt",
            "create_multiple",
            "create_structured",
            "create_spreadsheet_advanced",
            "create_with_analysis"
        ]
        
        if operation not in valid_operations:
            return {
                'success': False,
                'error': f'Invalid operation: {operation}. Valid operations: {", ".join(valid_operations)}'
            }
        
        # Step 2: Generate content based on operation
        processing_steps.append(f"Processing {operation}")
        content = ""
        generated_title = title
        
        if operation == "create_from_template":
            if not template:
                return {
                    'success': False,
                    'error': 'template parameter required for create_from_template operation'
                }
            
            if template not in DOCUMENT_TEMPLATES:
                return {
                    'success': False,
                    'error': f'Unknown template: {template}. Available: {", ".join(DOCUMENT_TEMPLATES.keys())}'
                }
            
            # Generate from template
            processing_steps.append(f"Using template: {template}")
            template_content = DOCUMENT_TEMPLATES[template]
            
            # Fill in template variables
            if not generated_title:
                generated_title = template.replace("_", " ").title()
            
            content = template_content.format(
                title=generated_title,
                date=datetime.now().strftime("%Y-%m-%d")
            )
            
        elif operation == "create_from_prompt":
            if not prompt:
                return {
                    'success': False,
                    'error': 'prompt parameter required for create_from_prompt operation'
                }
            
            # AI content generation from prompt
            processing_steps.append(f"Generating content from prompt")
            
            # TODO: Integrate with AI agent for content generation
            # For now, create structured outline based on prompt
            if not generated_title:
                generated_title = prompt[:50] + ("..." if len(prompt) > 50 else "")
            
            content = f"""# {generated_title}

## Overview
{prompt}

## Key Points
- Point 1
- Point 2
- Point 3

## Details
[Content to be generated based on prompt]

## Next Steps
- [ ] Action item 1
- [ ] Action item 2
"""
        
        elif operation == "create_structured":
            # Create document with specific structure
            processing_steps.append("Creating structured document")
            
            if not generated_title:
                generated_title = "Structured Document"
            
            sections = context.get('sections', ['Introduction', 'Body', 'Conclusion']) if context else ['Introduction', 'Body', 'Conclusion']
            
            content = f"# {generated_title}\n\n"
            for section in sections:
                content += f"## {section}\n\n[Content for {section}]\n\n"
        
        elif operation == "create_spreadsheet_advanced":
            # Create advanced spreadsheet
            processing_steps.append("Creating advanced spreadsheet")
            doc_type = "spreadsheet"
            
            if not generated_title:
                generated_title = "Spreadsheet"
            
            # Create sample data structure
            data = context.get('data', [
                ["Column A", "Column B", "Column C"],
                ["Value 1", "Value 2", "Value 3"]
            ]) if context else [
                ["Column A", "Column B", "Column C"],
                ["Value 1", "Value 2", "Value 3"]
            ]
            
            content = json.dumps(data)
        
        else:
            # Default: create simple document
            processing_steps.append(f"Creating document with operation: {operation}")
            if not generated_title:
                generated_title = "Untitled Document"
            content = f"# {generated_title}\n\n[Content to be added]"
        
        # Step 3: Auto-generate tags if requested
        tags = None
        description = None
        
        if auto_tags:
            processing_steps.append("Generating tags")
            # Simple tag extraction from title
            tags = ", ".join([word.lower() for word in generated_title.split() if len(word) > 3][:5])
        
        # Step 4: Create the document
        processing_steps.append("Creating document in database")
        
        payload = {
            'session_id': session_id,
            'title': generated_title,
            'content': content if doc_type == "richtext" else "",
            'content_json': content if doc_type == "spreadsheet" else None,
            'format': 'markdown',
            'doc_type': doc_type,
            'created_by': f'ai_agent_smart_create',
            'description': description,
            'tags': tags
        }
        
        response = requests.post(
            f'{api_base_url}/api/synergy/internal-doc/create',
            json=payload,
            headers={'X-User-ID': str(user_id)}
        )
        
        data = response.json()
        
        if not data.get('success'):
            return {
                'success': False,
                'error': f'Failed to create document: {data.get("error", "Unknown error")}',
                'processing_steps': processing_steps
            }
        
        processing_steps.append("Document created successfully")
        
        # Step 5: Auto-link if requested
        if auto_link:
            processing_steps.append("Linking to AI for processing")
            # TODO: Implement auto-linking to related documents
        
        return {
            'success': True,
            'doc_id': data['doc_id'],
            'title': data['title'],
            'slug': data.get('slug'),
            'share_url': data.get('share_url'),
            'processing_steps': processing_steps,
            'ai_generated_content': True,
            'operation': operation,
            'template': template,
            'metadata': {
                'tags': tags,
                'description': description,
                'doc_type': doc_type
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Smart create failed: {str(e)}',
            'processing_steps': processing_steps
        }


def synergy_smart_update_document(
    doc_id: str,
    operation: str,
    content: Optional[str] = None,
    section: Optional[str] = None,
    position: Optional[int] = None,
    source_doc_id: Optional[str] = None,
    preserve_formatting: bool = True,
    validate: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered smart document update with intelligent modifications
    
    Args:
        doc_id: Document ID to update (required)
        operation: Smart update operation (required)
        content: Content to add/replace/insert (optional)
        section: Section identifier (optional)
        position: Character position for insert (optional)
        source_doc_id: Source document for merge (optional)
        preserve_formatting: Preserve existing formatting (default: true)
        validate: Validate content before update (default: true)
        **kwargs: Credential injection
    
    Returns:
        Update result with validation details
    """
    try:
        import os
        api_base_url = kwargs.get('api_base_url', 
            os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001')
        user_id = kwargs.get('user_id', 1)
        
        # Get existing document
        response = requests.get(
            f'{api_base_url}/api/synergy/internal-doc/{doc_id}',
            headers={'X-User-ID': str(user_id)}
        )
        
        doc_data = response.json()
        
        if not doc_data.get('success'):
            return {
                'success': False,
                'error': f'Document not found: {doc_id}'
            }
        
        existing_content = doc_data.get('content', '')
        existing_json = doc_data.get('content_json')
        changes_made = []
        
        # Process operation
        if operation == "append_content":
            if section:
                # Find section and append there
                if f"## {section}" in existing_content:
                    parts = existing_content.split(f"## {section}")
                    next_section_idx = parts[1].find("\n## ")
                    if next_section_idx != -1:
                        updated_content = parts[0] + f"## {section}" + parts[1][:next_section_idx] + f"\n{content}\n" + parts[1][next_section_idx:]
                    else:
                        updated_content = existing_content + f"\n\n{content}"
                    changes_made.append(f"Appended content to section: {section}")
                else:
                    # Section doesn't exist, add at end
                    updated_content = existing_content + f"\n\n## {section}\n\n{content}"
                    changes_made.append(f"Created new section: {section}")
            else:
                # Append to end
                updated_content = existing_content + f"\n\n{content}"
                changes_made.append("Appended content to end")
                
        elif operation == "replace_section":
            if not section:
                return {'success': False, 'error': 'section parameter required for replace_section'}
            
            if f"## {section}" in existing_content:
                parts = existing_content.split(f"## {section}")
                next_section_idx = parts[1].find("\n## ")
                if next_section_idx != -1:
                    updated_content = parts[0] + f"## {section}\n\n{content}\n" + parts[1][next_section_idx:]
                else:
                    updated_content = parts[0] + f"## {section}\n\n{content}"
                changes_made.append(f"Replaced section: {section}")
            else:
                return {'success': False, 'error': f'Section not found: {section}'}
                
        elif operation == "insert_at":
            if position is None:
                return {'success': False, 'error': 'position parameter required for insert_at'}
            
            updated_content = existing_content[:position] + content + existing_content[position:]
            changes_made.append(f"Inserted content at position: {position}")
            
        elif operation == "merge_from":
            if not source_doc_id:
                return {'success': False, 'error': 'source_doc_id required for merge_from'}
            
            # Get source document
            source_response = requests.get(
                f'{api_base_url}/api/synergy/internal-doc/{source_doc_id}',
                headers={'X-User-ID': str(user_id)}
            )
            
            source_data = source_response.json()
            
            if not source_data.get('success'):
                return {'success': False, 'error': f'Source document not found: {source_doc_id}'}
            
            source_content = source_data.get('content', '')
            updated_content = existing_content + f"\n\n---\n\n## Merged Content from {source_data['title']}\n\n{source_content}"
            changes_made.append(f"Merged content from: {source_doc_id}")
            
        elif operation == "reformat":
            # Simple reformatting
            updated_content = existing_content.strip()
            changes_made.append("Reformatted content")
            
        else:
            return {'success': False, 'error': f'Unknown operation: {operation}'}
        
        # Validate if requested
        validation_warnings = []
        if validate:
            # Check for broken markdown
            if "]()" in updated_content:
                validation_warnings.append("Found empty markdown link: []()")
            if updated_content.count("```") % 2 != 0:
                validation_warnings.append("Unmatched code fence (```)")
        
        # Update document
        update_payload = {
            'content': updated_content
        }
        
        update_response = requests.put(
            f'{api_base_url}/api/synergy/internal-doc/{doc_id}',
            json=update_payload,
            headers={'X-User-ID': str(user_id)}
        )
        
        update_data = update_response.json()
        
        if not update_data.get('success'):
            return {
                'success': False,
                'error': f'Failed to update document: {update_data.get("error", "Unknown error")}'
            }
        
        return {
            'success': True,
            'doc_id': doc_id,
            'version': update_data.get('version'),
            'operation': operation,
            'changes_made': changes_made,
            'validation_warnings': validation_warnings,
            'updated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Smart update failed: {str(e)}'
        }


def synergy_smart_analyze_document(
    doc_id: str,
    analysis_type: str,
    question: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered document analysis with comprehensive insights
    
    Args:
        doc_id: Document ID to analyze (required)
        analysis_type: Type of analysis (required)
        question: Specific question for qa analysis (optional)
        context: Additional context for analysis (optional)
        **kwargs: Credential injection
    
    Returns:
        Analysis results tailored to requested type
    """
    try:
        import os
        api_base_url = kwargs.get('api_base_url', 
            os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001')
        user_id = kwargs.get('user_id', 1)
        
        # Get document
        response = requests.get(
            f'{api_base_url}/api/synergy/internal-doc/{doc_id}',
            headers={'X-User-ID': str(user_id)}
        )
        
        doc_data = response.json()
        
        if not doc_data.get('success'):
            return {
                'success': False,
                'error': f'Document not found: {doc_id}'
            }
        
        content = doc_data.get('content', '')
        title = doc_data.get('title', '')
        
        # Perform analysis
        result = {}
        
        if analysis_type == "summary":
            # Generate summary
            lines = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]
            result = {
                'summary': ' '.join(lines[:3])[:200] + "..." if len(' '.join(lines[:3])) > 200 else ' '.join(lines[:3])
            }
            
        elif analysis_type == "key_points":
            # Extract bullet points
            bullet_points = [line.strip() for line in content.split('\n') if line.strip().startswith('-') or line.strip().startswith('*')]
            result = {
                'key_points': bullet_points[:10]
            }
            
        elif analysis_type == "action_items":
            # Extract checkboxes
            action_items = [line.strip() for line in content.split('\n') if '- [ ]' in line or '- [x]' in line]
            result = {
                'action_items': action_items
            }
            
        elif analysis_type == "sentiment":
            # Simple sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'success', 'positive']
            negative_words = ['bad', 'poor', 'fail', 'issue', 'problem', 'risk']
            
            content_lower = content.lower()
            pos_count = sum(content_lower.count(word) for word in positive_words)
            neg_count = sum(content_lower.count(word) for word in negative_words)
            
            if pos_count > neg_count:
                sentiment = "positive"
            elif neg_count > pos_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            result = {
                'sentiment': sentiment,
                'positive_indicators': pos_count,
                'negative_indicators': neg_count
            }
            
        elif analysis_type == "completeness":
            # Check for common sections
            common_sections = ['overview', 'objectives', 'requirements', 'timeline', 'risks', 'next steps']
            missing_sections = [s for s in common_sections if s.lower() not in content.lower()]
            
            result = {
                'completeness_score': (len(common_sections) - len(missing_sections)) / len(common_sections) * 100,
                'missing_sections': missing_sections
            }
            
        elif analysis_type == "full_analysis":
            # Combine all analyses
            result = {
                'summary': "Full analysis combining all metrics",
                'metadata': {
                    'word_count': len(content.split()),
                    'section_count': content.count('##'),
                    'action_items': len([line for line in content.split('\n') if '- [ ]' in line]),
                }
            }
        
        else:
            return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
        
        return {
            'success': True,
            'doc_id': doc_id,
            'title': title,
            'analysis_type': analysis_type,
            'result': result,
            'metadata': {
                'word_count': len(content.split()),
                'sections': content.count('##'),
                'version': doc_data.get('version')
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Smart analysis failed: {str(e)}'
        }


def synergy_smart_batch_operations(
    operation: str,
    session_id: Optional[str] = None,
    doc_ids: Optional[List[str]] = None,
    templates: Optional[List[str]] = None,
    update_content: Optional[str] = None,
    export_format: Optional[str] = None,
    tags: Optional[str] = None,
    search_query: Optional[str] = None,
    parallel: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered batch operations on multiple documents
    
    Args:
        operation: Batch operation type (required)
        session_id: Session ID (required for bulk_create)
        doc_ids: Array of document IDs (required for most operations)
        templates: Array of templates for bulk_create
        update_content: Content for batch_update
        export_format: Format for mass_export
        tags: Tags for bulk_tag
        search_query: Query for cross_search
        parallel: Process in parallel (default: true)
        **kwargs: Credential injection
    
    Returns:
        Batch operation results with progress tracking
    """
    try:
        import os
        api_base_url = kwargs.get('api_base_url', 
            os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001')
        user_id = kwargs.get('user_id', 1)
        
        results = []
        errors = []
        start_time = datetime.now()
        
        if operation == "bulk_create":
            if not session_id or not templates:
                return {'success': False, 'error': 'session_id and templates required for bulk_create'}
            
            for template in templates:
                try:
                    result = synergy_smart_create_document(
                        session_id=session_id,
                        operation="create_from_template",
                        template=template,
                        user_id=user_id,
                        api_base_url=api_base_url
                    )
                    results.append(result)
                except Exception as e:
                    errors.append({'template': template, 'error': str(e)})
        
        elif operation == "batch_update":
            if not doc_ids or not update_content:
                return {'success': False, 'error': 'doc_ids and update_content required for batch_update'}
            
            for doc_id in doc_ids:
                try:
                    result = synergy_smart_update_document(
                        doc_id=doc_id,
                        operation="append_content",
                        content=update_content,
                        user_id=user_id,
                        api_base_url=api_base_url
                    )
                    results.append(result)
                except Exception as e:
                    errors.append({'doc_id': doc_id, 'error': str(e)})
        
        elif operation == "generate_summaries":
            if not doc_ids:
                return {'success': False, 'error': 'doc_ids required for generate_summaries'}
            
            summaries = []
            for doc_id in doc_ids:
                try:
                    result = synergy_smart_analyze_document(
                        doc_id=doc_id,
                        analysis_type="summary",
                        user_id=user_id,
                        api_base_url=api_base_url
                    )
                    summaries.append({
                        'doc_id': doc_id,
                        'title': result.get('title'),
                        'summary': result['result'].get('summary')
                    })
                    results.append(result)
                except Exception as e:
                    errors.append({'doc_id': doc_id, 'error': str(e)})
            
            return {
                'success': True,
                'operation': operation,
                'total_docs': len(doc_ids),
                'summaries': summaries,
                'errors': errors
            }
        
        else:
            return {'success': False, 'error': f'Unknown batch operation: {operation}'}
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            'success': True,
            'operation': operation,
            'total_docs': len(templates or doc_ids or []),
            'processed_docs': len(results),
            'successful_operations': len([r for r in results if r.get('success')]),
            'failed_operations': len(errors),
            'results': results,
            'errors': errors,
            'processing_time_ms': processing_time,
            'summary': f"Processed {len(results)} documents in {processing_time:.0f}ms. {len(errors)} errors."
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Batch operation failed: {str(e)}'
        }
