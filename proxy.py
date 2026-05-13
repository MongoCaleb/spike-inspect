"""Local translating proxy for Grove.

Holds the Grove API key in this process's env and exposes a localhost endpoint
to Inspect's anthropic SDK. Strips client-supplied auth headers and injects
`api-key:` server-side so the key never enters Inspect's process and never
lands in eval logs' model_args.

`.env` (in the working directory) is auto-loaded at import time via
python-dotenv, so the proxy can be started directly:

    uv run uvicorn proxy:app --host 127.0.0.1 --port 7676

Then point Inspect at:
    --model-base-url http://127.0.0.1:7676/anthropic
    (no --model-args needed for auth)

An equivalent route is exposed at /openai for OpenAI-compatible clients
(point Inspect's `openai/` provider at `http://127.0.0.1:7676/openai`).
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Load .env from CWD without overriding values already present in the
# environment (so explicit exports still win).
load_dotenv(override=False)


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} not set. Add it to .env or export it before starting the proxy."
        )
    return value


# Drop hop-by-hop framing headers and any client-supplied auth.
# anthropic-version is preserved (Grove needs it).
HOP_BY_HOP = {
    "host",
    "x-api-key",
    "authorization",
    "content-length",
    "content-encoding",
    "transfer-encoding",
    "connection",
    "keep-alive",
    "te",
    "trailer",
    "upgrade",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.grove_base = _required_env("GROVE_BASE_URL").rstrip("/")
    app.state.grove_key = _required_env("GROVE_API_KEY")
    # Long timeout to accommodate multi-minute agent turns.
    app.state.client = httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0))
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/__health")
async def health():
    return {"ok": True, "grove_base": app.state.grove_base}


async def _proxy(route: str, path: str, request: Request):
    # Re-build headers without hop-by-hop / client auth, inject Grove auth.
    headers = {
        k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP
    }
    headers["api-key"] = app.state.grove_key

    body = await request.body()
    url = f"{app.state.grove_base}/{route}/{path}"

    upstream_req = app.state.client.build_request(
        request.method,
        url,
        headers=headers,
        content=body,
        params=request.query_params,
    )
    
    upstream = await app.state.client.send(upstream_req, stream=True)

    response_headers = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in {"content-encoding", "transfer-encoding", "content-length"}
    }

    async def stream_body():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()

    return StreamingResponse(
        stream_body(),
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


@app.api_route(
    "/anthropic/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def anthropic_proxy(path: str, request: Request):
    return await _proxy("anthropic", path, request)

@app.api_route(
    "/openai/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def openai_proxy(path: str, request: Request):
    # The OpenAI SDK treats `/v1` as part of the base URL, not the request path,
    # so it posts to `<base>/chat/completions`. Inject `v1/` so the upstream URL
    # lands at `{grove_base}/openai/v1/chat/completions` regardless of whether
    # the client's base URL includes `/v1` or not.
    if not path.startswith("v1/"):
        path = f"v1/{path}"
    return await _proxy("openai", path, request)