import { useEffect, useState } from 'react'

/** A ticking clock, updated every 30s -- no need for per-second precision
 * on elder-facing UI, and it keeps re-renders cheap.
 *
 * `now` starts null and is only set client-side in an effect: seeding it
 * from `new Date()` during render would make the server-rendered timestamp
 * and the client's first-render timestamp differ, which React treats as a
 * hydration mismatch. */
export function LiveClock({ className }: { className?: string }) {
  const [now, setNow] = useState<Date | null>(null)

  useEffect(() => {
    setNow(new Date())
    const timer = window.setInterval(() => setNow(new Date()), 30_000)
    return () => window.clearInterval(timer)
  }, [])

  if (now === null) return <span className={className} />

  const time = now.toLocaleTimeString('en-SG', {
    hour: 'numeric',
    minute: '2-digit',
  })
  const date = now.toLocaleDateString('en-SG', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  return (
    <span className={className}>
      {date} · {time}
    </span>
  )
}

export function useCurrentTime() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 30_000)
    return () => window.clearInterval(timer)
  }, [])
  return now
}
