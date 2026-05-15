// Mirrors compare.py: RunResult / summary JSON shape.

export interface Metric {
  scorer: string
  name: string
  value: number | null
}

export interface RunResult {
  task: string
  model: string
  base_url: string
  status: string
  score: number | null
  metric_name: string | null
  log_file: string | null
  error: string | null
  metrics: Metric[]
  samples: number | null
}

export interface Summary {
  proxy: string
  results: RunResult[]
}

export interface SummaryEntry {
  name: string
  size: number
  mtime: number
}
