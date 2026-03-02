"""
Lead Qualifier Agent
ReAct agent that qualifies B2B leads 0-100 using multiple tools.
"""
import json
import logging

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.langchain_layer.tools.company_tools import (
    analyze_industry_fit,
    calculate_urgency_signals,
    enrich_company_data,
    score_company_size,
)

logger = logging.getLogger(__name__)

LEAD_QUALIFIER_PROMPT = PromptTemplate.from_template(
    """You are an expert lead qualification agent for a B2B SaaS company.
Analyze lead data and produce a structured JSON result.

Tools available:
{tools}

SCORING CRITERIA (max 100 pts):
- score_company_size        -> up to 30 pts
- analyze_industry_fit      -> up to 20 pts
- calculate_urgency_signals -> up to 25 pts
- enrich_company_data       -> up to 15 pts
- Corporate email domain    -> +5 pts (manual)
- C-level / VP / Director   -> +5 pts (manual)

CATEGORIES: Enterprise (71-100), SMB (41-70), Startup (0-40)
NEXT ACTIONS: immediate_contact (>=70), nurture_sequence (40-69), disqualify (<40)

Use this format EXACTLY:
Question: lead data
Thought: I need to evaluate step by step
Action: one of [{tool_names}]
Action Input: input string
Observation: result
... repeat ...
Thought: I now have all information
Final Answer: {{"score":<int>,"category":"<str>","reasoning":"<str>","next_action":"<str>","suggested_message":"<str>"}}

Begin!
Question: {input}
Thought:{agent_scratchpad}"""
)


class LeadQualifierAgent:
    """
    ReAct agent that qualifies incoming B2B leads.

    Input  -> dict: name, company, email, industry, employees, message
    Output -> dict: score (0-100), category, reasoning, next_action, suggested_message
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.2,
            convert_system_message_to_human=True,
        )
        self.tools = [
            score_company_size,
            analyze_industry_fit,
            calculate_urgency_signals,
            enrich_company_data,
        ]
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=LEAD_QUALIFIER_PROMPT,
        )
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=8,
            handle_parsing_errors=True,
        )

    async def run(self, lead_data: dict) -> dict:
        """Qualify a lead and return structured output."""
        try:
            result = await self.executor.ainvoke({"input": json.dumps(lead_data)})
            return self._parse_output(result.get("output", ""), lead_data)
        except Exception as exc:
            logger.error("LeadQualifierAgent error: %s", exc, exc_info=True)
            return self._fallback_result(lead_data)

    def _parse_output(self, raw: str, lead_data: dict) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
            s = clean.index("{")
            e = clean.rindex("}") + 1
            return self._validate(json.loads(clean[s:e]))
        except Exception:
            logger.warning("Could not parse agent output, using fallback")
            return self._fallback_result(lead_data)

    def _validate(self, d: dict) -> dict:
        score = max(0, min(100, int(d.get("score", 0))))
        if score >= 71:
            cat, action = "Enterprise", "immediate_contact"
        elif score >= 41:
            cat, action = "SMB", "nurture_sequence"
        else:
            cat, action = "Startup", "disqualify"
        return {
            "score": score,
            "category": d.get("category", cat),
            "reasoning": d.get("reasoning", "No reasoning provided"),
            "next_action": d.get("next_action", action),
            "suggested_message": d.get("suggested_message", ""),
        }

    def _fallback_result(self, ld: dict) -> dict:
        """Rule-based scoring when LLM is unavailable."""
        score, reasons = 0, []

        emp = int(ld.get("employees", 0))
        if emp >= 1000:
            score += 30
            reasons.append("Enterprise 1000+ employees")
        elif emp >= 100:
            score += 20
            reasons.append("Mid-market 100-999 employees")
        elif emp >= 10:
            score += 10
            reasons.append("SMB 10-99 employees")

        ind = str(ld.get("industry", "")).lower()
        if any(k in ind for k in ["tech", "software", "finance", "healthcare", "insurance"]):
            score += 20
            reasons.append(f"High-fit industry: {ind}")

        msg = str(ld.get("message", "")).lower()
        if any(k in msg for k in ["asap", "urgent", "budget", "ready"]):
            score += 20
            reasons.append("Urgency signals detected")

        email = str(ld.get("email", ""))
        if "@gmail" not in email and "@yahoo" not in email and "@" in email:
            score += 5
            reasons.append("Corporate email domain")

        score = min(score, 100)
        if score >= 71:
            cat, action = "Enterprise", "immediate_contact"
        elif score >= 41:
            cat, action = "SMB", "nurture_sequence"
        else:
            cat, action = "Startup", "disqualify"

        name = ld.get("name", "there")
        company = ld.get("company", "your company")
        return {
            "score": score,
            "category": cat,
            "reasoning": "; ".join(reasons) or "Insufficient data for scoring",
            "next_action": action,
            "suggested_message": (
                f"Hi {name}, I noticed {company} might benefit from our AI automation platform. "
                "Would you be open to a quick 15-minute call this week?"
            ),
        }
