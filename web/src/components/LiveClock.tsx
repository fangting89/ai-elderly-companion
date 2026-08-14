import { useEffect, useState } from 'react'
import type { StringKey } from '@/lib/strings'

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

function greetingKeyForHour(hour: number): StringKey {
  if (hour < 12) return 'home_greeting_morning'
  if (hour < 18) return 'home_greeting_afternoon'
  return 'home_greeting_evening'
}

/** A time-of-day greeting key ("Good morning"/"afternoon"/"evening").
 *
 * Starts at the neutral 'home_greeting' fallback, matching what the server
 * renders (it has no reliable local time for the elder), then swaps in the
 * real time-of-day greeting once mounted client-side -- same reasoning as
 * LiveClock above. */
export function useGreetingKey(): StringKey {
  const [key, setKey] = useState<StringKey>('home_greeting')

  useEffect(() => {
    setKey(greetingKeyForHour(new Date().getHours()))
  }, [])

  return key
}
