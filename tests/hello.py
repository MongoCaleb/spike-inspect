"""Hello-world tasks for the Inspect spike.

hello_basic exercises Inspect <-> model-provider connectivity in isolation
(no sandbox, no inspect_swe). hello_anthropic exercises the full pipeline:
Docker sandbox + inspect_swe's bridge translating Claude Code's API calls
through Inspect's configured model provider.
"""

import os

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate
from inspect_swe import claude_code, opencode


HELLO_SAMPLE = Sample(
    input="What is 2+2? Reply with just the number, nothing else.",
    target="4",
)


@task
def hello_basic() -> Task:
    """No sandbox, no inspect_swe. Confirms model-provider auth works."""
    return Task(
        dataset=[HELLO_SAMPLE],
        solver=generate(),
        scorer=includes(),
    )


@task
def hello_anthropic() -> Task:
    """Routes the same prompt through claude_code() in a Docker sandbox."""
    return Task(
        dataset=[HELLO_SAMPLE],
        solver=claude_code(),
        scorer=includes(),
        sandbox="docker",
    )

@task
def hello_openai() -> Task:
    """Routes the same prompt through opencode() in a Docker sandbox, using
    the OpenAI Chat Completions protocol end-to-end.

    OpenCode's default `opencode_model` is `anthropic/...`, which makes it
    format requests as Anthropic Messages (`/v1/messages`). To exercise the
    proxy's `/openai/` route, OpenCode must format requests as OpenAI Chat
    Completions, and Inspect's host client must be the OpenAI provider
    pointed at the proxy's `/openai/` base URL.

    Invoke with:
        uv run inspect eval tasks/hello.py@hello_openai \\
            --model "$OPENAI_MODEL" \\
            --model-base-url "http://127.0.0.1:7676/openai"

    `$OPENAI_MODEL` is in `provider/id` form (e.g. `openai/gpt-4o`); passing
    `openai/$ANTHROPIC_MODEL` would send an Anthropic model id to Grove's
    OpenAI endpoint and get rejected with `api_not_supported`.
    """
    opencode_model = os.environ.get("OPENAI_MODEL") or "openai/gpt-4o"
    return Task(
        dataset=[HELLO_SAMPLE],
        solver=opencode(opencode_model=opencode_model),
        scorer=includes(),
        sandbox="docker",
    )

