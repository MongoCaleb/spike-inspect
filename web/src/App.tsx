import { useEffect, useState } from 'react'
import type { Summary, SummaryEntry } from './types'
import { ResultsTable } from './ResultsTable'
import { PivotTable } from './PivotTable'

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function fmtMtime(ms: number): string {
  return new Date(ms).toLocaleString()
}

// Long human-friendly timestamp, e.g. "May 14, 2026 at 4:37 PM".
function fmtFinished(ms: number): string {
  return new Date(ms).toLocaleString(undefined, {
    dateStyle: 'long', timeStyle: 'short',
  })
}

type Theme = 'light' | 'dark'

// Initial theme: explicit user choice (localStorage) wins, otherwise fall
// back to the OS preference, otherwise dark.
function initialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') return stored
  if (window.matchMedia?.('(prefers-color-scheme: light)').matches) {
    return 'light'
  }
  return 'dark'
}

export default function App() {
  const [entries, setEntries] = useState<SummaryEntry[] | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [theme, setTheme] = useState<Theme>(initialTheme)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    fetch('/api/summaries')
      .then((r) => r.json())
      .then((es: SummaryEntry[]) => {
        setEntries(es)
        if (es.length > 0) setSelected(es[0].name)
      })
      .catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    if (!selected) return
    setLoading(true)
    setError(null)
    fetch(`/api/summaries/${encodeURIComponent(selected)}`)
      .then((r) => r.json())
      .then((s: Summary) => setSummary(s))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [selected])

  return (
    <div className="layout">
      <button
        className="theme-toggle"
        type="button"
        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      >
        {theme === 'dark' ? '☀ light' : '☾ dark'}
      </button>
      <aside className="sidebar">
        <h1>compare summaries</h1>
        {entries === null && <p className="dim">loading…</p>}
        {entries && entries.length === 0 && (
          <p className="dim">No files found in logs/summary.</p>
        )}
        <ul className="file-list">
          {entries?.map((e) => (
            <li
              key={e.name}
              className={e.name === selected ? 'active' : undefined}
              onClick={() => setSelected(e.name)}
            >
              <div className="file-name">{e.name}</div>
              <div className="file-meta">
                {fmtMtime(e.mtime)} · {fmtSize(e.size)}
              </div>
            </li>
          ))}
        </ul>
      </aside>
      <main className="content">
        <h1 className="page-title">Inspection Comparison Report</h1>
        {error && <div className="error">{error}</div>}
        {loading && <p className="dim">loading summary…</p>}
        {summary && !loading && (() => {
          const entry = entries?.find((e) => e.name === selected)
          return (
          <>
            <header className="summary-header">
              {entry && (
                <h2>
                  Evaluation Run: {fmtFinished(entry.mtime)}
                </h2>
              )}
              <div className="meta">
                <strong>log file:</strong>{' '}
                <span className="mono">{selected}</span>
              </div>
            </header>
            <ResultsTable results={summary.results} />
            <PivotTable results={summary.results} />
          </>
          )
        })()}
      </main>
    </div>
  )
}
