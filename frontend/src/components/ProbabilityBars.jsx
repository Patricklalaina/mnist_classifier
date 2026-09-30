/**
 * Ten magnitudes, one series — so one colour throughout. The winning row is
 * marked by type weight and bar length, never by a second hue, and every row
 * carries its own value label.
 */
export default function ProbabilityBars({ probabilities, predicted }) {
  return (
    <div>
      {probabilities.map((p, digit) => {
        const top = digit === predicted
        return (
          <div
            key={digit}
            className="grid grid-cols-[1.25rem_1fr_3.25rem] items-center gap-[0.85rem] py-[0.3rem]"
          >
            <div className={`tabular-nums text-[0.9rem] text-center ${
              top ? 'text-ink font-semibold' : 'text-ink-faint'}`}>
              {digit}
            </div>
            <div className="h-[10px] bg-track rounded-[5px] overflow-hidden">
              <div
                className="h-full bg-accent rounded-r-[4px] min-w-[2px]"
                style={{ width: `${(p * 100).toFixed(4)}%` }}
              />
            </div>
            <div className={`tabular-nums text-[0.8rem] text-right ${
              top ? 'text-ink font-semibold' : 'text-ink-faint'}`}>
              {(p * 100).toFixed(1)}%
            </div>
          </div>
        )
      })}
    </div>
  )
}
