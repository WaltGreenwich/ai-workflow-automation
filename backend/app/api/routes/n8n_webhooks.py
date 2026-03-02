"""
n8n Webhook Endpoints
FastAPI routes called by n8n HTTP Request nodes.
"""
import logging
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.langchain_layer.agents import ContentCreatorAgent, EmailRouterAgent, LeadQualifierAgent
from app.langchain_layer.chains import DocumentProcessingChain, EmailAnalysisChain

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/langchain", tags=["n8n-integration"])


# ── Schemas ────────────────────────────────────────────────────────────────

class LeadRequest(BaseModel):
    name: str = Field(..., example="John Doe")
    company: str = Field(..., example="TechCorp Inc")
    email: str = Field(..., example="john@techcorp.com")
    industry: str = Field(default="Technology")
    employees: int = Field(default=100, ge=0)
    message: str = Field(default="")
    phone: str | None = None
    title: str | None = None


class EmailRequest(BaseModel):
    subject: str = Field(..., example="Billing question about invoice")
    body: str = Field(..., example="Hi, I have a question about my last invoice...")
    sender: str = Field(..., example="customer@example.com")
    received_at: str | None = None


class ContentRequest(BaseModel):
    topic: str = Field(..., example="AI automation trends")
    format: str = Field(default="blog")
    target_length: int = Field(default=1500)
    keywords: list[str] = Field(default_factory=list)


class DocumentRequest(BaseModel):
    file_name: str = Field(..., example="contract.pdf")
    file_content: str | None = None   # base64
    text: str | None = None           # pre-extracted
    document_type: str | None = None


class ClassifyRequest(BaseModel):
    text: str
    categories: list[str] = Field(default_factory=lambda: ["Support", "Sales", "Billing", "Spam"])


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/qualify-lead")
async def qualify_lead(lead: LeadRequest):
    """
    Webhook: n8n sends lead data, gets AI qualification result.
    Returns: score (0-100), category, reasoning, next_action, suggested_message
    """
    t = time.perf_counter()
    logger.info("qualify_lead: %s @ %s", lead.name, lead.company)
    try:
        result = await LeadQualifierAgent().run(lead.model_dump())
        logger.info("qualify_lead done in %dms score=%s", (time.perf_counter()-t)*1000, result.get("score"))
        return result
    except Exception as exc:
        logger.error("qualify_lead failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/analyze-email")
async def analyze_email(email: EmailRequest):
    """
    Webhook: n8n sends email data, gets routing decision + suggested response.
    Uses EmailAnalysisChain (4-step sequential).
    """
    t = time.perf_counter()
    logger.info("analyze_email from %s", email.sender)
    try:
        result = await EmailAnalysisChain().run(
            email_subject=email.subject,
            email_body=email.body,
            sender=email.sender,
        )
        logger.info("analyze_email done in %dms cat=%s", (time.perf_counter()-t)*1000, result.get("category"))
        return result
    except Exception as exc:
        logger.error("analyze_email failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-content")
async def generate_content(request: ContentRequest):
    """
    Webhook: n8n triggers content generation.
    Returns blog post, meta description, and social variants.
    """
    t = time.perf_counter()
    logger.info("generate_content topic='%s'", request.topic[:60])
    try:
        result = await ContentCreatorAgent().run(request.model_dump())
        logger.info("generate_content done in %dms", (time.perf_counter()-t)*1000)
        return result
    except Exception as exc:
        logger.error("generate_content failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/process-document")
async def process_document(doc: DocumentRequest):
    """
    Webhook: n8n sends document (base64 PDF or text), gets analysis.
    Returns: type, summary, key points, entities, action items.
    """
    t = time.perf_counter()
    logger.info("process_document: %s", doc.file_name)
    try:
        result = await DocumentProcessingChain().run(doc.model_dump())
        logger.info("process_document done in %dms", (time.perf_counter()-t)*1000)
        return result
    except Exception as exc:
        logger.error("process_document failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/classify")
async def classify_text(request: ClassifyRequest):
    """Generic text classification used by the custom n8n AI Classifier node."""
    import json as _json
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    prompt = PromptTemplate.from_template(
        "Classify into one of: {categories}\n\nText: {text}\n\n"
        'Reply ONLY JSON: {{"category":"...","confidence":0.0,"reasoning":"..."}}'
    )
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1,
                                     convert_system_message_to_human=True)
        chain = prompt | llm
        raw = await chain.ainvoke({"categories": ", ".join(request.categories), "text": request.text})
        content = raw.content if hasattr(raw, "content") else str(raw)
        clean = content.strip().removeprefix("```json").removesuffix("```").strip()
        s, e = clean.index("{"), clean.rindex("}") + 1
        return _json.loads(clean[s:e])
    except Exception as exc:
        logger.error("classify_text failed: %s", exc)
        return {"category": request.categories[0], "confidence": 0.5, "reasoning": "fallback"}
