"""Local translating proxy for Grove.

Holds the Grove API key in this process's env and exposes a localhost endpoint
to Inspect's anthropic SDK. Strips client-supplied auth headers and injects
`api-key:` server-side so the key never enters Inspect's process and never
lands in eval logs' model_args.

Run:
    set -a && source .env && set +a
    uv run uvicorn proxy:app --host 127.0.0.1 --port 7676

Then point Inspect at:
    --model-base-url http://127.0.0.1:7676/anthropic
    (no --model-args needed for auth)

An equivalent route is exposed at /opencode for OpenCode-style clients.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} not set. Run with `set -a && source .env && set +a` first."
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
    "/opencode/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def opencode_proxy(path: str, request: Request):
    return await _proxy("opencode", path, request)
