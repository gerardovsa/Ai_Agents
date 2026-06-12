# Token Reduction Examples - Before vs After

## Real-World Comparison Across All Google Platforms

---

## 📄 Google Docs Example

### Document: "Q4 Sales Report" (237,366 tokens before)

### ❌ BEFORE (Old Method):
```json
{
  "documentId": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "title": "Q4 Sales Report",
  "body": {
    "content": [
      {
        "startIndex": 1,
        "endIndex": 45,
        "paragraph": {
          "elements": [
            {
              "startIndex": 1,
              "endIndex": 44,
              "textRun": {
                "content": "Q4 Sales Performance - Executive Summary\n",
                "textStyle": {
                  "bold": true,
                  "italic": false,
                  "underline": false,
                  "strikethrough": false,
                  "smallCaps": false,
                  "backgroundColor": {},
                  "foregroundColor": {
                    "color": {
                      "rgbColor": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                      }
                    }
                  },
                  "fontSize": {
                    "magnitude": 18,
                    "unit": "PT"
                  },
                  "weightedFontFamily": {
                    "fontFamily": "Arial",
                    "weight": 700
                  },
                  "baselineOffset": "NONE",
                  "link": null
                }
              }
            }
          ],
          "paragraphStyle": {
            "namedStyleType": "HEADING_1",
            "alignment": "START",
            "lineSpacing": 115,
            "direction": "LEFT_TO_RIGHT",
            "spacingMode": "NEVER_COLLAPSE",
            "spaceAbove": {
              "magnitude": 20,
              "unit": "PT"
            },
            "spaceBelow": {
              "magnitude": 6,
              "unit": "PT"
            },
            "borderBetween": {
              "color": {},
              "width": {
                "magnitude": 0,
                "unit": "PT"
              },
              "padding": {
                "magnitude": 0,
                "unit": "PT"
              },
              "dashStyle": "SOLID"
            },
            "indentFirstLine": {
              "magnitude": 0,
              "unit": "PT"
            },
            "indentStart": {
              "magnitude": 0,
              "unit": "PT"
            },
            "indentEnd": {
              "magnitude": 0,
              "unit": "PT"
            }
          }
        }
      },
      ... (197 more paragraphs with identical verbose formatting) ...
    ]
  },
  "documentStyle": {
    "background": {
      "color": {
        "color": {
          "rgbColor": {
            "red": 1,
            "green": 1,
            "blue": 1
          }
        }
      }
    },
    "pageNumberStart": 1,
    "marginTop": {
      "magnitude": 72,
      "unit": "PT"
    },
    "marginBottom": {
      "magnitude": 72,
      "unit": "PT"
    },
    "marginRight": {
      "magnitude": 72,
      "unit": "PT"
    },
    "marginLeft": {
      "magnitude": 72,
      "unit": "PT"
    },
    "pageSize": {
      "height": {
        "magnitude": 792,
        "unit": "PT"
      },
      "width": {
        "magnitude": 612,
        "unit": "PT"
      }
    },
    "marginHeader": {
      "magnitude": 36,
      "unit": "PT"
    },
    "marginFooter": {
      "magnitude": 36,
      "unit": "PT"
    },
    "useCustomHeaderFooterMargins": true,
    "evenPageHeaderId": "",
    "evenPageFooterId": "",
    "firstPageHeaderId": "",
    "firstPageFooterId": "",
    "defaultHeaderId": "kix.header1",
    "defaultFooterId": "kix.footer1",
    "flipPageOrientation": false
  },
  "revisionId": "ALm37BWTiN_C6...",
  "suggestionsViewMode": "SUGGESTIONS_INLINE",
  "namedStyles": {
    "styles": [
      {
        "namedStyleType": "NORMAL_TEXT",
        "textStyle": {
          "bold": false,
          "italic": false,
          "underline": false,
          "strikethrough": false,
          "smallCaps": false,
          "backgroundColor": {},
          "foregroundColor": {
            "color": {
              "rgbColor": {
                "red": 0,
                "green": 0,
                "blue": 0
              }
            }
          },
          "fontSize": {
            "magnitude": 11,
            "unit": "PT"
          },
          "weightedFontFamily": {
            "fontFamily": "Arial",
            "weight": 400
          },
          "baselineOffset": "NONE"
        },
        "paragraphStyle": {
          "namedStyleType": "NORMAL_TEXT",
          "alignment": "START",
          "lineSpacing": 115,
          "direction": "LEFT_TO_RIGHT"
        }
      },
      ... (28 more style definitions) ...
    ]
  },
  "lists": {},
  "footnotes": {},
  "headers": {
    "kix.header1": {
      "headerId": "kix.header1",
      "content": [...]
    }
  },
  "footers": {
    "kix.footer1": {
      "footerId": "kix.footer1",
      "content": [...]
    }
  }
}
```

