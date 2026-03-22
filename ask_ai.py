import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_ai(question, market_prob, news_headlines):
    system_instruction = """You are an expert superforecaster who predicts probabilities of real world events.
You will receive a YES/NO question, the current market probability, and recent news.
Respond with ONLY a JSON object, nothing else:
{
  "probability": 0.75,
  "confidence": "high",
  "reasoning": "Two sentences max."
}
Rules:
- probability must be between 0.01 and 0.99
- confidence must be exactly: "low", "medium", or "high"
- Output ONLY the JSON. No extra text."""

    user_message = f"""Question: {question}
Market probability: {market_prob:.0%} chance of YES
Recent news:
{news_headlines}
What is the TRUE probability of YES? Reply with only the JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=200,
        temperature=0.2,
        timeout=15,
    )

    reply_text = response.choices[0].message.content.strip()
    reply_text = re.sub(r"```json|```", "", reply_text).strip()

    start = reply_text.find("{")
    end   = reply_text.rfind("}") + 1

    if start == -1 or end == 0:
        return {
            "probability": market_prob,
            "confidence":  "low",
            "reasoning":   "Could not parse AI response."
        }

    result = json.loads(reply_text[start:end])

    if not (0.01 <= result.get("probability", 0) <= 0.99):
        result["probability"] = market_prob

    return result


if __name__ == "__main__":
    question    = "Will the Federal Reserve cut interest rates in June 2026?"
    market_prob = 0.68
    news        = """- Fed leaves rates unchanged amid uncertainty (2026-03-18)
- CPI data comes in below expectations (2026-03-10)
- Fed chair says we are watching the data closely (2026-03-08)"""

    print(f"Question: {question}")
    print(f"Market says: {market_prob:.0%} YES")
    print("Asking Groq AI...\n")

    result = ask_ai(question, market_prob, news)
    print(f"AI probability : {result['probability']:.0%}")
    print(f"Confidence     : {result['confidence']}")
    print(f"Reasoning      : {result['reasoning']}")