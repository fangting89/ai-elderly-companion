import { useState } from 'react'
import { toast } from 'sonner'
import {
  useAcceptFamilyNudge,
  useCheckInOpener,
  useDemoProfile,
  useSendCheckInReply,
} from '@/lib/hooks'
import { getString } from '@/lib/strings'
import { ReadAloudButton } from '@/components/ReadAloudButton'
import { MicButton } from '@/components/MicButton'

// Embedded directly on Home so the elder is naturally prompted to reply,
// rather than needing to click into a separate page. Still deliberately not
// a persistent chat thread: normally one opener, one reply, done for the
// day -- the backend unlocks exactly one more reply box (see canContinue)
// when the first reply reads as low mood/distress, so the companion never
// asks "want to tell me more?" with nowhere left to answer.
export function CheckInPrompt() {
  const { data: profile, isError: profileError } = useDemoProfile()
  const language = profile?.preferredLanguage ?? 'English'
  const {
    data: opener,
    isLoading: openerLoading,
    isError: openerError,
  } = useCheckInOpener(profile?.elderId)
  const sendReply = useSendCheckInReply()
  const acceptFamilyNudge = useAcceptFamilyNudge(profile?.elderId)
  const [text, setText] = useState('')
  const [replies, setReplies] = useState<string[]>([])
  const [canContinue, setCanContinue] = useState(false)

  const showFamilyNudgeButton =
    opener?.lineType === 'family_nudge' && !opener.familyNudgeAccepted
  const showReplyForm = replies.length === 0 || canContinue

  const submitReply = (event: React.FormEvent) => {
    event.preventDefault()
    if (!text.trim()) return
    if (!profile) {
      toast("Couldn't send that", {
        description: 'Please check your connection and try again.',
      })
      return
    }
    sendReply.mutate(
      { elderId: profile.elderId, text: text.trim() },
      {
        onSuccess: (data) => {
          setReplies((prev) => [...prev, data.reply])
          setCanContinue(data.canContinue)
          setText('')
        },
        onError: () =>
          toast("Couldn't send that", {
            description: 'Please check your connection and try again.',
          }),
      },
    )
  }

  return (
    <section className="mt-8 rounded-3xl border-2 border-border bg-companion p-7 text-companion-foreground shadow-soft">
      {profileError || openerError ? (
        <p className="elder-body">
          Sorry, I couldn't connect just now. Please check with your family, or
          try again in a moment.
        </p>
      ) : !profile || openerLoading ? (
        <p className="elder-body">...</p>
      ) : opener === null ? (
        <p className="elder-body">
          {getString(language, 'check_in_nothing_more_today')}
        </p>
      ) : (
        <>
          <div className="flex items-start gap-3">
            <p className="elder-body">{opener!.text}</p>
            <ReadAloudButton
              text={opener!.text}
              language={language}
              className="mt-1"
            />
          </div>
          {showFamilyNudgeButton ? (
            <button
              type="button"
              onClick={() =>
                acceptFamilyNudge.mutate(profile.elderId, {
                  onError: () =>
                    toast("Couldn't save that", {
                      description: 'Please try again in a moment.',
                    }),
                })
              }
              disabled={acceptFamilyNudge.isPending}
              className="mt-4 inline-flex min-h-12 items-center rounded-2xl border-2 border-companion-foreground/30 bg-transparent px-5 text-lg font-semibold transition-colors hover:bg-companion-foreground/10 disabled:opacity-50"
            >
              {getString(language, 'check_in_family_nudge_accept_button')}
            </button>
          ) : opener!.lineType === 'family_nudge' ? (
            <p className="mt-3 text-sm text-companion-foreground/80">
              {getString(language, 'check_in_family_nudge_accepted_label')}
            </p>
          ) : null}
        </>
      )}

      {replies.map((reply, index) => (
        <div
          key={index}
          className="mt-4 flex items-start gap-3 border-t border-companion-foreground/20 pt-4"
        >
          <p className="elder-body">{reply}</p>
          <ReadAloudButton text={reply} language={language} className="mt-1" />
        </div>
      ))}

      {showReplyForm ? (
        <>
          {replies.length > 0 ? (
            <p className="mt-4 elder-body">
              {getString(language, 'check_in_extend_prompt')}
            </p>
          ) : null}
          <form className="mt-4" onSubmit={submitReply}>
            <div className="flex items-start gap-3">
              <textarea
                value={text}
                onChange={(event) => setText(event.target.value)}
                rows={2}
                placeholder={getString(language, 'check_in_placeholder')}
                className="w-full resize-none rounded-2xl border border-border bg-background px-4 py-3 text-foreground elder-body outline-none focus:ring-2 focus:ring-ring"
              />
              <MicButton
                language={language}
                onResult={(spoken) =>
                  setText((current) =>
                    current ? `${current} ${spoken}` : spoken,
                  )
                }
              />
            </div>
            <div className="mt-3 flex justify-end">
              <button
                type="submit"
                disabled={sendReply.isPending || !text.trim()}
                className="inline-flex min-h-14 items-center gap-2 rounded-2xl bg-primary px-6 text-lg font-semibold text-primary-foreground shadow-soft transition-transform hover:scale-[1.02] disabled:opacity-50"
              >
                {sendReply.isPending
                  ? getString(language, 'check_in_sending')
                  : getString(language, 'check_in_send_button')}
              </button>
            </div>
          </form>
        </>
      ) : null}
    </section>
  )
}
