import { Volume2, VolumeX } from 'lucide-react'
import { useSpeechSynthesis } from '@/lib/speech'
import type { Language } from '@/lib/api'

export function ReadAloudButton({
  text,
  language,
  className = '',
}: {
  text: string
  language: Language
  className?: string
}) {
  const { speak, stop, isSpeaking, isSupported } = useSpeechSynthesis()
  if (!isSupported) return null

  return (
    <button
      type="button"
      onClick={() => (isSpeaking ? stop() : speak(text, language))}
      aria-label={isSpeaking ? 'Stop reading aloud' : 'Read aloud'}
      className={`inline-flex size-11 shrink-0 items-center justify-center rounded-full border-2 border-border bg-card text-foreground transition-colors hover:bg-secondary ${className}`}
    >
      {isSpeaking ? (
        <VolumeX className="size-5" aria-hidden="true" />
      ) : (
        <Volume2 className="size-5" aria-hidden="true" />
      )}
    </button>
  )
}
