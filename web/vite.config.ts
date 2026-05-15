import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { resolve, join } from 'node:path'

// Serves the repo's logs/summary directory through the dev server:
//   GET /api/summaries          -> [{ name, size, mtime }, ...]
//   GET /api/summaries/<name>   -> the raw JSON file
// Paths are restricted to the resolved summaries dir to keep traversal out.
function summariesPlugin(summariesDir: string): Plugin {
  return {
    name: 'summaries',
    configureServer(server) {
      server.middlewares.use('/api/summaries', (req, res, next) => {
        try {
          const url = req.url || '/'
          if (url === '/' || url === '') {
            const entries = readdirSync(summariesDir)
              .filter((f) => f.endsWith('.json'))
              .map((f) => {
                const s = statSync(join(summariesDir, f))
                return { name: f, size: s.size, mtime: s.mtimeMs }
              })
              .sort((a, b) => b.mtime - a.mtime)
            res.setHeader('content-type', 'application/json')
            res.end(JSON.stringify(entries))
            return
          }
          const name = decodeURIComponent(url.replace(/^\//, ''))
          if (name.includes('/') || name.includes('..') || !name.endsWith('.json')) {
            res.statusCode = 400
            res.end('bad request')
            return
          }
          const full = join(summariesDir, name)
          res.setHeader('content-type', 'application/json')
          res.end(readFileSync(full))
        } catch (e) {
          res.statusCode = 500
          res.end(String(e))
        }
        void next
      })
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    summariesPlugin(resolve(__dirname, '..', 'logs', 'summary')),
  ],
  server: { port: 5173 },
})
