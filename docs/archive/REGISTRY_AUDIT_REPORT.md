
# REGISTRY AUDIT REPORT
**Date:** November 3, 2025  
**Status:** COMPLETE  

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Tools in Schemas** | 606 |
| **Tools with Implementation** | 606 |
| **Phantom Tools (no impl)** | 0 |
| **Success Rate** | 100.0% |
| **Platforms** | 33 |

---

## KEY FINDINGS

### 1. Phantom Tools
**Finding:** 0 tools defined in schemas have NO implementations

**Phantom Rate:** 0.0%

**Impact:** Users discover these tools but can't execute them

### 2. Authentication Requirements
**Gmail Tools:** 0 require authentication  
**Google Tools:** 0 require authentication  
**Microsoft Tools:** 0 require authentication  
**Other Tools:** 0 require authentication  

**Issue:** Authentication requirements are inconsistently documented

### 3. Parameter Type Issues
**Found:** 0 tools with potential parameter type mismatches

Examples:


### 4. Platform Distribution

Top 10 Platforms:

- **unknown**: 115 tools (115 with impl, 100%)
- **gmail**: 37 tools (37 with impl, 100%)
- **google_docs**: 31 tools (31 with impl, 100%)
- **woocommerce**: 29 tools (29 with impl, 100%)
- **google_forms**: 25 tools (25 with impl, 100%)
- **stripe**: 25 tools (25 with impl, 100%)
- **supabase**: 25 tools (25 with impl, 100%)
- **slack**: 24 tools (24 with impl, 100%)
- **microsoft_onedrive**: 23 tools (23 with impl, 100%)
- **microsoft_outlook**: 23 tools (23 with impl, 100%)

---

## DETAILED ANALYSIS

### Tools WITH Implementation (606)

These tools have working implementations:


#### ai_personal_tasks (7 tools)
- `ai_check_pending_work`
- `ai_complete_task`
- `ai_create_project_tasks`
- `ai_create_task`
- `ai_list_my_tasks`
- `ai_organize_tasks`
- `ai_update_task`

#### assemblyai (4 tools)
- `assemblyai_analyze`
- `assemblyai_speakers`
- `assemblyai_status`
- `assemblyai_transcribe`

#### cloudconvert (4 tools)
- `cloudconvert_convert`
- `cloudconvert_merge`
- `cloudconvert_optimize`
- `cloudconvert_status`

#### cloudflare (4 tools)
- `cloudflare_deploy_worker`
- `cloudflare_get_worker_logs`
- `cloudflare_list_workers`
- `cloudflare_worker_status`

#### github (4 tools)
- `github_commit_file`
- `github_create_pr`
- `github_create_repo`
- `github_get_issues`

#### gmail (37 tools)
- `gmail_ai_smart_compose_and_send`
- `gmail_archive_message`
- `gmail_batch_delete`
- `gmail_batch_modify`
- `gmail_create_draft`
- `gmail_create_filter`
- `gmail_create_label`
- `gmail_delete_filter`
- `gmail_delete_label`
- `gmail_delete_message`
- ... and 27 more

#### google_analytics (12 tools)
- `google_analytics_get_conversions`
- `google_analytics_get_demographics`
- `google_analytics_get_device_data`
- `google_analytics_get_events`
- `google_analytics_get_page_views`
- `google_analytics_get_realtime_report`
- `google_analytics_get_top_pages`
- `google_analytics_get_traffic_sources`
- `google_analytics_get_user_behavior`
- `google_analytics_list_accounts`
- ... and 2 more

#### google_calendar (12 tools)
- `google_calendar_add_reminder`
- `google_calendar_check_availability`
- `google_calendar_create_event`
- `google_calendar_delete_event`
- `google_calendar_get_calendar`
- `google_calendar_get_colors`
- `google_calendar_get_event`
- `google_calendar_list_calendars`
- `google_calendar_list_events`
- `google_calendar_move_event`
- ... and 2 more

