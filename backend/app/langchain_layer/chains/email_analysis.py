"""
Email Analysis Chain
4-step sequential chain: classify -> extract -> sentiment -> response
"""
import json
import logging

from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

CLASSIFY_PROMPT = PromptTemplate(
    input_variables=["email_subject", "email_body", "sender"],
    template="""Classify this email. Categories: Support|Sales|Billing|Spam|Urgent

Subject: {email_subject}
Body: {email_body}
Sender: {sender}

Reply ONLY with JSON: {{"category":"<cat>","subcategory":"<subcat>","confidence":<0-1>}}""",
)

EXTRACT_PROMPT = PromptTemplate(
    input_variables=["email_subject", "email_body", "sender", "category"],
    template="""Extract entities from this {category} email.
Subject: {email_subject}
Body: {email_body}
Sender: {sender}

Reply ONLY with JSON: {{"entities":{{"names":[],"companies":[],"reference_numbers":[],"dates":[],"amounts":[]}}}}""",
)

SENTIMENT_PROMPT = PromptTemplate(
    input_variables=["email_subject", "email_body", "sender", "category", "entities"],
    template="""Analyze sentiment and priority.
Category: {category}
Subject: {email_subject}
Body: {email_body}

Reply ONLY with JSON: {{"sentiment":"Positive|Neutral|Negative|Angry","priority":"Low|Medium|High|Critical","frustration_level":<0-10>}}""",
)

RESPONSE_PROMPT = PromptTemplate(
    input_variables=["email_subject", "email_body", "sender", "category", "entities", "sentiment"],
    template="""Generate a professional email response.
Category: {category}, Sentiment: {sentiment}
Subject: {email_subject}, Original: {email_body}, Sender: {sender}

Rules: Be empathetic if Negative/Angry. Be concise. Include clear next step.

Reply ONLY with JSON: {{"suggested_response":"<full response>","assign_to":"support_team|sales_team|billing_team|management","auto_send":<true|false>}}""",
)


class EmailAnalysisChain:
    """
    Sequential pipeline for comprehensive email analysis.
    Input:  email_subject, email_body, sender (all str)
    Output: flat dict with category, entities, sentiment, priority, suggested_response, assign_to
    """

    def __init__(self):
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.2,
            convert_system_message_to_human=True,
        )
        c1 = LLMChain(llm=llm, prompt=CLASSIFY_PROMPT, output_key="category")
        c2 = LLMChain(llm=llm, prompt=EXTRACT_PROMPT, output_key="entities")
        c3 = LLMChain(llm=llm, prompt=SENTIMENT_PROMPT, output_key="sentiment")
        c4 = LLMChain(llm=llm, prompt=RESPONSE_PROMPT, output_key="suggested_response")
        self.chain = SequentialChain(
            chains=[c1, c2, c3, c4],
            input_variables=["email_subject", "email_body", "sender"],
            output_variables=["category", "entities", "sentiment", "suggested_response"],
            verbose=True,
        )

    async def run(self, email_subject: str, email_body: str, sender: str) -> dict:
        try:
            result = await self.chain.ainvoke({
                "email_subject": email_subject,
                "email_body": email_body,
                "sender": sender,
            })
            return self._flatten(result)
        except Exception as exc:
            logger.error("EmailAnalysisChain error: %s", exc, exc_info=True)
            return self._fallback(email_subject, email_body)

    def _j(self, val):
        """Parse JSON string or return dict as-is."""
        if isinstance(val, dict):
            return val
        try:
            clean = str(val).strip().removeprefix("```json").removesuffix("```").strip()
            s, e = clean.index("{"), clean.rindex("}") + 1
            return json.loads(clean[s:e])
        except Exception:
            return {}

    def _flatten(self, r: dict) -> dict:
        cat = self._j(r.get("category", {}))
        ent = self._j(r.get("entities", {}))
        sen = self._j(r.get("sentiment", {}))
        res = self._j(r.get("suggested_response", {}))
        return {
            "category":          cat.get("category", "Support"),
            "subcategory":       cat.get("subcategory", "General"),
            "confidence":        cat.get("confidence", 0.8),
            "entities":          ent.get("entities", {}),
            "sentiment":         sen.get("sentiment", "Neutral"),
            "priority":          sen.get("priority", "Medium"),
            "frustration_level": sen.get("frustration_level", 0),
            "suggested_response":res.get("suggested_response", ""),
            "assign_to":         res.get("assign_to", "support_team"),
            "auto_send":         res.get("auto_send", False),
        }

    def _fallback(self, subject: str, body: str) -> dict:
        text = (subject + " " + body).lower()
        if any(k in text for k in ["invoice", "bill", "payment"]):
            cat, team = "Billing", "billing_team"
        elif any(k in text for k in ["buy", "price", "demo"]):
            cat, team = "Sales", "sales_team"
        else:
            cat, team = "Support", "support_team"
        return {
            "category": cat, "subcategory": "General", "confidence": 0.6,
            "entities": {}, "sentiment": "Neutral", "priority": "Medium",
            "frustration_level": 0, "assign_to": team, "auto_send": True,
            "suggested_response": "Thank you for reaching out. We'll respond within 24 business hours.",
        }
