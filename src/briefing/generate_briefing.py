from src.foundry_client import get_client
from src.config import FOUNDRY_MODEL_DEPLOYMENT
from src.briefing.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.briefing.context_builder import build_context

from src.config import FOUNDRY_ENDPOINT

print("FOUNDRY_ENDPOINT:", FOUNDRY_ENDPOINT)
print("FOUNDRY_MODEL_DEPLOYMENT:", FOUNDRY_MODEL_DEPLOYMENT)


def generate_briefing():
    client = get_client()
    context = build_context()

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
