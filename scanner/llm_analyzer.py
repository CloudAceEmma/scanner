from google import genai
from google.genai import Client
import os
import json

# Configure the API key
client = Client(api_key=os.environ["GEMINI_API_KEY"])


def analyze_text_with_gemini(text_content: str):
    """
    Sends text to Gemini for secret analysis.
    """
    prompt = f"""
You are an automated secret scanning assistant with expertise in identifying sensitive information within code and text. Your task is to analyze the provided git diff and commit message to find any potential secrets.

When you find a potential secret, you must respond ONLY with a JSON object containing the following keys:
- "finding_type": (e.g., "API Key", "Password", "Private Key", "AWS Access Key")
- "rationale": (A brief, one-sentence explanation of why this is a potential secret)
- "confidence": (A score from 0.0 to 1.0 indicating your confidence)
- "snippet": (The exact line of code or text containing the secret)

If you find no secrets, respond with an empty JSON object: {{}}.

Analyze the following content:
---
{text_content}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        # Clean the response to ensure it's valid JSON
        response_text = response.text
        assert response_text is not None
        cleaned_response = response_text.strip().replace("`", "").replace("json", "")
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, ValueError):
        return {}  # Return empty if response is not valid JSON
