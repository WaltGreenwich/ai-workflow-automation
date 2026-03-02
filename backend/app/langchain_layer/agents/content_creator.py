"""
Content Creator Agent
Generates blog posts, social media content, and email templates.
"""
import json
import logging

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.langchain_layer.tools.company_tools import calculate_urgency_signals

logger = logging.getLogger(__name__)

CONTENT_CREATOR_PROMPT = PromptTemplate.from_template(
    """You are an expert B2B content creator specializing in AI automation.
Create high-quality, SEO-optimized content.

Tools: {tools}

Return JSON with: title, content (markdown), meta_description, social_posts (twitter/linkedin),
word_count, reading_time, keywords.

Question: {input}
Thought:{agent_scratchpad}"""
)


class ContentCreatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.7,
            convert_system_message_to_human=True,
        )
        self.tools = [calculate_urgency_signals]
        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=CONTENT_CREATOR_PROMPT)
        self.executor = AgentExecutor(
            agent=agent, tools=self.tools, verbose=True,
            max_iterations=5, handle_parsing_errors=True,
        )

    async def run(self, request: dict) -> dict:
        try:
            result = await self.executor.ainvoke({"input": json.dumps(request)})
            return self._parse(result.get("output", ""), request)
        except Exception as exc:
            logger.error("ContentCreatorAgent error: %s", exc)
            return self._fallback(request)

    def _parse(self, raw: str, request: dict) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
            s, e = clean.index("{"), clean.rindex("}") + 1
            return json.loads(clean[s:e])
        except Exception:
            return self._fallback(request)

    def _fallback(self, r: dict) -> dict:
        topic = r.get("topic", "AI Automation")
        return {
            "title": f"The Complete Guide to {topic}",
            "content": f"# {topic}\n\nContent generation in progress...",
            "meta_description": f"Learn about {topic} in this comprehensive guide.",
            "social_posts": {
                "twitter": f"New guide: {topic} #AI #Automation",
                "linkedin": f"We just published a comprehensive guide on {topic}.",
            },
            "word_count": 0,
            "reading_time": "5 min",
            "keywords": [topic, "AI", "automation"],
        }