#### google_cloud_run (15 tools)
- `google_cloud_run_create_job`
- `google_cloud_run_delete_service`
- `google_cloud_run_deploy_service`
- `google_cloud_run_execute_job`
- `google_cloud_run_get_job_executions`
- `google_cloud_run_get_service`
- `google_cloud_run_get_service_logs`
- `google_cloud_run_get_service_metrics`
- `google_cloud_run_get_service_url`
- `google_cloud_run_list_jobs`
- ... and 5 more

#### google_docs (31 tools)
- `google_docs_add_formatted_content`
- `google_docs_add_page_numbers`
- `google_docs_ai_smart_generate_document`
- `google_docs_append_text`
- `google_docs_batch_update`
- `google_docs_create_document`
- `google_docs_create_from_template`
- `google_docs_create_heading`
- `google_docs_create_list`
- `google_docs_create_named_range`
- ... and 21 more

#### google_drive (15 tools)
- `google_drive_copy_file`
- `google_drive_create_folder`
- `google_drive_delete_file`
- `google_drive_export_file`
- `google_drive_get_file`
- `google_drive_get_storage_quota`
- `google_drive_list_files`
- `google_drive_list_permissions`
- `google_drive_move_file`
- `google_drive_remove_permission`
- ... and 5 more

#### google_forms (25 tools)
- `google_forms_add_checkbox`
- `google_forms_add_linear_scale`
- `google_forms_add_multiple_choice`
- `google_forms_add_question`
- `google_forms_add_quiz_question`
- `google_forms_add_text_question`
- `google_forms_ai_analyze_responses`
- `google_forms_ai_generate_form`
- `google_forms_batch_add_questions`
- `google_forms_bulk_create_multiple`
- ... and 15 more

#### google_meet (14 tools)
- `google_meet_cancel_meeting`
- `google_meet_create_daily_standup`
- `google_meet_create_instant_meeting`
- `google_meet_create_meeting`
- `google_meet_create_space`
- `google_meet_create_team_meeting_with_agenda`
- `google_meet_create_weekly_review`
- `google_meet_get_join_info`
- `google_meet_get_meeting_details`
- `google_meet_get_space`
- ... and 4 more

#### google_sheets (4 tools)
- `google_charts_create`
- `gsheets_ai_generate_table`
- `gsheets_bulk_create_multiple`
- `gsheets_create_complete_spreadsheet`

#### google_tasks (12 tools)
- `google_tasks_complete_task`
- `google_tasks_create_task`
- `google_tasks_create_task_list`
- `google_tasks_delete_task`
- `google_tasks_delete_task_list`
- `google_tasks_get_task_list`
- `google_tasks_list_task_lists`
- `google_tasks_list_tasks`
- `google_tasks_smart_bulk_complete`
- `google_tasks_smart_create_project`
- ... and 2 more

#### gsheets (4 tools)
- `gsheets_append`
- `gsheets_create`
- `gsheets_read`
- `gsheets_write`

#### inhouse_database (5 tools)
- `db_calculate_quote`
- `db_execute_query`
- `db_get_available_queries`
- `db_get_business_summary`
- `db_get_stock_levels`

#### instagram (20 tools)
- `instagram_delete_comment`
- `instagram_get_account_info`
- `instagram_get_account_insights`
- `instagram_get_audience_insights`
- `instagram_get_comment`
- `instagram_get_comments`
- `instagram_get_hashtag_id`
- `instagram_get_media`
- `instagram_get_media_insights`
- `instagram_get_mentioned_media`
- ... and 10 more

#### meta_tools (8 tools)
- `execute_tool`
- `get_platform_guide`
- `get_tool_schema`
- `get_workflow_steps`
- `list_available_platforms`
- `list_platform_tools`
- `recommend_tools_for_task`
- `search_tools`

