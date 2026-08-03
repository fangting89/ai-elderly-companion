import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { Pill } from 'lucide-react'
import { toast } from 'sonner'
import { FamilyShell } from '@/components/FamilyShell'
import { useAddMedication, useDemoProfile, useMedications } from '@/lib/hooks'

export const Route = createFileRoute('/family/medication')({
  head: () => ({
    meta: [
      { title: 'Medication — You Little Companion' },
      {
        name: 'description',
        content:
          "Add and manage Ma's medications -- she can mark doses taken, not add new ones.",
      },
    ],
  }),
  component: FamilyMedication,
})

function FamilyMedication() {
  const { data: profile } = useDemoProfile()
  const { data: medications } = useMedications(profile?.elderId)
  const addMedication = useAddMedication(profile?.elderId)
  const [name, setName] = useState('')
  const [dosage, setDosage] = useState('1 tablet')
  const [timesPerDay, setTimesPerDay] = useState('08:00')

  return (
    <FamilyShell
      title="Medication"
      intro="Add what Ma takes and when. She'll see these on her own Medicine page and can mark each dose taken -- adding or changing a medication is a family-only action, on purpose."
    >
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <ul className="flex flex-col gap-3">
          {medications?.length ? (
            medications.map((med) => (
              <li
                key={med.id}
                className="flex items-center gap-3 rounded-2xl border border-border bg-card p-5 shadow-soft"
              >
                <span className="inline-flex size-11 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary">
                  <Pill className="size-5" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="font-semibold">{med.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {med.dosage} · {med.timesPerDay.join(', ')}
                  </p>
                </div>
              </li>
            ))
          ) : (
            <li className="rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
              No medications added yet.
            </li>
          )}
        </ul>

        <form
          className="h-fit rounded-2xl border border-border bg-card p-5 shadow-soft"
          onSubmit={(event) => {
            event.preventDefault()
            if (!profile || !name.trim() || !timesPerDay.trim()) return
            addMedication.mutate(
              {
                elderId: profile.elderId,
                name: name.trim(),
                dosage: dosage.trim(),
                timesPerDay,
              },
              {
                onSuccess: () => {
                  toast('Added', {
                    description: `${name.trim()} will show up on her Medicine page.`,
                  })
                  setName('')
                  setDosage('1 tablet')
                  setTimesPerDay('08:00')
                },
                onError: () =>
                  toast("Couldn't add that medication", {
                    description: 'Please try again.',
                  }),
              },
            )
          }}
        >
          <p className="font-semibold">Add a medication</p>
          <label htmlFor="med-name" className="mt-4 block text-sm font-medium">
            Name
          </label>
          <input
            id="med-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Metformin"
            className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
          />
          <label
            htmlFor="med-dosage"
            className="mt-4 block text-sm font-medium"
          >
            Dosage
          </label>
          <input
            id="med-dosage"
            value={dosage}
            onChange={(event) => setDosage(event.target.value)}
            placeholder="1 tablet, after breakfast"
            className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
          />
          <label htmlFor="med-times" className="mt-4 block text-sm font-medium">
            Times per day
          </label>
          <input
            id="med-times"
            value={timesPerDay}
            onChange={(event) => setTimesPerDay(event.target.value)}
            placeholder="08:00, 20:00"
            className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
          />
          <p className="mt-2 text-xs text-muted-foreground">
            Comma-separated 24-hour times, e.g. 08:00, 20:00
          </p>
          <button
            type="submit"
            disabled={addMedication.isPending}
            className="mt-4 inline-flex min-h-11 w-full items-center justify-center rounded-xl bg-primary font-semibold text-primary-foreground disabled:opacity-50"
          >
            {addMedication.isPending ? 'Adding...' : 'Add medication'}
          </button>
        </form>
      </div>
    </FamilyShell>
  )
}