**Tokens:** 237,366 tokens  
**Problem:** 95% of this is repetitive formatting metadata!

---

### ✅ AFTER (New Method - Three Steps):

#### Step 1: Get Structure (500 tokens)
```python
google_docs_get_document(
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0',
    format='summary'  # DEFAULT
)
```

**Returns:**
```json
{
  "success": true,
  "title": "Q4 Sales Report",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "preview": "Q4 Sales Performance - Executive Summary\n\nOverall Performance\nTotal Revenue: $4.2M (18% increase YoY)\nNew Customers: 156 (23% increase)\nAverage Deal Size: $26,923 (5% increase)\n\nRegional Breakdown:\n\nNorth America: $2.1M (50% of total)\n- Enterprise segment leading with 34% growth\n- SMB segment stable at 8% growth\n\nEurope: $1.3M (31% of total)\n- Strong growth in DACH region (28%)\n- UK market recovering (12% growth)\n\nAPAC: $800K (19% of total)\n- Explosive growth in Southeast Asia (45%)\n- Australia/NZ maintaining steady 15% growth\n\nProduct Performance:\n\nEnterprise Suite: $2.5M (60% of revenue)\n- Strong adoption of new AI features\n- 89% renewal rate\n\nProfessional Edition: $1.2M (29% of revenue)\n- Popular with mid-market\n- Upsell opportunities identified\n\nStarter Package: $500K (11% of revenue)\n- High volume, lower margin\n- Gateway to enterprise deals\n\nKey Wins:\n1. Acme Corp - $850K enterprise deal (largest this quarter)\n2. TechStart Inc - $320K multi-year contract\n3. Global Solutions - $280K expansion\n\nChallenges:\n- Sales cycle lengthening (avg 87 days, up from 72)\n- Increased competition in mid-market\n- Economic headwinds affecting Q1 pipeline\n\nQ1 Forecast:\nConservative: $3.8M\nRealistic: $4.5M\nOptimistic: $5.2M\n\nRecommendations:\n1. Accelerate enterprise sales with dedicated team\n2. Enhance mid-market offering...",
  "preview_length": 2000,
  "format": "summary",
  "revision_id": "ALm37BWTiN_C6...",
  "note": "Use format='text' or format='markdown' for full content, or use google_docs_search_document() for specific queries"
}
```

**Tokens:** ~500 tokens (99.8% reduction!)  
**Content:** Full 2000 char preview showing actual text  
**AI can see:** Document structure, topics, and enough context to know what questions to ask

---

#### Step 2: Get Full Text Content (50,000 tokens)
```python
google_docs_get_document(
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0',
    format='text'  # Just the text, no formatting
)
```

**Returns:**
```json
{
  "success": true,
  "title": "Q4 Sales Report",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "text": "Q4 Sales Performance - Executive Summary\n\nOverall Performance\nTotal Revenue: $4.2M (18% increase YoY)\nNew Customers: 156 (23% increase)\nAverage Deal Size: $26,923 (5% increase)\n\nRegional Breakdown:\n\nNorth America: $2.1M (50% of total)\n- Enterprise segment leading with 34% growth\n- SMB segment stable at 8% growth\n\nEurope: $1.3M (31% of total)\n- Strong growth in DACH region (28%)\n- UK market recovering (12% growth)\n\nAPAC: $800K (19% of total)\n- Explosive growth in Southeast Asia (45%)\n- Australia/NZ maintaining steady 15% growth\n\n[... FULL 50 pages of actual content with NO formatting metadata ...]\n\nConclusion\nQ4 exceeded expectations across all metrics. Strong foundation for Q1 with robust pipeline and proven product-market fit in enterprise segment. Recommend doubling down on enterprise while maintaining mid-market momentum.",
  "text_length": 45230,
  "format": "text",
  "revision_id": "ALm37BWTiN_C6..."
}
```

**Tokens:** ~50,000 tokens (79% reduction from original!)  
**Content:** EVERY WORD from the document, zero formatting metadata  
**AI can see:** Complete document content in pure text form

---

#### Step 3: Search for Specific Content (2,000 tokens)
```python
google_docs_search_document(
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0',
    query='APAC growth',
    context_chars=800
)
```

**Returns:**
```json
{
  "success": true,
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "title": "Q4 Sales Report",
  "query": "APAC growth",
  "matches": [
    {
      "match_number": 1,
      "context": "...Europe: $1.3M (31% of total)\n- Strong growth in DACH region (28%)\n- UK market recovering (12% growth)\n\n>>> APAC: $800K (19% of total)\n- Explosive growth in Southeast Asia (45%)\n- Australia/NZ maintaining steady 15% growth <<<\n\nProduct Performance:\n\nEnterprise Suite: $2.5M (60% of revenue)..."
    },
    {
      "match_number": 2,
      "context": "...Regional Deep Dive\n\n>>> APAC Growth Strategy\nSoutheast Asia expansion exceeded projections with 45% quarter-over-quarter growth. <<<\nKey drivers:\n- Strategic partnership with regional distributor\n- Localized product offering\n- Competitive pricing for emerging markets..."
    }
  ],
  "match_count": 2,
  "total_context_length": 1650
}
```

