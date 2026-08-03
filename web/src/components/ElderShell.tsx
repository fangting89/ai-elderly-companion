import { Link } from '@tanstack/react-router'
import { ArrowLeft, Home } from 'lucide-react'
import type { ReactNode } from 'react'
import { useWeather } from '@/lib/weather'
import type { WeatherScene } from '@/lib/weather'
import { useDemoProfile } from '@/lib/hooks'
import { getString } from '@/lib/strings'
import type { StringKey } from '@/lib/strings'
import { LiveClock } from '@/components/LiveClock'

const SCENE_BLURB_KEY: Record<string, StringKey> = {
  clear: 'weather_blurb_clear',
  cloudy: 'weather_blurb_cloudy',
  rain: 'weather_blurb_rain',
  storm: 'weather_blurb_storm',
}
const SCENE_BLURB_KEY_NIGHT: Record<string, StringKey> = {
  clear: 'weather_blurb_clear_night',
  cloudy: 'weather_blurb_cloudy_night',
  rain: 'weather_blurb_rain_night',
  storm: 'weather_blurb_storm_night',
}

// Same weather data WeatherNow shows, carried through as page background --
// "full" (Home only) is the actual animated scene; "subtle" (every other
// elder page) is just a static tint so the app doesn't whiplash between one
// lush page and four flat ones, without competing for attention where the
// elder needs to read something carefully (a dosage, a photographed letter).
const SUBTLE_TINT: Record<WeatherScene, string> = {
  clear: 'bg-gradient-to-b from-caution/12 via-transparent to-transparent',
  cloudy: 'bg-gradient-to-b from-muted/50 via-transparent to-transparent',
  rain: 'bg-gradient-to-b from-family/10 via-transparent to-transparent',
  storm: 'bg-gradient-to-b from-family/16 via-transparent to-transparent',
}

// A dark scrim layered over the day tint at night -- each scene keeps its
// own hue and decorations (sun vs. clouds vs. rain), just dimmed and starred
// differently, rather than one universal "night mode" look.
const NIGHT_OVERLAY =
  'bg-gradient-to-b from-foreground/25 via-foreground/10 to-transparent'

// How many stars each scene shows at night -- a clear sky shows the most,
// a storm shows none (the sky is covered), matching what's actually visible.
const STAR_COUNT: Record<WeatherScene, number> = {
  clear: 7,
  cloudy: 3,
  rain: 1,
  storm: 0,
}
const STAR_POSITIONS = [
  { top: '8%', left: '15%' },
  { top: '14%', left: '62%' },
  { top: '5%', left: '80%' },
  { top: '20%', left: '35%' },
  { top: '11%', left: '48%' },
  { top: '25%', left: '72%' },
  { top: '17%', left: '8%' },
]

function Stars({ count }: { count: number }) {
  if (count === 0) return null
  return (
    <>
      {STAR_POSITIONS.slice(0, count).map((pos) => (
        <span
          key={`${pos.top}-${pos.left}`}
          className="absolute block size-1 rounded-full bg-foreground/40"
          style={pos}
        />
      ))}
    </>
  )
}

function FullWeatherScene({
  scene,
  isDay,
}: {
  scene: WeatherScene
  isDay: boolean
}) {
  const cloudOpacity = isDay ? '' : 'opacity-60'
  return (
    <div
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      aria-hidden="true"
    >
      <div className={`absolute inset-0 ${SUBTLE_TINT[scene]}`} />
      {!isDay && <div className={`absolute inset-0 ${NIGHT_OVERLAY}`} />}
      {!isDay && <Stars count={STAR_COUNT[scene]} />}

      {scene === 'clear' && isDay && (
        <>
          <span className="absolute right-[8%] top-[6%] block size-40 rounded-full bg-caution/50 blur-2xl animate-sun-pulse" />
          <span className="absolute right-[6%] top-[3%] block size-56 rounded-full border-2 border-dashed border-caution/25 animate-slow-spin" />
        </>
      )}
      {scene === 'clear' && !isDay && (
        <span className="absolute right-[10%] top-[8%] block size-24 rounded-full bg-companion-foreground/20 blur-xl" />
      )}
      {(scene === 'cloudy' || scene === 'clear') && (
        <>
          <span
            className={`absolute left-[4%] top-[10%] block h-16 w-56 rounded-full bg-card/50 animate-cloud-drift ${cloudOpacity}`}
          />
          <span
            className={`absolute left-[30%] top-[22%] block h-12 w-40 rounded-full bg-card/40 animate-cloud-drift-slow ${cloudOpacity}`}
          />
        </>
      )}
      {(scene === 'rain' || scene === 'storm') && (
        <>
          <span
            className={`absolute left-[2%] top-[6%] block h-20 w-64 rounded-full bg-card/40 animate-cloud-drift ${cloudOpacity}`}
          />
          <span
            className={`absolute left-[35%] top-[16%] block h-16 w-48 rounded-full bg-card/30 animate-cloud-drift-slow ${cloudOpacity}`}
          />
        </>
      )}
    </div>
  )
}

