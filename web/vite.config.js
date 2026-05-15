import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { resolve, join } from 'node:path';
// Serves the repo's logs/summary directory through the dev server:
//   GET /api/summaries          -> [{ name, size, mtime }, ...]
//   GET /api/summaries/<name>   -> the raw JSON file
// Paths are restricted to the resolved summaries dir to keep traversal out.
function summariesPlugin(summariesDir) {
    return {
        name: 'summaries',
        configureServer: function (server) {
            server.middlewares.use('/api/summaries', function (req, res, next) {
                try {
                    var url = req.url || '/';
                    if (url === '/' || url === '') {
                        var entries = readdirSync(summariesDir)
                            .filter(function (f) { return f.endsWith('.json'); })
                            .map(function (f) {
                            var s = statSync(join(summariesDir, f));
                            return { name: f, size: s.size, mtime: s.mtimeMs };
                        })
                            .sort(function (a, b) { return b.mtime - a.mtime; });
                        res.setHeader('content-type', 'application/json');
                        res.end(JSON.stringify(entries));
                        return;
                    }
                    var name_1 = decodeURIComponent(url.replace(/^\//, ''));
                    if (name_1.includes('/') || name_1.includes('..') || !name_1.endsWith('.json')) {
                        res.statusCode = 400;
                        res.end('bad request');
                        return;
                    }
                    var full = join(summariesDir, name_1);
                    res.setHeader('content-type', 'application/json');
                    res.end(readFileSync(full));
                }
                catch (e) {
                    res.statusCode = 500;
                    res.end(String(e));
                }
                void next;
            });
        },
    };
}
export default defineConfig({
    plugins: [
        react(),
        summariesPlugin(resolve(__dirname, '..', 'logs', 'summary')),
    ],
    server: { port: 5173 },
});
