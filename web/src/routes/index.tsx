import { createFileRoute, Link } from '@tanstack/react-router'
import { CalendarDays, Camera, Pill, Users } from 'lucide-react'
import { toast } from 'sonner'
import { ElderShell } from '@/components/ElderShell'
import { PhotoDeck } from '@/components/PhotoDeck'
import { FamilyGreeting } from '@/components/FamilyGreeting'
import { CheckInPrompt } from '@/components/CheckInPrompt'
import { useDemoProfile } from '@/lib/hooks'
import { getString } from '@/lib/strings'

export const Route = createFileRoute('/')({
  head: () => ({
    meta: [
      { title: 'Home: You Little Companion' },
      {
        name: 'description',
        content:
          "A calm home screen for chatting, asking about letters, medication reminders and what's on today.",
      },
    ],
  }),
  component: ElderHome,
})

function ElderHome() {
  const { data: profile } = useDemoProfile()
  const language = profile?.preferredLanguage ?? 'English'

  const actions = [
    {
      to: '/point-ask' as const,
      label: getString(language, 'nav_point_and_ask'),
      hint: getString(language, 'home_hint_point_and_ask'),
      icon: Camera,
    },
    {
      to: '/medication' as const,
      label: getString(language, 'nav_medication'),
      hint: getString(language, 'home_hint_medication'),
      icon: Pill,
    },
    {
      to: '/calendar' as const,
      label: getString(language, 'nav_calendar'),
      hint: getString(language, 'home_hint_calendar'),
      icon: CalendarDays,
    },
  ]

  return (
    <ElderShell
      title={`${getString(language, 'home_greeting')}, ${profile?.elderName ?? 'Mdm Tan'}`}
      showBack={false}
      weatherBackground="full"
    >
      <div className="grid gap-5">
        <PhotoDeck />
        <FamilyGreeting />
      </div>

      <CheckInPrompt />

      <div className="mt-8 flex flex-col gap-4">
        {actions.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className="flex items-center gap-5 rounded-3xl border-2 border-border bg-card p-6 shadow-soft transition-all hover:-translate-y-0.5 hover:border-primary hover:shadow-lift"
          >
            <span className="inline-flex size-14 shrink-0 items-center justify-center rounded-2xl bg-secondary text-primary">
              <action.icon className="size-8" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="block font-display text-2xl font-semibold">
                {action.label}
              </span>
              <span className="block text-lg text-muted-foreground">
                {action.hint}
              </span>
            </span>
          </Link>
        ))}
      </div>

      <section className="mt-8 rounded-3xl border border-border bg-accent/50 p-7">
        <div className="flex items-start gap-4">
          <span className="inline-flex size-14 shrink-0 items-center justify-center rounded-2xl bg-card text-accent-foreground">
            <Users className="size-7" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <h2 className="font-display text-2xl font-semibold">
              {getString(language, 'home_happening_title')}
            </h2>
            <p className="mt-2 elder-body">
              {getString(language, 'home_happening_body')}
            </p>
            <button
              type="button"
              onClick={() =>
                toast(
                  getString(language, 'home_happening_reminder_toast_title'),
                  {
                    description: getString(
                      language,
                      'home_happening_reminder_toast_body',
                    ),
                  },
                )
              }
              className="mt-5 inline-flex min-h-14 items-center rounded-2xl border-2 border-border bg-card px-6 text-lg font-semibold transition-colors hover:bg-secondary"
            >
              {getString(language, 'home_happening_button')}
            </button>
          </div>
        </div>
      </section>

      <p className="mx-auto mt-10 max-w-xl text-center text-lg leading-relaxed text-muted-foreground">
        {getString(language, 'home_boundary_statement')}
      </p>
    </ElderShell>
  )
}
