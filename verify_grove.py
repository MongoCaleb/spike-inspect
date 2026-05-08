"""Verify Grove + Anthropic SDK compatibility before wiring Inspect.

Grove uses Anthropic-native protocol with Azure-style auth (`api-key:` instead
of `x-api-key:`). The Anthropic SDK auto-sends `x-api-key:` from the api_key
param. The question this script answers: does Grove tolerate both headers
being present (so we can use the SDK's `default_headers` to inject `api-key:`),
or does it reject the request and force us to write a translating proxy?

Run:
    set -a && source .env && set +a
    uv run python verify_grove.py
"""

from __future__ import annotations

import os
import sys

from anthropic import Anthropic


def main() -> int:
    grove_key = os.environ.get("GROVE_API_KEY")
    grove_base = os.environ.get("GROVE_BASE_URL")
    model = os.environ.get("GROVE_MODEL", "claude-opus-4-6")

    if not grove_key or not grove_base:
        print("ERROR: GROVE_API_KEY and GROVE_BASE_URL must be set", file=sys.stderr)
        return 1

    client = Anthropic(
        # SDK requires *some* api_key. The SDK will send `x-api-key: dummy`,
        # which Grove should ignore. Real auth comes from default_headers below.
        api_key="dummy-not-used",
        base_url=grove_base,
        default_headers={"api-key": grove_key},
    )

    print(f"POST {grove_base}/v1/messages")
    print(f"  model: {model}")
    print(f"  headers: api-key=<grove>, x-api-key=dummy-not-used")
    print()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=64,
            messages=[{"role": "user", "content": "Reply with just the digit: 2+2"}],
        )
        text = response.content[0].text if response.content else "<empty>"
        print(f"OK  status=200")
        print(f"    model={response.model}  stop_reason={response.stop_reason}")
        print(f"    usage={response.usage}")
        print(f"    text={text!r}")
        return 0
    except Exception as e:
        print(f"FAIL  {type(e).__name__}: {e}")
        msg = str(e).lower()
        if "401" in msg or "403" in msg or "unauthorized" in msg or "forbidden" in msg:
            print()
            print("Auth failure - Grove likely rejects the dual-header request.")
            print("Next step: run a translating proxy that strips x-api-key.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