**Tokens:** ~2,000 tokens (99.2% reduction from original!)  
**Content:** Only the relevant sections mentioning APAC growth  
**AI can see:** Exact information needed without reading entire document

---

## 📊 Google Slides Example

### Presentation: "Company All-Hands" (150,000 tokens before)

### ❌ BEFORE (Old Method):
```json
{
  "presentationId": "1a2b3c4d5e6f",
  "pageSize": {
    "height": {
      "magnitude": 5400000,
      "unit": "EMU"
    },
    "width": {
      "magnitude": 9600000,
      "unit": "EMU"
    }
  },
  "slides": [
    {
      "objectId": "slide1",
      "slideProperties": {
        "layoutObjectId": "layout1",
        "masterObjectId": "master1",
        "notesPage": {
          "notesProperties": {},
          "pageElements": [
            {
              "objectId": "notes1",
              "size": {
                "height": {
                  "magnitude": 2000000,
                  "unit": "EMU"
                },
                "width": {
                  "magnitude": 9600000,
                  "unit": "EMU"
                }
              },
              "transform": {
                "scaleX": 1,
                "scaleY": 1,
                "translateX": 0,
                "translateY": 0,
                "unit": "EMU"
              },
              "shape": {
                "shapeType": "TEXT_BOX",
                "text": {
                  "textElements": [
                    {
                      "textRun": {
                        "content": "Speaker notes for slide 1\n",
                        "style": {
                          "bold": false,
                          "italic": false,
                          "underline": false,
                          "strikethrough": false,
                          "smallCaps": false,
                          "backgroundColor": {
                            "opaqueColor": {
                              "rgbColor": {}
                            }
                          },
                          "foregroundColor": {
                            "opaqueColor": {
                              "rgbColor": {
                                "red": 0,
                                "green": 0,
                                "blue": 0
                              }
                            }
                          },
                          "fontSize": {
                            "magnitude": 11,
                            "unit": "PT"
                          },
                          "fontFamily": "Arial",
                          "link": null,
                          "baselineOffset": "NONE",
                          "weightedFontFamily": {
                            "fontFamily": "Arial",
                            "weight": 400
                          }
                        }
                      }
                    }
                  ],
                  "lists": {}
                },
                "shapeProperties": {
                  "shapeBackgroundFill": {
                    "solidFill": {
                      "color": {
                        "rgbColor": {
                          "red": 1,
                          "green": 1,
                          "blue": 1
                        }
                      },
                      "alpha": 1
                    }
                  },
                  "outline": {
                    "outlineFill": {
                      "solidFill": {
                        "color": {
                          "rgbColor": {
                            "red": 0,
                            "green": 0,
                            "blue": 0
                          }
                        },
                        "alpha": 1
                      }
                    },
                    "weight": {
                      "magnitude": 9525,
                      "unit": "EMU"
                    },
                    "dashStyle": "SOLID",
                    "propertyState": "RENDERED"
                  },
                  "contentAlignment": "TOP"
                }
              }
            }
          ]
        }
      },
      "pageElements": [
        {
          "objectId": "title1",
          "size": {
            "height": {
              "magnitude": 1234567,
              "unit": "EMU"
            },
            "width": {
              "magnitude": 8765432,
              "unit": "EMU"
            }
          },
          "transform": {
            "scaleX": 1,
            "scaleY": 1,
            "translateX": 500000,
            "translateY": 1000000,
            "unit": "EMU"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Q4 Company All-Hands\n",
                    "style": {
                      "bold": true,
                      "italic": false,
                      "fontSize": {
                        "magnitude": 44,
                        "unit": "PT"
                      },
                      "fontFamily": "Arial",
                      ... (30 more style properties) ...
                    }
                  }
                }
              ]
            }
          }
        },
        ... (8 more page elements with full positioning/styling) ...
      ]
    },
    ... (44 more slides with identical verbose structure) ...
  ],
  "layouts": [
    {
      "objectId": "layout1",
      "layoutProperties": {
        "masterObjectId": "master1",
        "name": "Title Slide",
        "displayName": "Title Slide"
      },
      "pageElements": [...]
    },
    ... (12 more layout definitions) ...
  ],
  "masters": [
    {
      "objectId": "master1",
      "pageProperties": {...},
      "pageElements": [...]
    }
  ]
}
```

**Tokens:** 150,000 tokens  
**Problem:** Massive positioning, sizing, and styling data for every element!

---

