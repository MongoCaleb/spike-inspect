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

export default function App() {
  const [entries, setEntries] = useState<SummaryEntry[] | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

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
        {error && <div className="error">{error}</div>}
        {loading && <p className="dim">loading summary…</p>}
        {summary && !loading && (
          <>
            <header className="summary-header">
              <h2>{selected}</h2>
              <div className="meta">
                <span><strong>proxy:</strong> {summary.proxy}</span>
                <span><strong>runs:</strong> {summary.results.length}</span>
                <span><strong>errors:</strong>{' '}
                  {summary.results.filter((r) => r.status === 'error').length}
                </span>
              </div>
            </header>
            <ResultsTable results={summary.results} />
            <PivotTable results={summary.results} />
          </>
        )}
      </main>
    </div>
  )
}
