"""Hello-world tasks for the Inspect spike.

hello_basic exercises Inspect <-> model-provider connectivity in isolation
(no sandbox, no inspect_swe). hello_anthropic exercises the full pipeline:
Docker sandbox + inspect_swe's bridge translating Claude Code's API calls
through Inspect's configured model provider.
"""

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
def hello_opencode() -> Task:
    """Routes the same prompt through opencode() in a Docker sandbox."""
    return Task(
        dataset=[HELLO_SAMPLE],
        solver=opencode(),
        scorer=includes(),
        sandbox="docker",
    )

