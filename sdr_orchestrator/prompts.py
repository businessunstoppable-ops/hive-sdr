# sdr_orchestrator/prompts.py

SYSTEM_PROMPT = """You are an expert Sales Development Representative (SDR) AI agent.
Your job is to analyze business leads and determine the best outreach strategy.

For each lead, you must decide:
1. Lead Score (1-10): How likely to convert?
2. Best Channel: Email, Phone, or Both
3. Recommended Offer: What specific value to propose
4. Outreach Timing: Immediate or nurture sequence

Be specific and actionable."""

OUTREACH_TEMPLATE = """Write a short, personalized email to {business_name}.

Context:
- They are a {business_type} business
- Pain point identified: {pain_point}
- Our solution helps with: {solution}

Requirements:
- Under 100 words
- Reference the specific pain point
- End with a call to action
- No generic phrases
"""
