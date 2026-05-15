import type { RunResult } from './types'
import { fmtScore, inspectUrl } from './format'

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

  // Count present cells in a slice and how many equal 1.0. Missing cells are
  // ignored so a sparse pivot still classifies cleanly. The CSS suffix is
  // '' / '-some' / '-all' depending on the present-vs-perfect counts.
  const tally = (cells: (RunResult | undefined)[]) => {
    let present = 0
    let perfect = 0
    for (const c of cells) {
      if (!c) continue
      present++
      if (c.score === 1) perfect++
    }
    const suffix =
      present === 0 || perfect === 0
        ? ''
        : perfect === present
          ? '-all'
          : '-some'
    return { present, perfect, suffix }
  }

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
              {models.map((m) => {
                const colCells = tasks.map((t) => byKey.get(`${t}\u0000${m}`))
                const { present, perfect, suffix } = tally(colCells)
                const countCls =
                  'col-count' + (suffix ? ' col-count' + suffix : ' col-count-none')
                return (
                  <th key={m} className="num mono">
                    <div>{m}</div>
                    {present > 0 && (
                      <div className={countCls}>{perfect}/{present} perfect</div>
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => {
              const cells = models.map((m) => byKey.get(`${t}\u0000${m}`))
              const { suffix: rowSuffix } = tally(cells)
              const rowCls = rowSuffix ? 'row-perfect' + rowSuffix : undefined
              return (
                <tr key={t} className={rowCls}>
                  <td className="mono">{t}</td>
                  {cells.map((r, i) => {
                    const perfect = r?.score === 1
                    const url = inspectUrl(r?.log_file)
                    const text = r ? fmtScore(r.score) : '-'
                    return (
                      <td key={models[i]}
                          className={'num' + (perfect ? ' cell-perfect' : '')}>
                        {url ? (
                          <a className="inspect-link" href={url}
                             target="_blank" rel="noreferrer"
                             title={r?.log_file ?? ''}>{text}</a>
                        ) : text}
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