### ✅ AFTER (New Method - Three Steps):

#### Step 1: Get Slide Index (1,200 tokens)
```python
google_slides_get_presentation(
    presentation_id='1a2b3c4d5e6f',
    format='structure'  # DEFAULT
)
```

**Returns:**
```json
{
  "success": true,
  "presentation_id": "1a2b3c4d5e6f",
  "title": "Q4 Company All-Hands",
  "slide_count": 45,
  "format": "structure",
  "slides": [
    {
      "slide_number": 1,
      "object_id": "slide1",
      "layout": "Title Slide",
      "title": "Q4 Company All-Hands",
      "subtitle": "December 2024 - Team Update",
      "element_count": 3,
      "has_notes": true,
      "notes_preview": "Welcome everyone. Today we'll cover Q4 results, 2025 roadmap, and team updates."
    },
    {
      "slide_number": 2,
      "object_id": "slide2",
      "layout": "Section Header",
      "title": "Agenda",
      "element_count": 5,
      "has_notes": false
    },
    {
      "slide_number": 3,
      "object_id": "slide3",
      "layout": "Title and Body",
      "title": "Q4 Financial Results",
      "bullet_points": [
        "Revenue: $4.2M (18% growth)",
        "New customers: 156",
        "ARR: $15.8M"
      ],
      "element_count": 7,
      "has_notes": true,
      "notes_preview": "Emphasize the 18% growth - exceeds target of 15%. New customers..."
    },
    ... (42 more slide summaries)
  ]
}
```

**Tokens:** ~1,200 tokens (99.2% reduction!)  
**Content:** Title and preview of every slide  
**AI can see:** Full deck structure, can ask for specific slides

---

#### Step 2: Get Specific Slide (3,000 tokens)
```python
google_slides_get_slide(
    presentation_id='1a2b3c4d5e6f',
    slide_number=3
)
```

**Returns:**
```json
{
  "success": true,
  "presentation_id": "1a2b3c4d5e6f",
  "slide_number": 3,
  "object_id": "slide3",
  "title": "Q4 Financial Results",
  "layout": "Title and Body",
  "text_content": [
    "Q4 Financial Results",
    "Revenue: $4.2M (18% growth YoY)",
    "New customers: 156 (23% increase)",
    "ARR: $15.8M (quarterly growth of $2.1M)",
    "Churn rate: 2.3% (down from 3.1% in Q3)",
    "Average deal size: $26,923"
  ],
  "speaker_notes": "Emphasize the 18% growth - this exceeds our target of 15%. New customers metric particularly strong this quarter due to successful enterprise push. ARR growth of $2.1M QoQ shows healthy momentum. Churn reduction is a major win - thank the customer success team. Average deal size up 5% shows we're moving upmarket successfully.",
  "elements": {
    "text_boxes": 6,
    "images": 1,
    "charts": 1,
    "shapes": 3
  },
  "images": [
    {
      "title": "Revenue Chart",
      "description": "Bar chart showing quarterly revenue growth Q1-Q4"
    }
  ]
}
```

**Tokens:** ~3,000 tokens (98% reduction from getting full presentation!)  
**Content:** Complete text content from slide 3, speaker notes, element descriptions  
**AI can see:** Everything on the slide without positioning/styling metadata

---

#### Step 3: Search Across Slides (2,500 tokens)
```python
google_slides_search_presentation(
    presentation_id='1a2b3c4d5e6f',
    query='product roadmap'
)
```

**Returns:**
```json
{
  "success": true,
  "presentation_id": "1a2b3c4d5e6f",
  "query": "product roadmap",
  "matches": [
    {
      "slide_number": 15,
      "title": "2025 Product Roadmap",
      "matched_text": "Product Roadmap - H1 2025\n\n- AI-powered analytics (Q1 launch)\n- Mobile app v2.0 (Q2 launch)\n- Enterprise SSO (Q1)\n- Advanced reporting dashboard (Q2)",
      "speaker_notes": "Product roadmap is aggressive but achievable. AI analytics is priority #1..."
    },
    {
      "slide_number": 28,
      "title": "Engineering Priorities",
      "matched_text": "Aligning with product roadmap:\n- Hire 3 AI engineers (Jan-Feb)\n- Infrastructure upgrades (Q1)\n- Mobile team expansion (Q2)"
    }
  ],
  "match_count": 2
}
```

**Tokens:** ~2,500 tokens (98.3% reduction!)  
**Content:** Only slides mentioning product roadmap  
**AI can see:** Specific information without reading all 45 slides

---

## 📋 Google Forms Example

### Form: "Customer Feedback Survey" (80,000 tokens + 500,000 tokens for responses)

