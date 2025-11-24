import anthropic
import pandas as pd
import json

def extract_sections(api_key, pdf_text, model="claude-3-haiku-20240307"):
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are extracting specific narrative sections from UK charity annual accounts.
These accounts should follow Charity Commission reporting requirements (SORP), but the structure is unlikely to be consistent.

Your task is to extract THREE specific sections. These sections contain descriptive, narrative text about the charity's work - NOT financial tables or lists of numbers.

IMPORTANT: When identifying section HEADINGS, use SEMANTIC UNDERSTANDING. Headings contain similar words/concepts but may be combined or reworded creatively. For example, "Activities, Specific Objectives and Aims" should be recognized as matching "Objectives and Activities" because it refers to the same semantic concepts (objectives + activities), just worded differently or combined with extra terms.

SECTION 1: OBJECTIVES AND ACTIVITIES
Look for HEADINGS that semantically refer to: objectives, aims, goals, purposes, objects, or activities.
Common heading patterns:
- "Objectives and Activities"
- "Objects and Activities"
- "Charitable Objectives"
- "Principal Activities"
- "Aims and Activities"
- "Activities, Specific Objectives and Relevant Policies" (combined/reworded but same concept)
- Or may reference SORP paragraphs 1.17, 1.18, or 1.19

The section content describes what the charity aims to do and how it operates.

SECTION 2: ACHIEVEMENTS AND PERFORMANCE
Look for HEADINGS that semantically refer to: achievements, performance, results, impact, review, or accomplishments.
Common heading patterns:
- "Achievements and Performance"
- "Activities and Achievements"
- "Review of Activities"
- "Charitable Activities" (when context suggests review/outcomes)
- "Annual Review"
- "Public Benefit"
- Or may reference SORP paragraph 1.20

The section content describes what the charity accomplished during the year.

SECTION 3: GRANT-MAKING POLICY
Look for HEADINGS that semantically refer to: grant-making, grants policy, funding approach, or distribution.
Common heading patterns:
- "Grant-making Policy"
- "Grants Policy"
- "Policy on Grant Giving"
- "Grantmaking Strategy"
- "Funding Policy"
- Or may reference SORP paragraph 1.38

The section content describes how the charity decides who to fund.

CRITICAL EXTRACTION RULES:

1. EXACT BOUNDARIES: Extract ONLY the narrative text within each section
   - Start AFTER the section heading
   - Stop BEFORE the next section heading or financial table
   - Do NOT include section titles in the extracted text
   - Do NOT include SORP paragraph references

2. AVOID CONTAMINATION:
   - Do NOT include text from other sections
   - Do NOT include financial statements, balance sheets, or income/expenditure tables
   - Do NOT include lists of trustees, staff, or contact details
   - Do NOT include governance sections about risk management or reserves policy
   - If a section contains ONLY a single sentence or appears to be a heading with no content, return null

3. HANDLING COMBINED SECTIONS:
   - Sometimes "Objectives and Activities" combines with "Achievements and Performance" in one section
   - If this happens, extract the ENTIRE combined section for BOTH fields
   - It's acceptable for both fields to contain identical text if they're genuinely combined

4. WORD COUNT GUIDANCE:
   - Typical sections are 50-500 words
   - If extraction is <15 words, it's likely just a heading - return null instead
   - If extraction is >2000 words, you've likely captured multiple sections - be more precise
   - Sections of 15-20 words are acceptable if that's genuinely all the charity wrote

5. PRECISION OVER COMPLETENESS:
   - If you're uncertain where a section ends, it's better to extract slightly less than to include wrong content
   - If you cannot clearly identify a section, return null for that field
   - Do NOT guess or infer section boundaries

6. GRANT POLICY SPECIAL NOTES:
   - This section is often short (1-2 paragraphs) or missing entirely
   - Only extract if there's genuine policy description
   - Do NOT extract generic statements like "grants are made to charitable institutions"
   - Look for detail about application processes, funding priorities, decision criteria

Return ONLY valid JSON in this exact format (no markdown formatting):
{{
  "objectives_activities": "extracted text or null",
  "achievements_performance": "extracted text or null",
  "grant_policy": "extracted text or null"
}}

ACCOUNTS TEXT:
{pdf_text}"""

    try:
        max_tokens = 8000 if "sonnet" in model else 4000
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        #remove markdown created by clade
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        #get json only
        first_brace = response_text.find("{")
        last_brace = response_text.rfind("}")

        if first_brace == -1 or last_brace == -1:
            return {
                "objectives_activities": None,
                "achievements_performance": None,
                "grant_policy": None
            }

        json_text = response_text[first_brace:last_brace + 1]
        result = json.loads(json_text)

        return {
            "objectives_activities": result.get("objectives_activities"),
            "achievements_performance": result.get("achievements_performance"),
            "grant_policy": result.get("grant_policy")
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing failed - {e}")
        return {
            "objectives_activities": None,
            "achievements_performance": None,
            "grant_policy": None
        }
    except Exception as e:
        print(f"Error calling API - {e}")
        return {
            "objectives_activities": None,
            "achievements_performance": None,
            "grant_policy": None
        }