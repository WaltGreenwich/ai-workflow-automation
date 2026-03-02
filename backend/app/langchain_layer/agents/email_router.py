"""
Email Router Agent
Classifies incoming emails and routes them to the correct team.
"""
import json
import logging

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.langchain_layer.tools.company_tools import (
    calculate_urgency_signals,
    extract_contact_info,
)

logger = logging.getLogger(__name__)

EMAIL_ROUTER_PROMPT = PromptTemplate.from_template(
    """You are an intelligent email routing agent for a B2B SaaS company.
Analyze emails and determine routing.

Tools:
{tools}

Determine:
1. Category: Support | Sales | Billing | Spam | Urgent
2. Subcategory (e.g. "Login Issue", "Invoice Question")
3. Priority: Low | Medium | High | Critical
4. Sentiment: Positive | Neutral | Negative | Angry
5. Team: support_team | sales_team | billing_team | management

Format:
Question: email data
Thought: analyze
Action: [{tool_names}]
Action Input: input
Observation: result
... repeat ...
Final Answer: {{"category":"...","subcategory":"...","priority":"...","sentiment":"...","assign_to":"...","auto_response":true,"suggested_response":"..."}}

Begin!
Question: {input}
Thought:{agent_scratchpad}"""
)


class EmailRouterAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.1,
            convert_system_message_to_human=True,
        )
        self.tools = [calculate_urgency_signals, extract_contact_info]
        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=EMAIL_ROUTER_PROMPT)
        self.executor = AgentExecutor(
            agent=agent, tools=self.tools, verbose=True,
            max_iterations=5, handle_parsing_errors=True,
        )

    async def run(self, email_data: dict) -> dict:
        try:
            result = await self.executor.ainvoke({"input": json.dumps(email_data)})
            return self._parse(result.get("output", ""), email_data)
        except Exception as exc:
            logger.error("EmailRouterAgent error: %s", exc)
            return self._fallback(email_data)

    def _parse(self, raw: str, email_data: dict) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
            s, e = clean.index("{"), clean.rindex("}") + 1
            return json.loads(clean[s:e])
        except Exception:
            return self._fallback(email_data)

    def _fallback(self, d: dict) -> dict:
        text = (str(d.get("subject", "")) + " " + str(d.get("body", ""))).lower()
        if any(k in text for k in ["invoice", "billing", "payment", "charge"]):
            cat, team = "Billing", "billing_team"
        elif any(k in text for k in ["buy", "pricing", "demo", "trial"]):
            cat, team = "Sales", "sales_team"
        elif any(k in text for k in ["urgent", "asap", "critical", "down"]):
            cat, team = "Urgent", "management"
        else:
            cat, team = "Support", "support_team"
        return {
            "category": cat, "subcategory": "General",
            "priority": "Medium", "sentiment": "Neutral",
            "assign_to": team, "auto_response": True,
            "suggested_response": "Thank you for contacting us. We'll respond within 24 hours.",
        }