### ❌ BEFORE (Old Method):
```json
{
  "formId": "1xyz789",
  "info": {
    "title": "Customer Feedback Survey",
    "documentTitle": "Q4 Customer Feedback"
  },
  "items": [
    {
      "itemId": "q1",
      "title": "How satisfied are you with our product?",
      "questionItem": {
        "question": {
          "questionId": "q1_question",
          "required": true,
          "choiceQuestion": {
            "type": "RADIO",
            "options": [
              {
                "value": "Very Satisfied",
                "image": null,
                "isOther": false,
                "goToAction": "NEXT_SECTION",
                "goToSectionId": null
              },
              {
                "value": "Satisfied",
                "image": null,
                "isOther": false,
                "goToAction": "NEXT_SECTION",
                "goToSectionId": null
              },
              ... (3 more options with full metadata) ...
            ],
            "shuffle": false
          },
          "grading": null,
          "textQuestion": null,
          "scaleQuestion": null,
          "dateQuestion": null,
          "timeQuestion": null,
          "fileUploadQuestion": null,
          "choiceQuestion": {...},
          "rowQuestion": null
        }
      },
      "description": "",
      "questionGroupItem": null,
      "pageBreakItem": null,
      "textItem": null,
      "imageItem": null,
      "videoItem": null
    },
    ... (24 more questions with identical verbose structure) ...
  ],
  "settings": {
    "quizSettings": null,
    "responseCollectionSettings": {
      "collectEmail": true,
      "requireLogin": false,
      "isPublicUrlShareEnabled": true,
      "canEditResponse": false,
      "confirmationMessage": "Thank you for your feedback!",
      "publishResponse": false
    }
  },
  "linkedSheetId": null,
  "responderUri": "https://docs.google.com/forms/d/e/...",
  "revisionId": "000000ab"
}
```

**Plus 2,847 responses (500,000+ tokens):**
```json
{
  "responses": [
    {
      "responseId": "resp1",
      "createTime": "2024-11-15T10:23:45.123Z",
      "lastSubmittedTime": "2024-11-15T10:24:12.789Z",
      "respondentEmail": "user1@example.com",
      "answers": {
        "q1_question": {
          "questionId": "q1_question",
          "textAnswers": {
            "answers": [
              {
                "value": "Very Satisfied",
                "grade": null
              }
            ]
          },
          "fileUploadAnswers": null,
          "grading": null
        },
        ... (24 more answer objects) ...
      },
      "totalScore": null
    },
    ... (2,846 more responses with identical structure) ...
  ]
}
```

**Tokens:** 80,000 (form) + 500,000 (responses) = 580,000 tokens!  
**Problem:** ALL responses returned at once with verbose metadata!

---

### ✅ AFTER (New Method - Four Steps):

#### Step 1: Get Form Structure (1,500 tokens)
```python
google_forms_get_form(
    form_id='1xyz789',
    format='structure'  # DEFAULT
)
```

**Returns:**
```json
{
  "success": true,
  "form_id": "1xyz789",
  "title": "Customer Feedback Survey",
  "description": "Help us improve by sharing your feedback",
  "question_count": 25,
  "response_count": 2847,
  "format": "structure",
  "questions": [
    {
      "question_number": 1,
      "question_id": "q1_question",
      "title": "How satisfied are you with our product?",
      "type": "RADIO",
      "required": true,
      "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
    },
    {
      "question_number": 2,
      "question_id": "q2_question",
      "title": "What features do you use most?",
      "type": "CHECKBOX",
      "required": false,
      "options": ["Analytics", "Reporting", "Dashboards", "Integrations", "API"]
    },
    {
      "question_number": 3,
      "question_id": "q3_question",
      "title": "What could we improve?",
      "type": "PARAGRAPH",
      "required": false,
      "max_characters": 500
    },
    ... (22 more question summaries)
  ],
  "linked_sheet_id": "1abc456",
  "form_url": "https://docs.google.com/forms/d/1xyz789/edit"
}
```

**Tokens:** ~1,500 tokens (98.1% reduction from form structure!)  
**Content:** All questions with types and options  
**AI can see:** Form structure, question types, response count

---

#### Step 2: Get Response Summary (3,000 tokens)
```python
google_forms_get_response_summary(
    form_id='1xyz789'
)
```

**Returns:**
```json
{
  "success": true,
  "form_id": "1xyz789",
  "total_responses": 2847,
  "summary": [
    {
      "question": "How satisfied are you with our product?",
      "type": "RADIO",
      "responses": {
        "Very Satisfied": 1423,
        "Satisfied": 892,
        "Neutral": 312,
        "Dissatisfied": 156,
        "Very Dissatisfied": 64
      },
      "percentages": {
        "Very Satisfied": "50.0%",
        "Satisfied": "31.3%",
        "Neutral": "11.0%",
        "Dissatisfied": "5.5%",
        "Very Dissatisfied": "2.2%"
      }
    },
    {
      "question": "What features do you use most?",
      "type": "CHECKBOX",
      "responses": {
        "Analytics": 2145,
        "Reporting": 1876,
        "Dashboards": 1654,
        "Integrations": 987,
        "API": 543
      }
    },
    {
      "question": "What could we improve?",
      "type": "PARAGRAPH",
      "total_responses": 2341,
      "common_themes": [
        "Mobile app improvements (mentioned 892 times)",
        "Better documentation (mentioned 567 times)",
        "Performance issues (mentioned 432 times)",
        "More integrations (mentioned 398 times)"
      ]
    },
    ... (22 more question summaries)
  ]
}
```

