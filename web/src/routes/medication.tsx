import { createFileRoute } from '@tanstack/react-router'
import { toast } from 'sonner'
import { ElderShell } from '@/components/ElderShell'
import { LiveClock } from '@/components/LiveClock'
import { useDemoProfile, useMarkDoseTaken, useTodaysDoses } from '@/lib/hooks'
import { getString } from '@/lib/strings'

export const Route = createFileRoute('/medication')({
  head: () => ({ meta: [{ title: 'Medicine today: You Little Companion' }] }),
  component: Medication,
})

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-SG', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function Medication() {
  const { data: profile } = useDemoProfile()
  const language = profile?.preferredLanguage ?? 'English'
  const { data: doses, isLoading } = useTodaysDoses(profile?.elderId)
  const markTaken = useMarkDoseTaken(profile?.elderId)
  const remaining = doses?.filter((d) => d.status !== 'taken').length ?? 0

  return (
    <ElderShell
      title={getString(language, 'medication_title')}
      subtitle={
        <>
          {remaining} {getString(language, 'medication_subtitle')} ·{' '}
          <LiveClock />
        </>
      }
    >
      {isLoading ? (
        <p className="elder-body text-muted-foreground">
          {getString(language, 'medication_loading')}
        </p>
      ) : !doses || doses.length === 0 ? (
        <div className="rounded-3xl border-2 border-dashed border-border bg-card p-8 text-center shadow-soft">
          <p className="elder-body">
            {getString(language, 'medication_empty_title')}
          </p>
          <p className="mt-2 text-muted-foreground">
            {getString(language, 'medication_empty_body')}
          </p>
        </div>
      ) : (
        <div className="grid gap-5">
          {doses.map((dose) => (
            <div
              key={dose.logId}
              className={`rounded-3xl border-2 p-6 shadow-soft ${
                dose.status === 'taken'
                  ? 'border-calm bg-calm/40'
                  : dose.status === 'missed'
                    ? 'border-caution/60 bg-caution/10'
                    : 'border-border bg-card'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-display text-2xl font-semibold">
                    {dose.medicationName}
                  </p>
                  <p className="mt-1 elder-body text-muted-foreground">
                    {dose.dosage}
                  </p>
                </div>
                <p className="shrink-0 text-lg font-semibold">
                  {formatTime(dose.scheduledFor)}
                </p>
              </div>
              <div className="mt-4">
                {dose.status === 'taken' ? (
                  <span className="inline-flex items-center gap-2 text-lg font-semibold text-calm-foreground">
                    ✓ {getString(language, 'medication_taken_label')}
                  </span>
                ) : (
                  <>
                    {dose.status === 'missed' ? (
                      <p className="mb-3 text-lg font-semibold text-caution-foreground">
                        {getString(language, 'medication_missed_label')}
                      </p>
                    ) : null}
                    <button
                      type="button"
                      onClick={() =>
                        markTaken.mutate(dose.logId, {
                          onError: () =>
                            toast("Couldn't save that", {
                              description: 'Please try again in a moment.',
                            }),
                        })
                      }
                      disabled={markTaken.isPending}
                      className="inline-flex min-h-14 items-center gap-2 rounded-2xl bg-primary px-6 text-lg font-semibold text-primary-foreground shadow-soft transition-transform hover:scale-[1.02] disabled:opacity-50"
                    >
                      ✓ {getString(language, 'medication_mark_taken_button')}
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="mx-auto mt-10 max-w-xl text-center elder-body text-muted-foreground">
        {getString(language, 'medication_disclaimer')}
      </p>
    </ElderShell>
  )
}
