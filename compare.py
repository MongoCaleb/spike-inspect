"""Compare multiple (task, model) configurations against the same eval set.

Each "run" is a (task_ref, model[, base_url]) triple. Since each @task in
tasks/ already encodes the harness (generate / claude_code / opencode) and
any solver options (skills, seeds, etc.), this lets you compare across
harness, model, and options axes by listing run triples. base_url is
auto-derived from the model's provider prefix against --proxy unless
overridden in a config file.

Usage:
    # Args mode (repeatable):
    uv run python compare.py \\
        --run tasks/hello.py@hello_basic:anthropic/claude-sonnet-4-5 \\
        --run tasks/hello.py@hello_basic:openai/gpt-4o

    # Config file mode:
    uv run python compare.py --config compare.json

    # Interactive mode (no args):
    uv run python compare.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from inspect_ai import eval as inspect_eval

DEFAULT_PROXY = "http://127.0.0.1:7676"
TASKS_DIR = Path(__file__).parent / "tasks"
PROVIDER_SUFFIX = {"anthropic": "/anthropic", "openai": "/openai"}


@dataclass
class RunSpec:
    task: str
    model: str
    base_url: str | None = None

    def resolved_base_url(self, proxy: str) -> str:
        if self.base_url:
            return self.base_url
        provider = self.model.split("/", 1)[0] if "/" in self.model else ""
        return proxy.rstrip("/") + PROVIDER_SUFFIX.get(provider, "")


@dataclass
class RunResult:
    task: str
    model: str
    base_url: str
    status: str
    score: float | None  # primary metric value (first scorer, first metric)
    metric_name: str | None  # primary metric name
    log_file: str | None
    error: str | None = None
    # Full per-scorer/per-metric breakdown.
    # Each entry: {"scorer": str, "name": str, "value": float | None}
    metrics: list[dict[str, Any]] = field(default_factory=list)
    samples: int | None = None


def parse_run_arg(arg: str) -> RunSpec:
    if ":" not in arg:
        raise argparse.ArgumentTypeError(f"--run must be TASK:MODEL, got {arg!r}")
    task, model = arg.split(":", 1)
    return RunSpec(task=task.strip(), model=model.strip())


def load_config(path: Path) -> tuple[list[RunSpec], str]:
    data = json.loads(path.read_text())
    proxy = data.get("proxy", DEFAULT_PROXY)
    runs = [RunSpec(task=r["task"], model=r["model"], base_url=r.get("base_url"))
            for r in data["runs"]]
    return runs, proxy


_TASK_RE = re.compile(r"^@task(?:\([^)]*\))?\s*$", re.MULTILINE)
_DEF_RE = re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE)


def _task_refs_in_file(path: Path) -> list[str]:
    """Parse a tasks/*.py file and return its @task refs as
    'tasks/<name>.py@<func>'. Source-level scan (no import) so a single
    bad @task can't crash discovery for the rest of the file."""
    text = path.read_text()
    refs: list[str] = []
    idx = 0
    while (m := _TASK_RE.search(text, idx)):
        n = _DEF_RE.search(text, m.end())
        if not n:
            break
        refs.append(f"tasks/{path.name}@{n.group(1)}")
        idx = n.end()
    return refs


def discover_task_refs() -> list[str]:
    refs: list[str] = []
    for py in sorted(TASKS_DIR.glob("*.py")):
        if py.name.startswith("_"):
            continue
        refs.extend(_task_refs_in_file(py))
    return refs


def expand_specs(specs: list[RunSpec]) -> list[RunSpec]:
    """File-level specs (no '@func') are fanned out to one spec per @task
    in the file so a per-task materialization failure (e.g. ValueError
    from load_sample_by_name) only fails that task, not the whole file.
    Task-level specs pass through unchanged. Unparseable / missing files
    pass through so inspect_eval surfaces the underlying error."""
    out: list[RunSpec] = []
    for s in specs:
        if "@" in s.task:
            out.append(s)
            continue
        path = Path(s.task)
        if not path.is_absolute():
            path = Path(__file__).parent / s.task
        if not (path.exists() and path.suffix == ".py"):
            out.append(s)
            continue
        refs = _task_refs_in_file(path)
        if not refs:
            out.append(s)
            continue
        out.extend(RunSpec(task=ref, model=s.model, base_url=s.base_url)
                   for ref in refs)
    return out


def interactive() -> tuple[list[RunSpec], str]:
    print("No --run / --config provided. Interactive mode.\n")
    available = discover_task_refs()
    if not available:
        print("No @task functions found under tasks/.", file=sys.stderr)
        sys.exit(1)
    print("Available tasks:")
    for i, ref in enumerate(available):
        print(f"  [{i}] {ref}")
    raw = input("\nSelect task indices (comma-separated): ").strip()
    selected = [available[int(i)] for i in raw.split(",") if i.strip()]
    raw_models = input(
        "Models (comma-separated, e.g. anthropic/claude-sonnet-4-5,openai/gpt-4o): "
    ).strip()
    models = [m.strip() for m in raw_models.split(",") if m.strip()]
    proxy = input(f"Proxy URL [{DEFAULT_PROXY}]: ").strip() or DEFAULT_PROXY
    runs = [RunSpec(task=t, model=m) for t in selected for m in models]
    return runs, proxy


def _result_from_log(spec: RunSpec, base_url: str, log: Any) -> RunResult:
    metrics: list[dict[str, Any]] = []
    if log.results and log.results.scores:
        for s in log.results.scores:
            for mname, m in (s.metrics or {}).items():
                metrics.append({
                    "scorer": s.scorer or s.name,
                    "name": mname,
                    "value": float(m.value) if m.value is not None else None,
                })
    primary = metrics[0] if metrics else None
    samples = log.results.completed_samples if log.results else None
    # Derive the specific task ref from the log. When spec.task is a file
    # (no @func), inspect_eval expands to one log per @task in that file;
    # we want one RunResult per @task, each tagged with its real ref.
    task_file = getattr(log.eval, "task_file", None)
    task_name = getattr(log.eval, "task", None)
    if task_file and task_name:
        task_ref = f"{task_file}@{task_name}"
    else:
        task_ref = spec.task
    err = getattr(log.error, "message", None) if log.error else None
    return RunResult(
        task=task_ref, model=spec.model, base_url=base_url, status=log.status,
        score=primary["value"] if primary else None,
        metric_name=primary["name"] if primary else None,
        log_file=log.location, metrics=metrics, samples=samples, error=err,
    )


def run_one(spec: RunSpec, proxy: str, log_dir: str,
            display: str | None = None) -> list[RunResult]:
    """Returns a list because a file-level spec (no @func) expands to one
    EvalLog per @task in the file. `display` is forwarded to inspect_eval;
    workers in a process pool must use 'log' (or 'plain'/'none') because the
    Rich Live TUI can't attach in a spawned worker without a TTY and raises
    'I/O operation on closed file'."""
    base_url = spec.resolved_base_url(proxy)
    print(f"\n>>> {spec.task}  model={spec.model}  base_url={base_url}", flush=True)
    kwargs: dict[str, Any] = {
        "tasks": spec.task, "model": spec.model,
        "model_base_url": base_url, "log_dir": log_dir,
    }
    if display is not None:
        kwargs["display"] = display
    try:
        logs = inspect_eval(**kwargs)
    except Exception as e:
        return [RunResult(spec.task, spec.model, base_url, "error",
                          None, None, None, error=str(e))]
    return [_result_from_log(spec, base_url, log) for log in logs]


def run_parallel(specs: list[RunSpec], proxy: str, log_dir: str,
                 concurrency: int) -> list[RunResult]:
    """Process-pool parallelism. Each child has its own inspect_ai state,
    avoiding the single-instance constraint of eval_async. Workers run with
    display='log' to avoid Rich Live TUI failures in non-TTY children;
    progress lines still print to stdout (interleaved)."""
    buckets: list[list[RunResult] | None] = [None] * len(specs)
    with ProcessPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(run_one, s, proxy, log_dir, "log"): i
                   for i, s in enumerate(specs)}
        for fut in as_completed(futures):
            buckets[futures[fut]] = fut.result()
    return [r for bucket in buckets if bucket for r in bucket]


def _render(headers: list[str], rows: list[list[str]]) -> None:
    widths = [max(len(h), *(len(row[i]) for row in rows)) if rows else len(h)
              for i, h in enumerate(headers)]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


_NO_SAMPLE_RE = re.compile(r"(No sample found with name '[^']*')")


def _fmt_err(s: str | None, limit: int = 100) -> str:
    if not s:
        return "-"
    s = s.replace("\n", " ").strip()
    if (m := _NO_SAMPLE_RE.search(s)):
        return m.group(1)
    return s if len(s) <= limit else s[: limit - 1] + "…"


def print_table(results: list[RunResult]) -> None:
    """One row per (run, scorer, metric). Falls back to one row per run when
    a run has no metrics (e.g. status=error). The error column surfaces
    RunResult.error (truncated) so failures like 'No sample found with name
    ...' are visible without opening the JSON summary."""
    headers = ["task", "model", "status", "scorer", "metric", "value", "n", "error"]
    rows: list[list[str]] = []
    for r in results:
        n = "-" if r.samples is None else str(r.samples)
        err = _fmt_err(r.error)
        if not r.metrics:
            rows.append([r.task, r.model, r.status, "-", "-", "-", n, err])
            continue
        for m in r.metrics:
            v = "-" if m["value"] is None else f"{m['value']:.3f}"
            rows.append([r.task, r.model, r.status, m["scorer"],
                         m["name"], v, n, err])
    print()
    _render(headers, rows)


def print_pivot(results: list[RunResult]) -> None:
    """Pivot: rows=task, cols=model, cell=primary metric value. Only printed
    when there are 2+ unique tasks AND 2+ unique models AND all results
    share the same primary metric name."""
    tasks = sorted({r.task for r in results})
    models = sorted({r.model for r in results})
    if len(tasks) < 2 or len(models) < 2:
        return
    metric_names = {r.metric_name for r in results if r.metric_name}
    if len(metric_names) != 1:
        return
    metric_name = next(iter(metric_names))
    by_key = {(r.task, r.model): r for r in results}
    headers = ["task"] + models
    rows: list[list[str]] = []
    for t in tasks:
        row = [t]
        for m in models:
            r = by_key.get((t, m))
            row.append("-" if r is None or r.score is None else f"{r.score:.3f}")
        rows.append(row)
    print(f"\nPivot ({metric_name}):")
    _render(headers, rows)


EXAMPLES = """\
examples:
  # hello_basic against Anthropic and OpenAI, run in parallel:
  uv run python compare.py --parallel 2 \\
      --run "tasks/hello.py@hello_basic:anthropic/$ANTHROPIC_MODEL" \\
      --run "tasks/hello.py@hello_basic:$OPENAI_MODEL"

  # All @tasks in tasks/hello.py against Anthropic and OpenAI, in parallel.
  # A file-level run (no @func) expands to one result row per @task in the file:
  uv run python compare.py --parallel 2 \\
      --run "tasks/hello.py:anthropic/$ANTHROPIC_MODEL" \\
      --run "tasks/hello.py:$OPENAI_MODEL"
"""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compare task/model configurations.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--run", action="append", type=parse_run_arg, default=[],
                   help="TASK_REF:MODEL_ID (repeatable). TASK_REF may be a "
                        "file (tasks/X.py) to run every @task in it.")
    p.add_argument("--config", type=Path, help="JSON config with 'runs' list")
    p.add_argument("--proxy", default=DEFAULT_PROXY)
    p.add_argument("--output", type=Path, help="JSON summary path")
    p.add_argument("--log-dir", default="./logs")
    p.add_argument("--list-tasks", action="store_true",
                   help="Print discovered @task refs and exit.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print resolved runs and exit without calling eval().")
    p.add_argument("--parallel", type=int, default=1, metavar="N",
                   help="Max concurrent runs via a process pool (default: 1).")
    args = p.parse_args()

    if args.list_tasks:
        for ref in discover_task_refs():
            print(ref)
        return 0

    if args.config:
        runs, proxy = load_config(args.config)
    elif args.run:
        runs, proxy = args.run, args.proxy
    else:
        runs, proxy = interactive()

    if not runs:
        print("No runs specified.", file=sys.stderr)
        return 1

    # Fan out file-level specs to per-@task specs so one bad task doesn't
    # abort the rest of the file.
    runs = expand_specs(runs)

    if args.dry_run:
        print(f"proxy: {proxy}")
        print(f"log_dir: {args.log_dir}")
        print(f"runs ({len(runs)}):")
        for r in runs:
            print(f"  task={r.task}  model={r.model}  base_url={r.resolved_base_url(proxy)}")
        return 0

    if args.parallel > 1:
        results = run_parallel(runs, proxy, args.log_dir, args.parallel)
    else:
        results = [r for spec in runs for r in run_one(spec, proxy, args.log_dir)]
    print_table(results)
    print_pivot(results)

    if args.output:
        out = args.output
    else:
        out = Path(args.log_dir) / "summary" / f"compare-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"proxy": proxy, "results": [asdict(r) for r in results]}, indent=2))
    print(f"\nWrote summary to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
