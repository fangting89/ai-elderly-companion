import { Heart } from 'lucide-react'
import { useDemoProfile, useLatestFamilyNote } from '@/lib/hooks'

export function FamilyGreeting() {
  const { data: profile } = useDemoProfile()
  const { data: note } = useLatestFamilyNote(profile?.elderId)

  if (!note) return null

  return (
    <section
      key={note.id}
      className="animate-scale-in relative overflow-hidden rounded-3xl border-4 border-family bg-family-soft p-7 shadow-lift"
      aria-label="A short note from your family"
    >
      <Heart
        className="absolute -right-4 -top-4 size-28 text-family/15 animate-heart-beat"
        aria-hidden="true"
      />
      <div className="relative flex items-center gap-4">
        <span className="inline-flex size-14 shrink-0 items-center justify-center rounded-full bg-family font-display text-2xl font-semibold text-family-foreground">
          {note.senderName[0]}
        </span>
        <div className="min-w-0">
          <p className="font-display text-xl font-semibold">
            From {note.senderName}
          </p>
          <p className="text-base text-muted-foreground">
            {note.relation ? `${note.relation} · ` : ''}
            {new Date(note.createdAt).toLocaleTimeString('en-SG', {
              hour: 'numeric',
              minute: '2-digit',
            })}
          </p>
        </div>
      </div>
      <p className="relative mt-5 font-display text-3xl leading-snug font-semibold">
        {note.text}
      </p>
    </section>
  )
}
