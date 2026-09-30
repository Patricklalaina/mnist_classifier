import ProbabilityBars from './ProbabilityBars.jsx'

export default function ResultPanel({ result, input, caption }) {
  return (
    <div className="grid gap-4 md:grid-cols-[1fr_1.15fr] items-start">
      <div className="grid gap-4">
        <div className="card">
          <p className="card-label">Entrée</p>
          <img
            src={input}
            alt="Image soumise"
            className="block w-full max-h-[300px] object-contain rounded-xl bg-black"
          />
        </div>

        <div className="card">
          <p className="card-label">Ce que voit le modèle · 28×28</p>
          <img
            src={result.preview}
            alt="Image 28 par 28 reçue par le modèle"
            /* 28px of source upscaled crisply, rather than sitting tiny in the box */
            className="block w-[260px] h-[260px] mx-auto object-fill rounded-xl bg-black
                       [image-rendering:pixelated]"
          />
          <p className="note mt-3">
            Recadré, mis à l'échelle sur 20 px et centré par centre de masse,
            comme les images d'entraînement.
          </p>
        </div>
      </div>

      <div className="grid gap-4">
        <div className="card">
          {caption && <p className="note mb-2">{caption}</p>}
          <div className="text-center py-2 pb-5">
            <div className="text-[7rem] leading-none font-bold tracking-[-0.05em]">
              {result.digit}
            </div>
            <div className="text-ink-muted text-[0.95rem] mt-[0.6rem]">
              confiance{' '}
              <b className="text-accent font-semibold">
                {(result.confidence * 100).toFixed(1)}%
              </b>
            </div>
          </div>
        </div>

        <div className="card">
          <p className="card-label">Probabilité par chiffre</p>
          <ProbabilityBars
            probabilities={result.probabilities}
            predicted={result.digit}
          />
        </div>
      </div>
    </div>
  )
}