#### microsoft_calendar (17 tools)
- `calendar_book_room`
- `calendar_create_calendar`
- `calendar_create_event`
- `calendar_create_recurring_event`
- `calendar_delete_event`
- `calendar_find_meeting_rooms`
- `calendar_get_availability`
- `calendar_get_event`
- `calendar_get_reminders`
- `calendar_list_calendars`
- ... and 7 more

#### microsoft_onedrive (23 tools)
- `onedrive_copy_item`
- `onedrive_create_folder`
- `onedrive_create_share_link`
- `onedrive_delete_item`
- `onedrive_download_file`
- `onedrive_get_file_info`
- `onedrive_get_file_versions`
- `onedrive_get_permissions`
- `onedrive_get_recent_files`
- `onedrive_get_storage_info`
- ... and 13 more

#### microsoft_outlook (23 tools)
- `outlook_add_category`
- `outlook_create_draft`
- `outlook_create_folder`
- `outlook_create_inbox_rule`
- `outlook_delete_message`
- `outlook_download_attachment`
- `outlook_flag_message`
- `outlook_forward_message`
- `outlook_get_attachments`
- `outlook_get_message`
- ... and 13 more

#### microsoft_teams (22 tools)
- `teams_add_member`
- `teams_create_channel`
- `teams_create_meeting`
- `teams_create_team`
- `teams_get_channel_messages`
- `teams_get_channel_tabs`
- `teams_get_team`
- `teams_list_channel_files`
- `teams_list_channels`
- `teams_list_members`
- ... and 12 more

#### microsoft_todo (22 tools)
- `planner_add_checklist`
- `planner_assign_task`
- `planner_create_bucket`
- `planner_create_plan`
- `planner_create_task`
- `planner_get_plan_progress`
- `planner_list_buckets`
- `planner_list_plans`
- `planner_list_tasks`
- `planner_smart_sprint_setup`
- ... and 12 more

#### ngrok (4 tools)
- `ngrok_get_public_url`
- `ngrok_list_tunnels`
- `ngrok_start_tunnel`
- `ngrok_stop_tunnel`

#### paypal (16 tools)
- `paypal_cancel_invoice`
- `paypal_capture_order`
- `paypal_create_invoice`
- `paypal_create_order`
- `paypal_create_payout`
- `paypal_create_refund`
- `paypal_get_invoice`
- `paypal_get_order`
- `paypal_get_payout`
- `paypal_get_payout_item`
- ... and 6 more

#### slack (24 tools)
- `slack_add_reaction`
- `slack_archive_channel`
- `slack_create_channel`
- `slack_delete_file`
- `slack_delete_message`
- `slack_get_channel_history`
- `slack_get_channel_info`
- `slack_get_file_info`
- `slack_get_message_permalink`
- `slack_get_user_info`
- ... and 14 more

#### stripe (25 tools)
- `stripe_attach_payment_method`
- `stripe_cancel_subscription`
- `stripe_capture_payment`
- `stripe_confirm_payment`
- `stripe_create_customer`
- `stripe_create_invoice`
- `stripe_create_payment_intent`
- `stripe_create_price`
- `stripe_create_product`
- `stripe_create_refund`
- ... and 15 more

#### supabase (25 tools)
- `supabase_auth_get_user`
- `supabase_auth_invite_user`
- `supabase_auth_reset_password`
- `supabase_auth_signin`
- `supabase_auth_signout`
- `supabase_auth_signup`
- `supabase_auth_update_user`
- `supabase_count`
- `supabase_create_bucket`
- `supabase_delete`
- ... and 15 more

#### synergy (8 tools)
- `synergy_create_session`
- `synergy_delete_session`
- `synergy_get_session`
- `synergy_list_sessions`
- `synergy_move_session`
- `synergy_smart_project_tracker`
- `synergy_sync_to_google`
- `synergy_update_session`

#### twilio (16 tools)
- `twilio_complete_video_room`
- `twilio_create_video_room`
- `twilio_get_call`
- `twilio_get_message`
- `twilio_get_video_room`
- `twilio_list_calls`
- `twilio_list_messages`
- `twilio_list_phone_numbers`
- `twilio_list_video_rooms`
- `twilio_make_call`
- ... and 6 more