// Folds the weather + time of day into the header (Home only), rather than
// giving it a whole card of its own -- one fewer "block" on a page that
// already has several.
function WeatherHeaderChip({
  scene,
  isDay,
  language,
}: {
  scene: WeatherScene
  isDay: boolean
  language: Parameters<typeof getString>[0]
}) {
  const { data: weather, isLoading } = useWeather()
  const blurb = getString(
    language,
    (isDay ? SCENE_BLURB_KEY : SCENE_BLURB_KEY_NIGHT)[scene],
  )
  return (
    <div className="flex shrink-0 flex-col items-end gap-1 text-right">
      <p className="font-display text-2xl font-semibold">
        {isLoading || !weather ? '--°C' : `${weather.tempC}°C`}
      </p>
      <LiveClock className="text-sm font-medium text-muted-foreground" />
      <p className="hidden max-w-40 text-sm text-muted-foreground sm:block">
        {blurb}
      </p>
    </div>
  )
}

export function ElderShell({
  title,
  subtitle,
  children,
  showBack = true,
  weatherBackground = 'subtle',
}: {
  title: string
  subtitle?: ReactNode
  children: ReactNode
  showBack?: boolean
  weatherBackground?: 'full' | 'subtle'
}) {
  const { data: weather } = useWeather()
  const { data: profile } = useDemoProfile()
  const language = profile?.preferredLanguage ?? 'English'
  const scene = weather?.scene ?? 'clear'
  const isDay = weather?.isDay ?? true

  return (
    <div className="min-h-screen relative paper-grain">
      {weatherBackground === 'full' ? (
        <FullWeatherScene scene={scene} isDay={isDay} />
      ) : (
        <div
          className="pointer-events-none fixed inset-0 -z-10"
          aria-hidden="true"
        >
          <div className={`absolute inset-0 ${SUBTLE_TINT[scene]}`} />
          {!isDay && <div className={`absolute inset-0 ${NIGHT_OVERLAY}`} />}
        </div>
      )}
      <header className="border-b border-border/70 bg-card/70 backdrop-blur">
        <div className="mx-auto grid max-w-3xl grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-4 px-5 py-5">
          {showBack ? (
            <Link
              to="/"
              className="inline-flex min-h-14 min-w-14 shrink-0 items-center justify-center gap-2 rounded-2xl border border-border bg-card px-4 text-lg font-semibold text-foreground transition-colors hover:bg-secondary"
              aria-label="Back to home"
            >
              <ArrowLeft className="size-6" aria-hidden="true" />
              <span className="hidden sm:inline">
                {getString(language, 'nav_home')}
              </span>
            </Link>
          ) : (
            <span className="inline-flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Home className="size-7" aria-hidden="true" />
            </span>
          )}
          <div className="min-w-0">
            <h1 className="truncate elder-title">{title}</h1>
            {subtitle ? (
              <p className="mt-1 text-lg text-muted-foreground">{subtitle}</p>
            ) : null}
          </div>
          {weatherBackground === 'full' ? (
            <WeatherHeaderChip
              scene={scene}
              isDay={isDay}
              language={language}
            />
          ) : null}
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-5 pb-16 pt-8">{children}</main>
      <footer className="pb-10 text-center">
        <Link
          to="/family"
          className="text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground"
        >
          {getString(language, 'home_family_view_link')}
        </Link>
      </footer>
    </div>
  )
}
