"""Tests for LangChain agents and tools (no real API calls)."""
import json
import pytest


class TestLeadQualifierAgent:
    def _agent(self):
        from app.langchain_layer.agents.lead_qualifier import LeadQualifierAgent
        return LeadQualifierAgent.__new__(LeadQualifierAgent)

    def test_fallback_high_score(self):
        result = self._agent()._fallback_result({
            "name": "John", "company": "BigTech", "email": "j@bigtech.com",
            "industry": "Technology", "employees": 1000,
            "message": "Need AI automation ASAP, budget approved",
        })
        assert result["score"] >= 70
        assert result["category"] == "Enterprise"
        assert result["next_action"] == "immediate_contact"

    def test_fallback_low_score(self):
        result = self._agent()._fallback_result({
            "name": "Bob", "company": "Joe Garage", "email": "bob@gmail.com",
            "industry": "Agriculture", "employees": 2, "message": "Just browsing",
        })
        assert result["score"] < 40
        assert result["next_action"] in ("nurture_sequence", "disqualify")

    def test_validate_clamps_score(self):
        r = self._agent()._validate({"score": 999, "reasoning": "test"})
        assert r["score"] == 100

    def test_validate_smb_range(self):
        r = self._agent()._validate({"score": 55, "reasoning": "mid"})
        assert r["category"] == "SMB"
        assert r["next_action"] == "nurture_sequence"

    def test_parse_clean_json(self):
        raw = '{"score":80,"category":"Enterprise","reasoning":"big","next_action":"immediate_contact","suggested_message":"Hi!"}'
        r = self._agent()._parse_output(raw, {})
        assert r["score"] == 80

    def test_parse_markdown_fence(self):
        raw = '```json\n{"score":55,"category":"SMB","reasoning":"ok","next_action":"nurture_sequence","suggested_message":""}\n```'
        r = self._agent()._parse_output(raw, {})
        assert r["score"] == 55


class TestEmailRouterAgent:
    def _agent(self):
        from app.langchain_layer.agents.email_router import EmailRouterAgent
        return EmailRouterAgent.__new__(EmailRouterAgent)

    def test_fallback_billing(self):
        r = self._agent()._fallback({"subject": "Invoice question", "body": "Send my invoice"})
        assert r["category"] == "Billing"
        assert r["assign_to"] == "billing_team"

    def test_fallback_sales(self):
        r = self._agent()._fallback({"subject": "Pricing", "body": "I want a demo"})
        assert r["category"] == "Sales"


class TestTools:
    def test_company_size_enterprise(self):
        from app.langchain_layer.tools.company_tools import score_company_size
        d = json.loads(score_company_size.invoke("1500"))
        assert d["score"] == 30
        assert d["category"] == "Enterprise"

    def test_company_size_startup(self):
        from app.langchain_layer.tools.company_tools import score_company_size
        d = json.loads(score_company_size.invoke("3"))
        assert d["category"] == "Startup"

    def test_industry_high(self):
        from app.langchain_layer.tools.company_tools import analyze_industry_fit
        d = json.loads(analyze_industry_fit.invoke("Technology"))
        assert d["score"] == 20
        assert d["fit"] == "high"

    def test_industry_low(self):
        from app.langchain_layer.tools.company_tools import analyze_industry_fit
        d = json.loads(analyze_industry_fit.invoke("Agriculture"))
        assert d["fit"] == "low"

    def test_urgency_detected(self):
        from app.langchain_layer.tools.company_tools import calculate_urgency_signals
        d = json.loads(calculate_urgency_signals.invoke("We need this ASAP, budget approved"))
        assert d["is_urgent"] is True
        assert len(d["detected_signals"]) >= 1

    def test_urgency_none(self):
        from app.langchain_layer.tools.company_tools import calculate_urgency_signals
        d = json.loads(calculate_urgency_signals.invoke("Hello, just browsing"))
        assert d["is_urgent"] is False

    def test_extract_contacts(self):
        from app.langchain_layer.tools.company_tools import extract_contact_info
        d = json.loads(extract_contact_info.invoke("Email john@example.com or call 555-123-4567"))
        assert "john@example.com" in d["emails"]
        assert len(d["phones"]) >= 1

    def test_enrich_returns_data(self):
        from app.langchain_layer.tools.company_tools import enrich_company_data
        d = json.loads(enrich_company_data.invoke("TechCorp"))
        assert "estimated_employees" in d
        assert d["company_name"] == "TechCorp"
