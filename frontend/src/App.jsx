import { useCallback, useEffect, useRef, useState } from 'react'
import DrawPad from './components/DrawPad.jsx'
import ResultPanel from './components/ResultPanel.jsx'
import { predictDataUrl, predictFile, randomSample } from './api.js'

const TABS = [
  { id: 'draw', label: 'Dessiner' },
  { id: 'upload', label: 'Importer une image' },
  { id: 'sample', label: 'Exemple MNIST' },
]

export default function App() {
  const [tab, setTab] = useState('draw')
  const [result, setResult] = useState(null)
  const [input, setInput] = useState(null)
  const [caption, setCaption] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const fileRef = useRef(null)

  const clear = useCallback(() => {
    setResult(null)
    setInput(null)
    setCaption(null)
    setError(null)
  }, [])

  // Each submission supersedes the previous one, whichever tab it came from.
  const submit = useCallback(async (run, preview, label) => {
    setBusy(true)
    setError(null)
    try {
      const prediction = await run()
      setResult(prediction)
      setInput(preview)
      setCaption(label ?? null)
    } catch (err) {
      setResult(null)
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }, [])

  const onStroke = useCallback(
    (dataUrl) => submit(() => predictDataUrl(dataUrl), dataUrl),
    [submit],
  )

  const onFile = useCallback((event) => {
    const file = event.target.files?.[0]
    if (!file) return
    const preview = URL.createObjectURL(file)
    submit(() => predictFile(file), preview)
  }, [submit])

  const onSample = useCallback(async () => {
    setBusy(true)
    setError(null)
    try {
      const { image, label } = await randomSample()
      const prediction = await predictDataUrl(image)
      setResult(prediction)
      setInput(image)
      setCaption(`Étiquette réelle : ${label}`)
    } catch (err) {
      setResult(null)
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }, [])

  useEffect(() => { document.title = 'MNIST' }, [])

  return (
    <div className="max-w-[1080px] mx-auto px-4 pt-14 pb-20">
      <header className="mb-9">
        <h1 className="text-[2rem] font-bold tracking-[-0.02em] mb-[0.35rem]">MNIST</h1>
        <p className="text-ink-faint text-[0.9rem]">
          Testez le classifieur de chiffres manuscrits.
        </p>
      </header>

      <nav className="flex gap-4 border-b border-edge mb-6" role="tablist">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            role="tab"
            aria-selected={tab === id}
            onClick={() => setTab(id)}
            className={`text-[0.9rem] pb-2 -mb-px border-b-2 transition-colors ${
              tab === id
                ? 'text-ink border-accent'
                : 'text-ink-faint border-transparent hover:text-ink'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      <section className="mb-8">
        {tab === 'draw' && (
          <>
            <DrawPad onStroke={onStroke} onClear={clear} busy={busy} />
            <p className="note mt-4">
              Tracez un chiffre bien centré et assez épais.
            </p>
          </>
        )}

        {tab === 'upload' && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/bmp,image/webp"
              onChange={onFile}
              className="block w-full text-[0.85rem] text-ink-faint
                         file:mr-4 file:rounded-full file:border-0 file:bg-accent
                         file:px-5 file:py-2 file:text-[0.85rem] file:font-semibold
                         file:text-white hover:file:bg-accent-hover file:cursor-pointer
                         rounded-xl border border-dashed border-edge bg-[#161615] p-4"
            />
            <p className="note mt-3">
              Fond clair ou sombre, peu importe : la polarité de l'encre est
              détectée automatiquement.
            </p>
          </>
        )}

        {tab === 'sample' && (
          <>
            <button
              type="button"
              onClick={onSample}
              disabled={busy}
              className="rounded-full bg-accent hover:bg-accent-hover disabled:opacity-60
                         px-[1.4rem] py-[0.55rem] text-[0.9rem] font-semibold text-white
                         transition-colors"
            >
              Tirer un chiffre au hasard
            </button>
            <p className="note mt-3">
              Un chiffre du jeu de test, avec son étiquette réelle pour comparer.
            </p>
          </>
        )}
      </section>

      {error && (
        <div className="card" role="alert">
          <p className="card-label">Erreur</p>
          <p className="text-ink-muted m-0">{error}</p>
        </div>
      )}

      {result && !error && (
        <ResultPanel result={result} input={input} caption={caption} />
      )}
    </div>
  )
}
