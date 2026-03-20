from src.foundry_client import get_client
from src.config import FOUNDRY_MODEL_DEPLOYMENT, ENABLE_HEAVY_CONTEXT_FOR_BRIEFING
from src.briefing.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.briefing.context_builder import build_context


def generate_briefing(include_heavy: bool | None = None):
    client = get_client()
    use_heavy_context = (
        ENABLE_HEAVY_CONTEXT_FOR_BRIEFING if include_heavy is None else include_heavy
    )
    context = build_context(include_heavy=use_heavy_context)

    response = client.chat.completions.create(
        model=FOUNDRY_MODEL_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(context=context),
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
