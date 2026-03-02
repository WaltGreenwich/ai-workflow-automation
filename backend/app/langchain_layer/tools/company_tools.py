"""
Company Tools
LangChain @tool functions used by agents.
"""
import json
import re

from langchain.tools import tool


@tool
def score_company_size(employee_count: str) -> str:
    """
    Score a company based on its employee headcount.
    Args:
        employee_count: Number of employees as string (e.g. '500')
    Returns:
        JSON string with score (0-30), category, and reasoning.
    """
    try:
        count = int(str(employee_count).strip().replace(",", ""))
    except (ValueError, TypeError):
        return json.dumps({"score": 0, "category": "Unknown", "reasoning": "Invalid employee count"})

    if count >= 1000:
        return json.dumps({"score": 30, "category": "Enterprise", "reasoning": "Large enterprise 1000+ employees"})
    elif count >= 500:
        return json.dumps({"score": 25, "category": "Enterprise", "reasoning": "Enterprise 500-999 employees"})
    elif count >= 100:
        return json.dumps({"score": 20, "category": "Mid-Market", "reasoning": "Mid-market 100-499 employees"})
    elif count >= 50:
        return json.dumps({"score": 15, "category": "SMB", "reasoning": "Small business 50-99 employees"})
    elif count >= 10:
        return json.dumps({"score": 10, "category": "SMB", "reasoning": "Small business 10-49 employees"})
    else:
        return json.dumps({"score": 5, "category": "Startup", "reasoning": "Early-stage startup under 10 employees"})


@tool
def analyze_industry_fit(industry: str) -> str:
    """
    Determine if an industry is a good fit for a B2B SaaS automation product.
    Args:
        industry: Industry name (e.g. 'Technology', 'Healthcare')
    Returns:
        JSON string with score (0-20), fit level, and reasoning.
    """
    ind = str(industry).lower().strip()

    high_fit = ["technology", "software", "saas", "fintech", "finance",
                "healthcare", "insurance", "legal", "consulting", "marketing"]
    medium_fit = ["retail", "ecommerce", "manufacturing", "education",
                  "real estate", "logistics", "telecom", "media"]
    low_fit = ["agriculture", "mining", "construction", "government",
               "non-profit", "restaurant", "hospitality"]

    if any(k in ind for k in high_fit):
        return json.dumps({"score": 20, "fit": "high", "reasoning": f"{industry} is a high-fit industry"})
    elif any(k in ind for k in medium_fit):
        return json.dumps({"score": 12, "fit": "medium", "reasoning": f"{industry} has moderate fit"})
    elif any(k in ind for k in low_fit):
        return json.dumps({"score": 4, "fit": "low", "reasoning": f"{industry} is a low-fit industry"})
    else:
        return json.dumps({"score": 8, "fit": "unknown", "reasoning": f"Unknown industry '{industry}'"})


@tool
def calculate_urgency_signals(text: str) -> str:
    """
    Detect purchase-intent and urgency signals in a text string.
    Args:
        text: Free-form text to analyze
    Returns:
        JSON string with score (0-25), detected_signals list, is_urgent flag.
    """
    urgency_map = {
        "asap": 8, "urgent": 8, "immediately": 8, "today": 6,
        "this week": 5, "budget approved": 10, "ready to buy": 10,
        "ready to purchase": 10, "decision maker": 5,
        "end of quarter": 6, "deadline": 5, "need this now": 8,
    }

    text_lower = str(text).lower()
    detected = {kw: pts for kw, pts in urgency_map.items() if kw in text_lower}
    total = min(sum(detected.values()), 25)

    return json.dumps({
        "score": total,
        "detected_signals": list(detected.keys()),
        "is_urgent": total >= 12,
        "reasoning": f"Found {len(detected)} urgency signal(s): {', '.join(detected.keys()) or 'none'}",
    })


@tool
def enrich_company_data(company_name: str) -> str:
    """
    Enrich company data with additional context (mock implementation).
    In production, call Clearbit/Hunter.io.
    Args:
        company_name: The name of the company to enrich
    Returns:
        JSON string with enriched company data.
    """
    import hashlib
    hash_val = int(hashlib.md5(company_name.encode()).hexdigest()[:4], 16)
    emp_buckets = [10, 50, 150, 400, 800, 1500, 3000]
    mock_emp = emp_buckets[hash_val % len(emp_buckets)]
    industries = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"]
    mock_ind = industries[hash_val % len(industries)]
    slug = company_name.lower().replace(" ", "-")
    return json.dumps({
        "company_name": company_name,
        "estimated_employees": mock_emp,
        "industry": mock_ind,
        "linkedin_url": f"https://linkedin.com/company/{slug}",
        "estimated_revenue": f"${mock_emp * 200_000:,}",
        "confidence": 0.72,
        "source": "mock_enrichment",
    })


@tool
def extract_contact_info(text: str) -> str:
    """
    Extract emails, phone numbers, and URLs from text using regex.
    Args:
        text: Text to scan for contact information
    Returns:
        JSON string with emails, phones, and urls lists.
    """
    email_re = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
    phone_re = r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    url_re = r'https?://(?:www\.)?[\w\-]+\.[\w\-./?=%&#+@]+'
    return json.dumps({
        "emails": re.findall(email_re, text),
        "phones": re.findall(phone_re, text),
        "urls": re.findall(url_re, text),
    })