**Tokens:** ~3,000 tokens (99.4% reduction from all responses!)  
**Content:** Aggregated response data, percentages, common themes  
**AI can see:** Overall feedback trends without individual responses

---

#### Step 3: Get Specific Responses (5,000 tokens for 100 responses)
```python
google_forms_get_responses(
    form_id='1xyz789',
    limit=100,  # DEFAULT
    filter={'question_id': 'q1_question', 'answer': 'Very Dissatisfied'}
)
```

**Returns:**
```json
{
  "success": true,
  "form_id": "1xyz789",
  "responses": [
    {
      "response_id": "resp2341",
      "submitted": "2024-11-20T14:35:22Z",
      "email": "frustrated@example.com",
      "answers": {
        "How satisfied are you with our product?": "Very Dissatisfied",
        "What could we improve?": "The mobile app is terrible. It crashes constantly and loses my data. I've lost hours of work because of this. Please fix it or I'm canceling my subscription.",
        "How likely to recommend?": "0 (Not at all likely)"
      }
    },
    ... (63 more dissatisfied responses - filtered)
  ],
  "returned_count": 64,
  "total_matching": 64,
  "has_more": false
}
```

**Tokens:** ~5,000 tokens (99% reduction from all 500K tokens!)  
**Content:** Only dissatisfied responses for deep dive  
**AI can see:** Specific feedback from unhappy customers

---

#### Step 4: Search Responses (4,000 tokens)
```python
google_forms_search_responses(
    form_id='1xyz789',
    query='mobile app crash'
)
```

**Returns:**
```json
{
  "success": true,
  "form_id": "1xyz789",
  "query": "mobile app crash",
  "matches": [
    {
      "response_id": "resp2341",
      "submitted": "2024-11-20T14:35:22Z",
      "matched_answer": "The mobile app is terrible. >>> It crashes constantly <<< and loses my data.",
      "satisfaction": "Very Dissatisfied"
    },
    {
      "response_id": "resp1876",
      "submitted": "2024-11-18T09:12:45Z",
      "matched_answer": "Love the desktop version but >>> mobile app crashes <<< daily on iOS 17",
      "satisfaction": "Neutral"
    },
    ... (89 more matches mentioning crashes)
  ],
  "match_count": 91,
  "total_responses_searched": 2847
}
```

**Tokens:** ~4,000 tokens (99.2% reduction!)  
**Content:** Only responses mentioning mobile app crashes  
**AI can see:** Specific issue feedback without reading all 2,847 responses

---

## 📊 Google Sheets Example

### Spreadsheet: "Sales Pipeline" (120,000 tokens)

### ❌ BEFORE (Old Method):
```json
{
  "spreadsheetId": "1sheet123",
  "properties": {
    "title": "Sales Pipeline 2024",
    "locale": "en_US",
    "autoRecalc": "ON_CHANGE",
    "timeZone": "America/Los_Angeles",
    "defaultFormat": {
      "backgroundColor": {
        "red": 1,
        "green": 1,
        "blue": 1
      },
      "padding": {
        "top": 2,
        "right": 3,
        "bottom": 2,
        "left": 3
      },
      "verticalAlignment": "BOTTOM",
      "wrapStrategy": "OVERFLOW_CELL",
      "textFormat": {
        "foregroundColor": {},
        "fontFamily": "arial,sans,sans-serif",
        "fontSize": 10,
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "foregroundColorStyle": {
          "rgbColor": {}
        }
      },
      "backgroundColorStyle": {
        "rgbColor": {
          "red": 1,
          "green": 1,
          "blue": 1
        }
      }
    }
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 0,
        "title": "Active Deals",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1243,
          "columnCount": 26,
          "frozenRowCount": 1
        }
      },
      "data": [
        {
          "rowData": [
            {
              "values": [
                {
                  "userEnteredValue": {
                    "stringValue": "Deal ID"
                  },
                  "effectiveValue": {
                    "stringValue": "Deal ID"
                  },
                  "formattedValue": "Deal ID",
                  "userEnteredFormat": {
                    "backgroundColor": {
                      "red": 0.2,
                      "green": 0.5,
                      "blue": 0.8
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "CLIP",
                    "textFormat": {
                      "foregroundColor": {
                        "red": 1,
                        "green": 1,
                        "blue": 1
                      },
                      "fontFamily": "Arial",
                      "fontSize": 12,
                      "bold": true,
                      "italic": false,
                      "strikethrough": false,
                      "underline": false
                    },
                    "borders": {
                      "top": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                          "red": 0,
                          "green": 0,
                          "blue": 0
                        }
                      },
                      "bottom": {
                        "style": "SOLID",
                        "width": 2,
                        "color": {
                          "red": 0,
                          "green": 0,
                          "blue": 0
                        }
                      },
                      "left": {...},
                      "right": {...}
                    }
                  },
                  "effectiveFormat": {...},
                  "hyperlink": null,
                  "note": null,
                  "textFormatRuns": [],
                  "dataValidation": null,
                  "pivotTable": null
                },
                ... (25 more header cells with identical verbose formatting) ...
              ]
            },
            ... (1,242 more rows with full formatting for each cell) ...
          ]
        }
      ],
      "merges": [],
      "conditionalFormats": [...],
      "filterViews": [],
      "protectedRanges": []
    },
    ... (4 more sheets with identical structure) ...
  ],
  "namedRanges": [...],
  "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1sheet123/edit"
}
```

