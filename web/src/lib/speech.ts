import { useCallback, useEffect, useRef, useState } from 'react'
import type { Language } from '@/lib/api'

// Browser-native Web Speech APIs -- no server round-trip, no new dependency.
// Voice availability and quality vary by browser/OS, so every consumer of
// these hooks must feature-detect and simply not render its button rather
// than error when unsupported (older Safari, most of Firefox).
const SPEECH_LANG: Record<Language, string> = {
  English: 'en-SG',
  'Mandarin Chinese': 'zh-CN',
  Malay: 'ms-MY',
  Tamil: 'ta-IN',
}

export function useSpeechSynthesis() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window

  const speak = useCallback(
    (text: string, language: Language) => {
      if (!isSupported) return
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = SPEECH_LANG[language]
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    },
    [isSupported],
  )

  const stop = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }, [isSupported])

  useEffect(() => stop, [stop])

  return { speak, stop, isSpeaking, isSupported }
}

// Minimal shape of the non-standard SpeechRecognition API this app uses --
// TypeScript's DOM lib doesn't ship types for it since it's still
// vendor-prefixed in most browsers.
type SpeechRecognitionLike = {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: (() => void) | null
  onend: (() => void) | null
}
type SpeechRecognitionEventLike = {
  results: ArrayLike<ArrayLike<{ transcript: string }>>
}

function getSpeechRecognitionConstructor():
  (new () => SpeechRecognitionLike) | undefined {
  if (typeof window === 'undefined') return undefined
  const w = window as unknown as Record<string, unknown>
  return (w.SpeechRecognition ?? w.webkitSpeechRecognition) as
    (new () => SpeechRecognitionLike) | undefined
}

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const isSupported = getSpeechRecognitionConstructor() !== undefined

  const start = useCallback(
    (language: Language, onResult: (text: string) => void) => {
      const Ctor = getSpeechRecognitionConstructor()
      if (!Ctor) return
      const recognition = new Ctor()
      recognition.lang = SPEECH_LANG[language]
      recognition.continuous = false
      recognition.interimResults = false
      recognition.onresult = (event) => {
        if (event.results.length === 0 || event.results[0].length === 0) return
        onResult(event.results[0][0].transcript)
      }
      recognition.onerror = () => setIsListening(false)
      recognition.onend = () => setIsListening(false)
      recognitionRef.current = recognition
      setIsListening(true)
      recognition.start()
    },
    [],
  )

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  useEffect(() => stop, [stop])

  return { start, stop, isListening, isSupported }
}
