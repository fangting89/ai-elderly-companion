import { Link } from '@tanstack/react-router'
import {
  BookHeart,
  Home,
  PenLine,
  Pill,
  Settings,
  LayoutGrid,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { useDemoProfile } from '@/lib/hooks'

const nav = [
  { to: '/family', label: 'Overview', icon: LayoutGrid, exact: true },
  { to: '/family/note', label: 'Send a note', icon: PenLine, exact: false },
  { to: '/family/medication', label: 'Medication', icon: Pill, exact: false },
  { to: '/family/memory', label: 'Memory bank', icon: BookHeart, exact: false },
  { to: '/family/settings', label: 'Settings', icon: Settings, exact: false },
] as const

export function FamilyShell({
  title,
  intro,
  children,
}: {
  title: string
  intro: string
  children: ReactNode
}) {
  const { data: profile } = useDemoProfile()

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-5 py-8 lg:flex-row lg:gap-10 lg:py-12">
        <aside className="lg:w-60 lg:shrink-0">
          <div className="mb-6">
            <p className="font-display text-lg font-semibold">
              You Little Companion
            </p>
            <p className="text-sm text-muted-foreground">
              Family view · {profile?.familyName ?? '...'}
            </p>
          </div>
          <nav className="flex flex-wrap gap-2 lg:flex-col">
            {nav.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                activeOptions={{ exact: item.exact }}
                activeProps={{
                  className: 'bg-secondary text-foreground border-border',
                }}
                inactiveProps={{
                  className: 'border-transparent text-muted-foreground',
                }}
                className="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition-colors hover:bg-secondary/60"
              >
                <item.icon className="size-4 shrink-0" aria-hidden="true" />
                {item.label}
              </Link>
            ))}
            <Link
              to="/"
              className="mt-2 inline-flex items-center gap-2 rounded-xl border border-dashed border-border px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary/60"
            >
              <Home className="size-4 shrink-0" aria-hidden="true" />
              Ma's view
            </Link>
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="mb-8">
            <h1 className="text-3xl font-semibold">{title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              {intro}
            </p>
          </header>
          {children}
        </main>
      </div>
    </div>
  )
}

export function MetricCard({
  label,
  value,
  meaning,
  children,
}: {
  label: string
  value?: ReactNode
  meaning: string
  children?: ReactNode
}) {
  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">
      <h2 className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">
        {label}
      </h2>
      {value !== undefined ? (
        <p className="mt-2 font-display text-3xl font-semibold">{value}</p>
      ) : null}
      {children}
      <p className="mt-4 border-t border-border/70 pt-3 text-xs leading-relaxed text-muted-foreground">
        {meaning}
      </p>
    </section>
  )
}
