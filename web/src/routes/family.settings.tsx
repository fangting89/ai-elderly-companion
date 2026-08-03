import { createFileRoute } from '@tanstack/react-router'
import { toast } from 'sonner'
import { FamilyShell } from '@/components/FamilyShell'
import { useDemoProfile, useSetLanguage } from '@/lib/hooks'
import type { Language } from '@/lib/api'

export const Route = createFileRoute('/family/settings')({
  head: () => ({ meta: [{ title: 'Settings — You Little Companion' }] }),
  component: FamilySettings,
})

const languages: Language[] = ['English', 'Mandarin Chinese', 'Malay', 'Tamil']

function FamilySettings() {
  const { data: profile } = useDemoProfile()
  const setLanguage = useSetLanguage()

  return (
    <FamilyShell
      title="Settings"
      intro="A few basics for how the companion talks with Ma."
    >
      <section className="max-w-md rounded-2xl border border-border bg-card p-6 shadow-soft">
        <label htmlFor="language" className="text-sm font-medium">
          Ma's preferred language
        </label>
        <select
          id="language"
          value={profile?.preferredLanguage ?? 'English'}
          disabled={!profile || setLanguage.isPending}
          onChange={(event) => {
            if (!profile) return
            const language = event.target.value as Language
            setLanguage.mutate(
              { elderId: profile.elderId, language },
              {
                onSuccess: () =>
                  toast('Language updated', {
                    description:
                      'Every screen she sees will now show in this language.',
                  }),
                onError: () =>
                  toast("Couldn't update the language", {
                    description: 'Please try again.',
                  }),
              },
            )
          }}
          className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
        >
          {languages.map((lang) => (
            <option key={lang} value={lang}>
              {lang}
            </option>
          ))}
        </select>
        <p className="mt-3 text-sm text-muted-foreground">
          The companion always replies in this language, never a translated
          draft.
        </p>
      </section>
    </FamilyShell>
  )
}
