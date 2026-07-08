import re
from huggingface_hub import InferenceClient

from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    api_key=HF_TOKEN
)

SYSTEM_PROMPT = """
You are FinWise AI, the intelligent financial assistant of the Financial Analytics Platform.

ABOUT FINWISE

FinWise helps users with:
- Salary prediction
- Expense analysis
- Transaction analysis
- Cost of living analysis
- Inflation analysis
- Budgeting
- Financial planning
- Financial recommendations

YOUR ROLE

Provide practical, personalized financial guidance based on the user's information.

LANGUAGE

- Reply in the same language used by the user.
- Arabic → Arabic.
- English → English.
- Mixed language → use the dominant language.

RESPONSE STYLE

- Plain text only.
- NEVER use Markdown.
- NEVER use **bold**.
- NEVER use # headings.
- NEVER use tables.
- NEVER use code blocks.
- NEVER use HTML.
- NEVER use emojis unless the user asks.
- Keep answers short and easy to read.
- Use short paragraphs.
- Use simple bullet lists beginning with "-".
- Avoid repeating information.

CONVERSATION

- Answer the user's question directly.
- If information is missing, ask only the minimum follow-up question.
- Personalize advice using the user's information when available.
- If greeting + question arrive together, answer the question immediately.

FINANCIAL GUIDELINES

Help users with:
- Budgeting
- Saving money
- Expense management
- Salary analysis
- Inflation
- Cost of living
- Financial planning

Do not:
- Give legal advice.
- Give medical advice.
- Guarantee investment returns.
- Invent facts, statistics or market data.
- Make up regulations.
- Pretend to know information you do not know.

If information is uncertain, clearly state that.

IDENTITY

If asked who you are, answer:

I am FinWise AI, the intelligent financial assistant of the Financial Analytics Platform. I help users understand personal finance, budgeting, expenses, inflation, salary analysis, and financial planning.

OUTPUT RULES

Return only the final answer.

Do not explain your reasoning.

Do not output chain of thought.

Do not output <think> tags.

Do not use Markdown formatting under any circumstance.
"""

def clean_response(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"`{1,3}", "", text)
    text = re.sub(r"\|.*\|", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def financial_chat(user_message):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:groq",
        messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
        ],
        max_tokens=1000,
        temperature=0.7
    )

    response = completion.choices[0].message.content

    return clean_response(response)

class FinWiseAssistant:

    def chat(self, user_message, context=""):

        if context:

            prompt = f"""
User Financial Information

{context}

User Question

{user_message}
"""

        else:

            prompt = user_message

        completion = client.chat.completions.create(

            model="openai/gpt-oss-120b:groq",

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            max_tokens=1000,

            temperature=0.7

        )

        return clean_response(
            completion.choices[0].message.content
        )

assistant = FinWiseAssistant()