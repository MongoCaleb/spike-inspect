import type { RunResult } from './types'
import { fmtScore } from './format'

// Mirrors compare.print_pivot: rows=task, cols=model, cell=primary metric.
// Only renders when there are 2+ tasks AND 2+ models AND all results share
// the same primary metric name.
export function PivotTable({ results }: { results: RunResult[] }) {
  const tasks = Array.from(new Set(results.map((r) => r.task))).sort()
  const models = Array.from(new Set(results.map((r) => r.model))).sort()
  const metricNames = new Set(
    results.map((r) => r.metric_name).filter((m): m is string => !!m),
  )

  if (tasks.length < 2 || models.length < 2 || metricNames.size !== 1) {
    return null
  }
  const metricName = metricNames.values().next().value as string
  const byKey = new Map<string, RunResult>()
  for (const r of results) byKey.set(`${r.task}\u0000${r.model}`, r)

  return (
    <section>
      <details className="section">
        <summary>
          <span className="section-title">Pivot</span>{' '}
          <span className="dim">({metricName} · {tasks.length} tasks · {models.length} models)</span>
        </summary>
      <div className="table-wrap">
        <table className="grid">
          <thead>
            <tr>
              <th>task</th>
              {models.map((m) => (
                <th key={m} className="num mono">{m}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => {
              const cells = models.map((m) => byKey.get(`${t}\u0000${m}`))
              const perfectRow = cells.some((r) => r?.score === 1)
              return (
                <tr key={t} className={perfectRow ? 'row-perfect' : undefined}>
                  <td className="mono">{t}</td>
                  {cells.map((r, i) => {
                    const perfect = r?.score === 1
                    return (
                      <td key={models[i]}
                          className={'num' + (perfect ? ' cell-perfect' : '')}>
                        {r ? fmtScore(r.score) : '-'}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      </details>
    </section>
  )
}
