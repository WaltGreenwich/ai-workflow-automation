"""Tests for n8n webhook endpoints (mocked LLM)."""
import pytest
from unittest.mock import AsyncMock, patch


class TestHealthAndRoutes:
    def test_health(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "docs" in r.json()

    def test_workflows_list(self, client):
        r = client.get("/api/v1/workflows")
        assert r.status_code == 200
        data = r.json()
        assert "workflows" in data
        assert data["total"] == 4

    def test_analytics_metrics(self, client):
        r = client.get("/api/v1/analytics/metrics")
        assert r.status_code == 200
        data = r.json()
        assert "executionsPerDay" in data
        assert "successRateByWorkflow" in data
        assert len(data["executionsPerDay"]) == 7


class TestLeadQualificationEndpoint:
    def test_qualify_lead_valid(self, client):
        with patch(
            "app.langchain_layer.agents.lead_qualifier.LeadQualifierAgent.run",
            new_callable=AsyncMock,
            return_value={
                "score": 85, "category": "Enterprise",
                "reasoning": "Large tech company",
                "next_action": "immediate_contact",
                "suggested_message": "Hi!",
            },
        ):
            r = client.post("/api/v1/langchain/qualify-lead", json={
                "name": "Alice", "company": "BigCo",
                "email": "alice@bigco.com", "industry": "Technology",
                "employees": 600,
            })
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["score"], int)
        assert "category" in data
        assert "next_action" in data

    def test_qualify_lead_missing_name(self, client):
        r = client.post("/api/v1/langchain/qualify-lead", json={
            "company": "X", "email": "x@x.com",
        })
        assert r.status_code == 422

    def test_qualify_lead_missing_email(self, client):
        r = client.post("/api/v1/langchain/qualify-lead", json={
            "name": "Bob",
        })
        assert r.status_code == 422


class TestEmailAnalysisEndpoint:
    def test_analyze_email_valid(self, client):
        with patch(
            "app.langchain_layer.chains.email_analysis.EmailAnalysisChain.run",
            new_callable=AsyncMock,
            return_value={
                "category": "Billing", "subcategory": "Invoice",
                "priority": "Medium", "sentiment": "Neutral",
                "entities": {}, "suggested_response": "We will help.",
                "assign_to": "billing_team", "auto_send": True,
            },
        ):
            r = client.post("/api/v1/langchain/analyze-email", json={
                "subject": "Invoice question",
                "body": "Need my invoice",
                "sender": "user@corp.com",
            })
        assert r.status_code == 200
        assert "category" in r.json()

    def test_analyze_email_missing_body(self, client):
        r = client.post("/api/v1/langchain/analyze-email", json={
            "subject": "Test", "sender": "x@x.com",
        })
        assert r.status_code == 422
