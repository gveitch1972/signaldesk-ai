from src.foundry_client import get_client
from src.config import FOUNDRY_MODEL_DEPLOYMENT, ENABLE_HEAVY_CONTEXT_FOR_QA
from src.briefing.context_builder import build_context


def ask_question(question: str, include_heavy: bool | None = None) -> str:
    client = get_client()
    use_heavy_context = (
        ENABLE_HEAVY_CONTEXT_FOR_QA if include_heavy is None else include_heavy
    )
    context = build_context(include_heavy=use_heavy_context)

    response = client.chat.completions.create(
        model=FOUNDRY_MODEL_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": "You are a senior financial analyst. Answer clearly and concisely using the provided data.",
            },
            {
                "role": "user",
                "content": f"""
DATA:
{context}

QUESTION:
{question}
""",
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
