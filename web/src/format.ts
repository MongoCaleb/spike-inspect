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
