// In production nginx proxies /api to the inference service; in `npm run dev`
// Vite's proxy does the same (see vite.config.js).
const BASE = import.meta.env.VITE_API_BASE || '/api'

async function unwrap(response) {
  const body = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(body.detail || `Erreur ${response.status}`)
  }
  return body
}

export function predictFile(file) {
  const form = new FormData()
  form.append('file', file)
  return fetch(`${BASE}/predict`, { method: 'POST', body: form }).then(unwrap)
}

export function predictDataUrl(image) {
  return fetch(`${BASE}/predict/data-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image }),
  }).then(unwrap)
}

export function randomSample() {
  return fetch(`${BASE}/samples/random`).then(unwrap)
}
