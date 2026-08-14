import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { NotebookText, CalendarPlus } from 'lucide-react'
import { toast } from 'sonner'
import { ElderShell } from '@/components/ElderShell'
import { useAddCalendarEvent, useCalendarEvents, useDemoProfile } from '@/lib/hooks'
import { getString } from '@/lib/strings'

export const Route = createFileRoute('/calendar')({
  head: () => ({
    meta: [{ title: "What's coming up: You Little Companion" }],
  }),
  component: Calendar,
})

function formatEventTime(iso: string) {
  const date = new Date(iso)
  return date.toLocaleString('en-SG', {
    weekday: 'long',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function Calendar() {
  const { data: profile } = useDemoProfile()
  const { data: events, isLoading } = useCalendarEvents(profile?.elderId)
  const addEvent = useAddCalendarEvent(profile?.elderId)
  const language = profile?.preferredLanguage ?? 'English'
  const [isAdding, setIsAdding] = useState(false)
  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [notes, setNotes] = useState('')

  const resetForm = () => {
    setTitle('')
    setDate('')
    setTime('')
    setNotes('')
    setIsAdding(false)
  }

  return (
    <ElderShell
      title={getString(language, 'calendar_title')}
      subtitle={getString(language, 'calendar_subtitle')}
    >
      <div className="grid gap-5">
        {isLoading ? (
          <p className="elder-body text-muted-foreground">Loading...</p>
        ) : !events || events.length === 0 ? (
          <p className="elder-body text-muted-foreground">
            {getString(language, 'calendar_no_events_message')}
          </p>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="rounded-3xl border-2 border-border bg-card p-6 shadow-soft"
            >
              <p className="text-base font-semibold uppercase tracking-wide text-primary">
                {formatEventTime(event.startTime)}
              </p>
              <p className="mt-2 font-display text-2xl font-semibold">
                {event.title}
              </p>
              {event.notes ? (
                <p className="mt-2 flex items-center gap-2 elder-body text-muted-foreground">
                  <NotebookText className="size-5 shrink-0" aria-hidden="true" />
                  {event.notes}
                </p>
              ) : null}
            </div>
          ))
        )}

        {isAdding ? (
          <form
            className="rounded-3xl border-2 border-border bg-card p-6 shadow-soft"
            onSubmit={(event) => {
              event.preventDefault()
              if (!profile || !title.trim() || !date || !time) return
              addEvent.mutate(
                {
                  elderId: profile.elderId,
                  title: title.trim(),
                  startTime: `${date}T${time}`,
                  notes: notes.trim(),
                },
                {
                  onSuccess: () => {
                    toast('Added', {
                      description: `${title.trim()} was added to the calendar.`,
                    })
                    resetForm()
                  },
                  onError: () =>
                    toast("Couldn't add that event", {
                      description: 'Please try again.',
                    }),
                },
              )
            }}
          >
            <label
              htmlFor="event-title"
              className="block text-lg font-semibold"
            >
              {getString(language, 'calendar_add_title_label')}
            </label>
            <input
              id="event-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-2 min-h-14 w-full rounded-2xl border border-border bg-background px-4 text-lg outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="event-date"
                  className="block text-lg font-semibold"
                >
                  {getString(language, 'calendar_add_day_label')}
                </label>
                <input
                  id="event-date"
                  type="date"
                  value={date}
                  onChange={(event) => setDate(event.target.value)}
                  className="mt-2 min-h-14 w-full rounded-2xl border border-border bg-background px-4 text-lg outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <div>
                <label
                  htmlFor="event-time"
                  className="block text-lg font-semibold"
                >
                  {getString(language, 'calendar_add_time_label')}
                </label>
                <input
                  id="event-time"
                  type="time"
                  value={time}
                  onChange={(event) => setTime(event.target.value)}
                  className="mt-2 min-h-14 w-full rounded-2xl border border-border bg-background px-4 text-lg outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>
            <label
              htmlFor="event-notes"
              className="mt-4 block text-lg font-semibold"
            >
              {getString(language, 'calendar_add_with_whom_label')}
            </label>
            <input
              id="event-notes"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              className="mt-2 min-h-14 w-full rounded-2xl border border-border bg-background px-4 text-lg outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="mt-5 flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={
                  !title.trim() || !date || !time || addEvent.isPending
                }
                className="inline-flex min-h-14 items-center rounded-2xl bg-primary px-6 text-lg font-semibold text-primary-foreground shadow-soft transition-transform hover:scale-[1.02] disabled:opacity-50"
              >
                {getString(language, 'calendar_add_save_button')}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="inline-flex min-h-14 items-center rounded-2xl border-2 border-border bg-card px-6 text-lg font-semibold transition-colors hover:bg-secondary"
              >
                {getString(language, 'calendar_add_cancel_button')}
              </button>
            </div>
          </form>
        ) : (
          <button
            type="button"
            onClick={() => setIsAdding(true)}
            className="flex min-h-16 items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-border bg-card/60 text-lg font-semibold text-muted-foreground transition-colors hover:bg-secondary/60"
          >
            <CalendarPlus className="size-5" aria-hidden="true" />
            {getString(language, 'calendar_add_button')}
          </button>
        )}
      </div>
    </ElderShell>
  )
}
