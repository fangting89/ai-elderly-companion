import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useDemoProfile, usePhotos } from '@/lib/hooks'

export function PhotoDeck() {
  const { data: profile } = useDemoProfile()
  const { data: photos, isLoading } = usePhotos(profile?.elderId)
  const [index, setIndex] = useState(0)

  const count = photos?.length ?? 0

  useEffect(() => {
    if (count < 2) return
    const timer = window.setInterval(
      () => setIndex((i) => (i + 1) % count),
      6000,
    )
    return () => window.clearInterval(timer)
  }, [count])

  useEffect(() => {
    // Keep the current index in range if the deck shrinks/grows after a new upload.
    setIndex((i) => (count === 0 ? 0 : i % count))
  }, [count])

  if (isLoading) {
    return (
      <section className="flex aspect-[4/3] w-full items-center justify-center rounded-3xl border-2 border-border bg-card shadow-soft sm:aspect-[16/10]">
        <p className="text-muted-foreground">Loading photos...</p>
      </section>
    )
  }

  if (!photos || photos.length === 0) {
    return (
      <section className="flex aspect-[4/3] w-full flex-col items-center justify-center gap-2 rounded-3xl border-2 border-dashed border-border bg-card p-6 text-center shadow-soft sm:aspect-[16/10]">
        <p className="elder-body">No photos yet.</p>
        <p className="text-muted-foreground">
          Ask your family to add some from the Memory bank page.
        </p>
      </section>
    )
  }

  const go = (step: number) => setIndex((i) => (i + step + count) % count)

  return (
    <section
      className="overflow-hidden rounded-3xl border-2 border-border bg-card shadow-soft"
      aria-roledescription="carousel"
      aria-label="Photos from your family"
    >
      <div className="relative aspect-[4/3] w-full sm:aspect-[16/10]">
        {photos.map((photo, i) => (
          <img
            key={photo.id}
            src={photo.imageUrl}
            alt={photo.caption}
            loading={i === 0 ? 'eager' : 'lazy'}
            aria-hidden={i !== index}
            className={`absolute inset-0 size-full object-cover transition-all duration-1000 ease-out ${
              i === index ? 'scale-100 opacity-100' : 'scale-105 opacity-0'
            }`}
          />
        ))}

        <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-6 pt-16">
          <p
            key={index}
            className="animate-fade-in text-2xl font-semibold text-white"
          >
            {photos[index]?.caption}
          </p>
        </div>

        {count > 1 && (
          <>
            <button
              type="button"
              onClick={() => go(-1)}
              aria-label="Previous photo"
              className="absolute left-3 top-1/2 inline-flex size-16 -translate-y-1/2 items-center justify-center rounded-full bg-card/85 text-foreground shadow-soft backdrop-blur transition-transform hover:scale-105"
            >
              <ChevronLeft className="size-8" aria-hidden="true" />
            </button>
            <button
              type="button"
              onClick={() => go(1)}
              aria-label="Next photo"
              className="absolute right-3 top-1/2 inline-flex size-16 -translate-y-1/2 items-center justify-center rounded-full bg-card/85 text-foreground shadow-soft backdrop-blur transition-transform hover:scale-105"
            >
              <ChevronRight className="size-8" aria-hidden="true" />
            </button>
          </>
        )}
      </div>

      {count > 1 && (
        <div className="flex items-center justify-center gap-3 p-4">
          {photos.map((photo, i) => (
            <button
              key={photo.id}
              type="button"
              onClick={() => setIndex(i)}
              aria-label={`Show photo ${i + 1}`}
              aria-current={i === index}
              className={`h-3 rounded-full transition-all duration-300 ${
                i === index
                  ? 'w-10 bg-primary'
                  : 'w-3 bg-border hover:bg-muted-foreground'
              }`}
            />
          ))}
        </div>
      )}
    </section>
  )
}
