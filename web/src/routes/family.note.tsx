import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { toast } from 'sonner'
import { FamilyShell } from '@/components/FamilyShell'
import { useDemoProfile, useSendFamilyNote } from '@/lib/hooks'

export const Route = createFileRoute('/family/note')({
  head: () => ({
    meta: [
      { title: 'Send a note — You Little Companion' },
      {
        name: 'description',
        content:
          "Write a short note that appears on Ma's home screen, clearly marked as coming from you.",
      },
    ],
  }),
  component: SendNote,
})

const quickNotes = [
  'Love you, Ma ❤️',
  'Thinking of you today',
  'Good morning! Eat well ah',
  "Call me when you're free",
  'See you Sunday',
  'Proud of you, Ma',
]

function SendNote() {
  const { data: profile } = useDemoProfile()
  const sendNote = useSendFamilyNote(profile?.elderId)
  const [text, setText] = useState('')

  const send = (message: string) => {
    if (!profile) return
    sendNote.mutate(
      {
        elderId: profile.elderId,
        senderName: profile.familyName,
        relation: 'Your daughter',
        text: message,
      },
      {
        onSuccess: () => {
          toast("Sent to Ma's home screen", {
            description: `It's labelled as from ${profile.familyName}, her daughter.`,
          })
        },
        onError: () => {
          toast("Couldn't send that note", { description: 'Please try again.' })
        },
      },
    )
  }

  return (
    <FamilyShell
      title="Send a note"
      intro="Short notes show up right on Ma's home screen in a blue card with your name on it, so she always knows it came from you and not from the companion."
    >
      <section className="mb-6 max-w-2xl rounded-2xl border border-border bg-card p-6 shadow-soft">
        <p className="text-sm font-medium">Quick hello</p>
        <p className="mt-1 text-sm text-muted-foreground">
          One tap. Best when you're busy — a short, warm line still lands as
          your words.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {quickNotes.map((note) => (
            <button
              key={note}
              type="button"
              onClick={() => send(note)}
              disabled={sendNote.isPending}
              className="inline-flex min-h-11 items-center rounded-full border border-family/40 bg-family-soft/70 px-4 text-sm font-medium transition-transform hover:scale-[1.03] disabled:opacity-50"
            >
              {note}
            </button>
          ))}
        </div>
      </section>

      <form
        className="max-w-2xl rounded-2xl border border-border bg-card p-6 shadow-soft"
        onSubmit={(event) => {
          event.preventDefault()
          if (!text.trim()) return
          send(text.trim())
          setText('')
        }}
      >
        <label htmlFor="note" className="text-sm font-medium">
          Your note
        </label>
        <textarea
          id="note"
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={5}
          placeholder="Ma, remember to drink more water today. I'll call you tonight."
          className="mt-2 w-full resize-none rounded-xl border border-border bg-background px-4 py-3 outline-none focus:ring-2 focus:ring-ring"
        />
        <p className="mt-3 text-sm text-muted-foreground">
          Keep it short and plain — she reads these in large type. The companion
          will not rewrite, summarise or reply on your behalf.
        </p>
        <button
          type="submit"
          disabled={sendNote.isPending}
          className="mt-5 inline-flex min-h-11 items-center rounded-xl bg-primary px-6 font-semibold text-primary-foreground transition-transform hover:scale-[1.01] disabled:opacity-50"
        >
          {sendNote.isPending ? 'Sending...' : 'Send to Ma'}
        </button>
      </form>

      <section className="mt-6 max-w-2xl rounded-2xl border border-border bg-family-soft/60 p-5">
        <p className="text-sm font-semibold">How it looks to her</p>
        <div className="mt-3 rounded-2xl border-4 border-family bg-card p-4">
          <p className="font-display text-lg font-semibold">
            From {profile?.familyName ?? 'you'}
          </p>
          <p className="text-sm text-muted-foreground">
            Your daughter · a real message, not from me
          </p>
          <p className="mt-2 text-lg">
            {text.trim() || 'Your note will appear here, in her reading size.'}
          </p>
        </div>
      </section>
    </FamilyShell>
  )
}
