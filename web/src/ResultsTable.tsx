import type { RunResult } from './types'
import { fmtErr, fmtN, fmtScore } from './format'

// Mirrors compare.print_table: one row per (run, scorer, metric); falls back
// to one row per run when a run has no metrics (e.g. status=error). The
// stderr metric is filtered out, matching the Python implementation. Rows
// are nested by file (the part of the task ref before '@') and then by task
// name; both levels render as collapsed <details> on first paint.
interface Row {
  model: string
  scorer: string
  metric: string
  score: string
  scoreValue: number | null
  n: string
  error: string
  status: string
}

interface TaskGroup { taskName: string; rows: Row[]; perfectCount: number }
interface FileGroup {
  file: string
  tasks: TaskGroup[]
  rowCount: number
  perfectCount: number
}

function splitTaskRef(ref: string): [string, string] {
  const i = ref.indexOf('@')
  return i === -1 ? [ref, ''] : [ref.slice(0, i), ref.slice(i + 1)]
}

function rowsFor(r: RunResult): Row[] {
  const n = fmtN(r.samples)
  const error = fmtErr(r.error)
  const metrics = r.metrics.filter((m) => m.name !== 'stderr')
  if (metrics.length === 0) {
    return [{ model: r.model, scorer: '-', metric: '-', score: '-',
              scoreValue: null, n, error, status: r.status }]
  }
  return metrics.map((m) => ({
    model: r.model, scorer: m.scorer, metric: m.name,
    score: fmtScore(m.value), scoreValue: m.value,
    n, error, status: r.status,
  }))
}

function buildGroups(results: RunResult[]): { files: FileGroup[]; total: number } {
  // Preserve first-seen order at every level so the UI mirrors the order in
  // the source JSON (which matches compare.py's run order).
  const byFile = new Map<string, Map<string, Row[]>>()
  let total = 0
  for (const r of results) {
    const [file, taskName] = splitTaskRef(r.task)
    let taskMap = byFile.get(file)
    if (!taskMap) { taskMap = new Map(); byFile.set(file, taskMap) }
    let list = taskMap.get(taskName)
    if (!list) { list = []; taskMap.set(taskName, list) }
    const rs = rowsFor(r)
    list.push(...rs)
    total += rs.length
  }
  const files: FileGroup[] = []
  for (const [file, taskMap] of byFile) {
    const tasks: TaskGroup[] = []
    let rowCount = 0
    let filePerfect = 0
    for (const [taskName, rows] of taskMap) {
      const perfectCount = rows.reduce(
        (n, r) => n + (r.scoreValue === 1 ? 1 : 0), 0)
      tasks.push({ taskName, rows, perfectCount })
      rowCount += rows.length
      filePerfect += perfectCount
    }
    files.push({ file, tasks, rowCount, perfectCount: filePerfect })
  }
  return { files, total }
}

function PerfectBadge({ count }: { count: number }) {
  if (count === 0) return null
  return (
    <span className="perfect-badge" title={`${count} perfect score${count === 1 ? '' : 's'}`}>
      ✓ {count}
    </span>
  )
}

function RowTr({ r }: { r: Row }) {
  const perfect = r.scoreValue === 1
  const classes = [
    r.status === 'error' ? 'row-error' : '',
    perfect ? 'row-perfect' : '',
  ].filter(Boolean).join(' ') || undefined
  return (
    <tr className={classes}>
      <td className="mono">{r.model}</td>
      <td>{r.scorer}</td>
      <td>{r.metric}</td>
      <td className={'num' + (perfect ? ' cell-perfect' : '')}>{r.score}</td>
      <td className="num">{r.n}</td>
      <td className="err">{r.error}</td>
    </tr>
  )
}

function TaskBlock({ group }: { group: TaskGroup }) {
  const cls = 'group-task' + (group.perfectCount > 0 ? ' has-perfect' : '')
  return (
    <details className={cls}>
      <summary>
        <span className="mono">{group.taskName || '(no task)'}</span>{' '}
        <span className="dim">({group.rows.length} rows)</span>
        <PerfectBadge count={group.perfectCount} />
      </summary>
      <div className="table-wrap">
        <table className="grid">
          <thead>
            <tr>
              <th>model</th><th>scorer</th><th>metric</th>
              <th className="num">score</th><th className="num">n</th>
              <th>error</th>
            </tr>
          </thead>
          <tbody>
            {group.rows.map((r, i) => <RowTr key={i} r={r} />)}
          </tbody>
        </table>
      </div>
    </details>
  )
}

export function ResultsTable({ results }: { results: RunResult[] }) {
  const { files, total } = buildGroups(results)
  const totalPerfect = files.reduce((n, fg) => n + fg.perfectCount, 0)
  return (
    <section>
      <details className="section">
        <summary>
          <span className="section-title">Results</span>{' '}
          <span className="dim">({total} rows · {files.length} files)</span>
          <PerfectBadge count={totalPerfect} />
        </summary>
        {files.map((fg) => {
          const cls = 'group-file' + (fg.perfectCount > 0 ? ' has-perfect' : '')
          return (
            <details key={fg.file} className={cls}>
              <summary>
                <span className="mono">{fg.file}</span>{' '}
                <span className="dim">
                  ({fg.tasks.length} tasks · {fg.rowCount} rows)
                </span>
                <PerfectBadge count={fg.perfectCount} />
              </summary>
              {fg.tasks.map((tg) => <TaskBlock key={tg.taskName} group={tg} />)}
            </details>
          )
        })}
      </details>
    </section>
  )
}