**Tokens:** 120,000 tokens  
**Problem:** Cell-by-cell formatting data for 1,243 rows × 26 columns!

---

### ✅ AFTER (New Method - Four Steps):

#### Step 1: Get Spreadsheet Structure (800 tokens)
```python
google_sheets_get_spreadsheet(
    spreadsheet_id='1sheet123',
    format='structure'  # DEFAULT
)
```

**Returns:**
```json
{
  "success": true,
  "spreadsheet_id": "1sheet123",
  "title": "Sales Pipeline 2024",
  "format": "structure",
  "sheets": [
    {
      "sheet_name": "Active Deals",
      "sheet_id": 0,
      "row_count": 1243,
      "column_count": 26,
      "data_range": "A1:Z1243",
      "headers": ["Deal ID", "Company", "Contact", "Stage", "Value", "Close Date", "Owner", "Notes", ...],
      "sample_row": {
        "Deal ID": "D-2024-1001",
        "Company": "Acme Corp",
        "Stage": "Negotiation",
        "Value": "$85,000",
        "Close Date": "2024-12-15"
      }
    },
    {
      "sheet_name": "Closed Won",
      "sheet_id": 1,
      "row_count": 487,
      "column_count": 26,
      "data_range": "A1:Z487"
    },
    {
      "sheet_name": "Closed Lost",
      "sheet_id": 2,
      "row_count": 234,
      "column_count": 26,
      "data_range": "A1:Z234"
    },
    {
      "sheet_name": "Pipeline Analysis",
      "sheet_id": 3,
      "row_count": 45,
      "column_count": 12,
      "data_range": "A1:L45",
      "description": "Summary metrics and charts"
    }
  ],
  "total_sheets": 4,
  "last_updated": "2024-11-27T15:42:18Z"
}
```

**Tokens:** ~800 tokens (99.3% reduction!)  
**Content:** Sheet names, sizes, headers, sample row  
**AI can see:** Spreadsheet structure, which sheet has what data

---

#### Step 2: Get Specific Range (8,000 tokens for 100 rows)
```python
google_sheets_get_range(
    spreadsheet_id='1sheet123',
    range='Active Deals!A1:H100',  # First 100 deals, key columns only
    format='values'  # Just values, no formatting
)
```

**Returns:**
```json
{
  "success": true,
  "spreadsheet_id": "1sheet123",
  "range": "Active Deals!A1:H100",
  "values": [
    ["Deal ID", "Company", "Contact", "Stage", "Value", "Close Date", "Owner", "Notes"],
    ["D-2024-1001", "Acme Corp", "John Smith", "Negotiation", "$85,000", "2024-12-15", "Sarah J.", "Waiting on legal review"],
    ["D-2024-1002", "TechStart Inc", "Jane Doe", "Proposal", "$42,000", "2024-12-20", "Mike T.", "Sent proposal 11/25"],
    ["D-2024-1003", "Global Solutions", "Bob Wilson", "Discovery", "$125,000", "2025-01-10", "Sarah J.", "First meeting scheduled"],
    ... (96 more rows with just the values, no formatting)
  ],
  "row_count": 100,
  "column_count": 8,
  "format": "values"
}
```

**Tokens:** ~8,000 tokens (93.3% reduction from full sheet!)  
**Content:** 100 rows of actual data, no cell formatting  
**AI can see:** Current pipeline deals with key info

---

#### Step 3: Query Filtered Data (5,000 tokens)
```python
google_sheets_query_data(
    spreadsheet_id='1sheet123',
    sheet_name='Active Deals',
    filter={'Stage': 'Negotiation', 'Value': '>50000'},
    columns=['Company', 'Value', 'Close Date', 'Owner', 'Notes']
)
```

