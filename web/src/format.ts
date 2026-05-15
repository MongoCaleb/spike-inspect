// Match compare.py's _fmt_err: collapse newlines, optionally extract the
// "No sample found with name '...'" snippet, then truncate.
const NO_SAMPLE_RE = /(No sample found with name '[^']*')/

export function fmtErr(s: string | null | undefined, limit = 100): string {
  if (!s) return ''
  const flat = s.replace(/\n/g, ' ').trim()
  if (!flat) return ''
  const m = NO_SAMPLE_RE.exec(flat)
  if (m) return m[1]
  return flat.length <= limit ? flat : flat.slice(0, limit - 1) + '…'
}

export function fmtScore(v: number | null | undefined): string {
  return v === null || v === undefined ? '-' : v.toFixed(3)
}

export function fmtN(n: number | null | undefined): string {
  return n === null || n === undefined ? '-' : String(n)
}

// Base URL for the inspect_ai log viewer. Override at build time with
// VITE_INSPECT_VIEW_URL if it runs elsewhere.
const INSPECT_VIEW_BASE: string =
  (import.meta as { env?: Record<string, string> }).env?.VITE_INSPECT_VIEW_URL
  || 'http://127.0.0.1:7575'

// Map an absolute .eval log path to its inspect viewer URL. Returns null when
// no log file is present (e.g. a run that errored before producing one).
export function inspectUrl(logFile: string | null | undefined): string | null {
  if (!logFile) return null
  const i = Math.max(logFile.lastIndexOf('/'), logFile.lastIndexOf('\\'))
  const base = i === -1 ? logFile : logFile.slice(i + 1)
  return `${INSPECT_VIEW_BASE}/#/tasks/${base}`
}
