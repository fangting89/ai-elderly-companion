import { createFileRoute } from '@tanstack/react-router'
import { useRef, useState } from 'react'
import {
  AlertTriangle,
  Camera,
  DollarSign,
  FileText,
  ImageUp,
  ShieldAlert,
} from 'lucide-react'
import { toast } from 'sonner'
import { ElderShell } from '@/components/ElderShell'
import { ReadAloudButton } from '@/components/ReadAloudButton'
import { useDemoProfile, usePointAndAsk } from '@/lib/hooks'
import type { Language, PointAndAskResult } from '@/lib/api'
import { getString } from '@/lib/strings'

export const Route = createFileRoute('/point-ask')({
  head: () => ({ meta: [{ title: 'Point & Ask: You Little Companion' }] }),
  component: PointAsk,
})

function ResultCard({
  result,
  language,
}: {
  result: PointAndAskResult
  language: Language
}) {
  if (result.classification === 'scam') {
    return (
      <section className="rounded-3xl border-2 border-destructive bg-destructive/10 p-7 shadow-soft">
        <div className="flex items-start gap-3">
          <ShieldAlert
            className="mt-1 size-7 shrink-0 text-destructive"
            aria-hidden="true"
          />
          <div>
            <p className="font-display text-2xl font-semibold">
              {getString(language, 'scam_warning_title')}
            </p>
            <p className="mt-3 elder-body">
              {getString(language, 'scam_warning_body')}
            </p>
          </div>
        </div>
      </section>
    )
  }
  if (result.classification === 'unclear') {
    return (
      <section className="rounded-3xl border-2 border-caution bg-caution/30 p-7 shadow-soft">
        <p className="elder-body">
          {getString(language, 'blurry_photo_message')}
        </p>
      </section>
    )
  }
  const explanation = result.explanation ?? result.contentSummary
  return (
    <section className="rounded-3xl border-2 border-border bg-card p-7 shadow-soft">
      <p className="font-display text-2xl font-semibold">
        {getString(language, 'point_and_ask_result_title')}
      </p>
      <div className="mt-3 flex items-start gap-3">
        <p className="elder-body">{explanation}</p>
        <ReadAloudButton
          text={explanation}
          language={language}
          className="mt-1"
        />
      </div>
    </section>
  )
}

function PointAsk() {
  const { data: profile } = useDemoProfile()
  const language = profile?.preferredLanguage ?? 'English'
  const pointAndAsk = usePointAndAsk()
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const galleryInputRef = useRef<HTMLInputElement>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const categories = [
    {
      label: getString(language, 'point_and_ask_category_letter'),
      icon: FileText,
    },
    {
      label: getString(language, 'point_and_ask_category_bill'),
      icon: DollarSign,
    },
    {
      label: getString(language, 'point_and_ask_category_sms'),
      icon: ShieldAlert,
    },
  ]

  const handleFile = (file: File | undefined) => {
    if (!file) return
    if (!profile) {
      toast("Couldn't process that photo", {
        description: 'Please check your connection and try again.',
      })
      return
    }
    setPreviewUrl(URL.createObjectURL(file))
    pointAndAsk.mutate({ elderId: profile.elderId, file })
  }

  return (
    <ElderShell
      title={getString(language, 'nav_point_and_ask')}
      subtitle={getString(language, 'point_and_ask_intro')}
    >
      <div className="rounded-3xl border-2 border-dashed border-border bg-card p-10 text-center shadow-soft">
        <span className="mx-auto inline-flex size-24 items-center justify-center rounded-full bg-secondary text-primary">
          <Camera className="size-10" aria-hidden="true" />
        </span>
        <p className="mx-auto mt-6 max-w-md elder-body">
          {getString(language, 'point_and_ask_tips')}
        </p>

        <div className="mx-auto mt-6 grid max-w-md grid-cols-3 gap-3">
          {categories.map((category) => (
            <div
              key={category.label}
              className="flex flex-col items-center gap-2 rounded-2xl bg-secondary/60 p-4"
            >
              <category.icon
                className="size-6 text-primary"
                aria-hidden="true"
              />
              <span className="text-sm text-muted-foreground">
                {category.label}
              </span>
            </div>
          ))}
        </div>

        {previewUrl && (
          <img
            src={previewUrl}
            alt="What you photographed"
            className="mx-auto mt-6 max-h-64 rounded-2xl border border-border object-contain"
          />
        )}

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
          <input
            ref={galleryInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            disabled={pointAndAsk.isPending}
            className="inline-flex min-h-16 items-center gap-2 rounded-2xl bg-primary px-7 text-xl font-semibold text-primary-foreground shadow-soft transition-transform hover:scale-[1.02] disabled:opacity-50"
          >
            <Camera className="size-6" aria-hidden="true" />
            {getString(language, 'point_and_ask_camera_button')}
          </button>
          <button
            type="button"
            onClick={() => galleryInputRef.current?.click()}
            disabled={pointAndAsk.isPending}
            className="inline-flex min-h-16 items-center gap-2 rounded-2xl border-2 border-border bg-card px-7 text-xl font-semibold transition-colors hover:bg-secondary disabled:opacity-50"
          >
            <ImageUp className="size-6" aria-hidden="true" />
            {getString(language, 'point_and_ask_gallery_button')}
          </button>
        </div>

        {pointAndAsk.isPending && (
          <p className="mt-6 elder-body text-muted-foreground">
            {getString(language, 'point_and_ask_spinner')}
          </p>
        )}
        {pointAndAsk.isError && (
          <p className="mt-6 flex items-center justify-center gap-2 elder-body text-destructive">
            <AlertTriangle className="size-5 shrink-0" aria-hidden="true" />
            {getString(language, 'point_and_ask_error_message')}
          </p>
        )}
      </div>

      {pointAndAsk.data && (
        <div className="mt-6">
          <ResultCard result={pointAndAsk.data} language={language} />
        </div>
      )}

      <p className="mx-auto mt-8 max-w-xl text-center elder-body text-muted-foreground">
        {getString(language, 'point_and_ask_disclaimer')}
      </p>
    </ElderShell>
  )
}