**Returns:**
```json
{
  "success": true,
  "spreadsheet_id": "1sheet123",
  "sheet_name": "Active Deals",
  "filter_applied": "Stage = Negotiation AND Value > $50,000",
  "results": [
    {
      "Company": "Acme Corp",
      "Value": "$85,000",
      "Close Date": "2024-12-15",
      "Owner": "Sarah J.",
      "Notes": "Waiting on legal review"
    },
    {
      "Company": "Enterprise LLC",
      "Value": "$230,000",
      "Close Date": "2024-12-30",
      "Owner": "Mike T.",
      "Notes": "Final approval from CFO needed"
    },
    {
      "Company": "BigCo Industries",
      "Value": "$156,000",
      "Close Date": "2025-01-05",
      "Owner": "Sarah J.",
      "Notes": "Security review in progress"
    },
    ... (18 more high-value negotiation deals)
  ],
  "result_count": 21,
  "total_rows_searched": 1243,
  "columns_returned": 5
}
```

**Tokens:** ~5,000 tokens (95.8% reduction!)  
**Content:** Only high-value deals in negotiation stage  
**AI can see:** Specific deals matching criteria

---

#### Step 4: Get Summary Statistics (1,200 tokens)
```python
google_sheets_get_summary(
    spreadsheet_id='1sheet123',
    sheet_name='Active Deals',
    aggregate_columns=['Value', 'Close Date'],
    group_by='Stage'
)
```

**Returns:**
```json
{
  "success": true,
  "spreadsheet_id": "1sheet123",
  "sheet_name": "Active Deals",
  "summary": {
    "Discovery": {
      "count": 342,
      "total_value": "$8,450,000",
      "avg_value": "$24,708",
      "avg_close_days": 45
    },
    "Proposal": {
      "count": 487,
      "total_value": "$15,230,000",
      "avg_value": "$31,272",
      "avg_close_days": 32
    },
    "Negotiation": {
      "count": 214,
      "total_value": "$12,870,000",
      "avg_value": "$60,140",
      "avg_close_days": 18
    },
    "Verbal Commit": {
      "count": 89,
      "total_value": "$8,920,000",
      "avg_value": "$100,224",
      "avg_close_days": 7
    },
    "Contract Sent": {
      "count": 111,
      "total_value": "$11,450,000",
      "avg_value": "$103,153",
      "avg_close_days": 3
    }
  },
  "grand_total": {
    "count": 1243,
    "total_value": "$56,920,000",
    "avg_value": "$45,790"
  }
}
```

**Tokens:** ~1,200 tokens (99% reduction!)  
**Content:** Aggregated metrics by stage  
**AI can see:** Pipeline health at a glance

---

## 💰 Token Comparison Summary

| Use Case | Before (Old) | After (New) | Reduction |
|----------|--------------|-------------|-----------|
| **Google Docs** | | | |
| "What's this doc about?" | 237,366 tokens | 500 tokens | 99.8% |
| "Find info about APAC" | 237,366 tokens | 2,000 tokens | 99.2% |
| "Show me full text" | 237,366 tokens | 50,000 tokens | 79% |
| **Google Slides** | | | |
| "What's in this deck?" | 150,000 tokens | 1,200 tokens | 99.2% |
| "Show me slide 5" | 150,000 tokens | 3,000 tokens | 98% |
| "Find roadmap slides" | 150,000 tokens | 2,500 tokens | 98.3% |
| **Google Forms** | | | |
| "What questions are asked?" | 80,000 tokens | 1,500 tokens | 98.1% |
| "Show response trends" | 580,000 tokens | 3,000 tokens | 99.5% |
| "Find negative feedback" | 580,000 tokens | 5,000 tokens | 99.1% |
| **Google Sheets** | | | |
| "What's in this sheet?" | 120,000 tokens | 800 tokens | 99.3% |
| "Show me 100 rows" | 120,000 tokens | 8,000 tokens | 93.3% |
| "High-value deals?" | 120,000 tokens | 5,000 tokens | 95.8% |
| "Pipeline summary?" | 120,000 tokens | 1,200 tokens | 99% |

---

## 🎯 Key Insight

**You ALWAYS get the full content, but in stages:**

1. **First Ask (500-1,500 tokens)**: "What is this?" → Get structure/summary
2. **Follow-up (2,000-8,000 tokens)**: "Show me section X" → Get specific content
3. **Search (2,000-5,000 tokens)**: "Find mentions of Y" → Get targeted info

**Total tokens for typical workflow: 4,500-14,500 tokens**  
**vs Old method: 80,000-580,000 tokens**  
**= 90-98% savings while still accessing ALL content!**

---

**The JSON waste is gone. The content remains. The AI can access everything efficiently.**