#### unknown (115 tools)
- `calculate_booklets`
- `calculate_business_cards`
- `calculate_corflute_signs`
- `calculate_flyers`
- `calculate_perfect_bound_books`
- `excel_add_worksheet`
- `excel_calculate`
- `excel_clear_range`
- `excel_create_chart`
- `excel_create_workbook`
- ... and 105 more

#### woocommerce (29 tools)
- `woocommerce_create_category`
- `woocommerce_create_coupon`
- `woocommerce_create_customer`
- `woocommerce_create_order`
- `woocommerce_create_order_note`
- `woocommerce_create_product`
- `woocommerce_create_refund`
- `woocommerce_create_webhook`
- `woocommerce_delete_order`
- `woocommerce_delete_product`
- ... and 19 more


### Tools WITHOUT Implementation (PHANTOM) (0)

These tools are defined in schemas but have NO implementations:



---

## AUTHENTICATION ANALYSIS

### Gmail Tools Requiring Auth (0)



### Google Tools Requiring Auth (0)



### Microsoft Tools Requiring Auth (0)



---

## PARAMETER TYPE ISSUES

### Type Mismatches Found (0)

Tools with incorrect parameter types in schemas:



---

## TEST RESULTS

### Tools That Can Be Found in Registry

✅ Working: 5
- gsheets_create, gmail_send_email, synergy_update_session, google_calendar_create_event, google_forms_create_form

❌ Not Found: 0
- 

⚠️  Errors: 0


---

## RECOMMENDATIONS

### CRITICAL (Fix Immediately)

1. **Remove Phantom Tools from Discovery**
   - 0 tools are returning "tool not found" errors
   - Update `list_platform_tools()` and `search_tools()` to only return implemented tools
   - Impact: Eliminate 50% of tool execution failures

2. **Document Authentication Requirements**
   - 0 tools need auth parameters
   - Add `_user_id` and `_injected_credentials` to schemas where required
   - Impact: Users know what parameters they need

3. **Fix Parameter Type Definitions**
   - 0 tools have wrong parameter types
   - Update schemas to match implementation requirements
   - Impact: Users can format data correctly

### HIGH (Fix Soon)

4. **Validate Implementations on Registry Load**
   - When registry loads a schema, verify implementation exists
   - Only add tools to registry that have real implementations
   - Impact: Discovery becomes trustworthy

5. **Create Verified Working Tools List**
   - Document which 606 tools actually work
   - Include test cases for each
   - Impact: Users have reliable reference

---

## STATISTICS

```
Registry Status:
  Total Schemas:       606 tools
  With Impl:           606 tools (100.0%)
  Phantom (no impl):   0 tools (0.0%)
  
Platform Breakdown:
  Total Platforms:     33
  Largest Platform:    unknown (115 tools)
  
Authentication:
  Gmail Tools:         0 need auth
  Google Tools:        0 need auth
  Microsoft Tools:     0 need auth
  
Quality Issues:
  Parameter Type Issues: 0
  
Test Results:
  Working:             5
  Not Found:           0
  Errors:              0
```

---

## NEXT STEPS

**Phase 1 - Verification (30 min):**
- [ ] Audit schema vs implementation files
- [ ] Generate complete phantom tools list
- [ ] Identify which tools are actually used

**Phase 2 - Fix Critical Issues (2-4 hours):**
- [ ] Remove phantom tools from discovery
- [ ] Add auth parameters to schemas
- [ ] Fix parameter type mismatches
- [ ] Fix error propagation

**Phase 3 - Validation (1 hour):**
- [ ] Test all 606 working tools
- [ ] Create verified working tools list
- [ ] Update documentation

---

**Report Generated:** audit_registry.py  
**Analysis Time:** 5-10 minutes  
**Status:** Ready for Phase 2 fixes
