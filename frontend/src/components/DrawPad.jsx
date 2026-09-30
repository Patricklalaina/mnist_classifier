import { useCallback, useEffect, useRef } from 'react'

const SIZE = 280
// ~3px once the digit is scaled into the 20px box, matching MNIST stroke width.
const STROKE = 26

export default function DrawPad({ onStroke, onClear, busy }) {
  const canvasRef = useRef(null)
  const drawing = useRef(false)
  const dirty = useRef(false)
  const last = useRef({ x: 0, y: 0 })

  const reset = useCallback(() => {
    const ctx = canvasRef.current.getContext('2d')
    ctx.fillStyle = '#000000'
    ctx.fillRect(0, 0, SIZE, SIZE)
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = STROKE
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    // Back the canvas at device resolution so strokes stay smooth.
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.round(SIZE * dpr)
    canvas.height = Math.round(SIZE * dpr)
    canvas.getContext('2d').scale(dpr, dpr)
    reset()
  }, [reset])

  const posOf = (event) => {
    const rect = canvasRef.current.getBoundingClientRect()
    return {
      x: (event.clientX - rect.left) * (SIZE / rect.width),
      y: (event.clientY - rect.top) * (SIZE / rect.height),
    }
  }

  const handleDown = (event) => {
    event.preventDefault()
    const ctx = canvasRef.current.getContext('2d')
    drawing.current = true
    last.current = posOf(event)
    // a tap with no drag should still leave a mark
    ctx.beginPath()
    ctx.arc(last.current.x, last.current.y, STROKE / 2, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
    dirty.current = true
    canvasRef.current.setPointerCapture?.(event.pointerId)
  }

  const handleMove = (event) => {
    if (!drawing.current) return
    event.preventDefault()
    const ctx = canvasRef.current.getContext('2d')
    const point = posOf(event)
    // midpoint smoothing keeps fast strokes from looking like polylines
    ctx.beginPath()
    ctx.moveTo(last.current.x, last.current.y)
    ctx.quadraticCurveTo(
      last.current.x, last.current.y,
      (last.current.x + point.x) / 2, (last.current.y + point.y) / 2,
    )
    ctx.stroke()
    last.current = point
    dirty.current = true
  }

  const handleUp = (event) => {
    if (!drawing.current) return
    event.preventDefault()
    drawing.current = false
    if (dirty.current) onStroke(canvasRef.current.toDataURL('image/png'))
  }

  const handleClear = () => {
    reset()
    dirty.current = false
    onClear()
  }

  return (
    <div className="flex flex-col items-start gap-[0.9rem]">
      <canvas
        ref={canvasRef}
        style={{ width: SIZE, height: SIZE }}
        className="bg-black border border-edge rounded-2xl touch-none cursor-crosshair block"
        onPointerDown={handleDown}
        onPointerMove={handleMove}
        onPointerUp={handleUp}
        onPointerCancel={handleUp}
        onPointerLeave={handleUp}
        aria-label="Zone de dessin"
      />
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleClear}
          className="rounded-full border border-edge px-[1.1rem] py-[0.4rem] text-[0.82rem]
                     font-semibold text-ink-faint hover:text-ink hover:border-[#4a4a45]
                     transition-colors"
        >
          Effacer
        </button>
        <span className="note">{busy ? 'Évaluation…' : 'Évalué à la fin de chaque trait'}</span>
      </div>
    </div>
  )
}
