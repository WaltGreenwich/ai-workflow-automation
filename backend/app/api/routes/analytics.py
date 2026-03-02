"""Analytics endpoints."""
import random
from datetime import date, timedelta
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

def dates(n=7):
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(n-1, -1, -1)]

@router.get("/metrics")
async def get_metrics():
    d = dates(7)
    return {
        "executionsPerDay":       [{"date": x, "count": random.randint(80, 200)} for x in d],
        "successRateByWorkflow":  [
            {"workflow": "Lead Qual",    "successRate": 97.5},
            {"workflow": "Email Routing","successRate": 99.1},
            {"workflow": "Content Gen",  "successRate": 95.2},
            {"workflow": "Doc Process",  "successRate": 98.8},
        ],
        "tokenUsage": [{"date": x, "tokens": random.randint(10000, 50000)} for x in d],
        "summary": {
            "total_executions": 1651,
            "avg_success_rate": 97.7,
            "total_tokens_used": 254000,
            "estimated_cost_usd": 0.00,
        },
    }
