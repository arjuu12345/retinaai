import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Create client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert ophthalmologist assistant.
Only answer questions related to:
- Diabetic Retinopathy
- Eye health
- Diabetes complications
- Retina treatment
- Prevention and symptoms

If user asks unrelated questions, respond:
"I am specialized in retinal healthcare. Please ask medical questions related to eye health."
"""

def get_ai_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content