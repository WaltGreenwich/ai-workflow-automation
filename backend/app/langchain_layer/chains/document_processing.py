"""
Document Processing Chain
4-step pipeline: classify -> extract -> summarize -> action items
"""
import base64
import json
import logging

from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


class DocumentProcessingChain:
    def __init__(self):
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.1,
            convert_system_message_to_human=True,
        )
        c1 = LLMChain(llm=llm, output_key="document_type", prompt=PromptTemplate(
            input_variables=["document_text"],
            template='Classify this document.\nExcerpt: {document_text}\nReply ONLY JSON: {{"document_type":"...","industry":"...","language":"..."}}'))
        c2 = LLMChain(llm=llm, output_key="entities", prompt=PromptTemplate(
            input_variables=["document_text", "document_type"],
            template='Extract key entities from this {document_type}.\nText: {document_text}\nReply ONLY JSON: {{"entities":{{"parties":[],"dates":[],"amounts":[],"key_terms":[]}}}}'))
        c3 = LLMChain(llm=llm, output_key="summary", prompt=PromptTemplate(
            input_variables=["document_text", "document_type", "entities"],
            template='3-sentence summary of this {document_type}.\nEntities: {entities}\nText: {document_text}\nReply ONLY JSON: {{"summary":"...","key_points":[]}}'))
        c4 = LLMChain(llm=llm, output_key="action_items", prompt=PromptTemplate(
            input_variables=["document_text", "document_type", "entities", "summary"],
            template='List action items from this {document_type}.\nSummary: {summary}\nReply ONLY JSON: {{"action_items":[],"deadlines":[],"risks":[]}}'))
        self.chain = SequentialChain(
            chains=[c1, c2, c3, c4],
            input_variables=["document_text"],
            output_variables=["document_type", "entities", "summary", "action_items"],
            verbose=True,
        )

    async def run(self, document_data: dict) -> dict:
        text = document_data.get("text", "")
        if not text and document_data.get("file_content"):
            try:
                text = base64.b64decode(document_data["file_content"]).decode("utf-8", errors="ignore")
            except Exception:
                text = "Could not decode document."
        text = text[:4000]
        try:
            result = await self.chain.ainvoke({"document_text": text})
            return self._flatten(result, document_data.get("file_name", "document"))
        except Exception as exc:
            logger.error("DocumentProcessingChain error: %s", exc)
            return {"document_type": "Unknown", "summary": "Processing failed.",
                    "key_points": [], "entities": {}, "action_items": []}

    def _j(self, val):
        if isinstance(val, dict):
            return val
        try:
            c = str(val).strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(c[c.index("{"):c.rindex("}")+1])
        except Exception:
            return {}

    def _flatten(self, r: dict, filename: str) -> dict:
        doc = self._j(r.get("document_type", {}))
        ent = self._j(r.get("entities", {}))
        summ = self._j(r.get("summary", {}))
        act = self._j(r.get("action_items", {}))
        return {
            "file_name": filename,
            "document_type": doc.get("document_type", "Unknown"),
            "language": doc.get("language", "English"),
            "entities": {
                "parties":    ent.get("entities", {}).get("parties", []),
                "dates":      ent.get("entities", {}).get("dates", []),
                "amounts":    ent.get("entities", {}).get("amounts", []),
                "key_terms":  ent.get("entities", {}).get("key_terms", []),
            },
            "summary":      summ.get("summary", ""),
            "key_points":   summ.get("key_points", []),
            "action_items": act.get("action_items", []),
            "deadlines":    act.get("deadlines", []),
            "risks":        act.get("risks", []),
        }
