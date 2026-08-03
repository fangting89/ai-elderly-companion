import { Mic, MicOff } from 'lucide-react'
import { toast } from 'sonner'
import { useSpeechRecognition } from '@/lib/speech'
import type { Language } from '@/lib/api'

export function MicButton({
  language,
  onResult,
  className = '',
}: {
  language: Language
  onResult: (text: string) => void
  className?: string
}) {
  const { start, stop, isListening, isSupported } = useSpeechRecognition()

  if (!isSupported) {
    return (
      <button
        type="button"
        onClick={() =>
          toast("Voice input isn't available in this browser", {
            description: 'Please type your reply instead.',
          })
        }
        aria-label="Voice input unavailable"
        className={`inline-flex size-11 shrink-0 items-center justify-center rounded-full border-2 border-border bg-card text-muted-foreground ${className}`}
      >
        <MicOff className="size-5" aria-hidden="true" />
      </button>
    )
  }

  return (
    <button
      type="button"
      onClick={() => (isListening ? stop() : start(language, onResult))}
      aria-label={isListening ? 'Stop voice input' : 'Speak instead of typing'}
      className={`inline-flex size-11 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
        isListening
          ? 'border-primary bg-primary text-primary-foreground'
          : 'border-border bg-card text-foreground hover:bg-secondary'
      } ${className}`}
    >
      <Mic className="size-5" aria-hidden="true" />
    </button>
  )
}
