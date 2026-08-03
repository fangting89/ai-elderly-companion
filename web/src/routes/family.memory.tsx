import { createFileRoute } from '@tanstack/react-router'
import { useRef, useState } from 'react'
import { ImagePlus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { FamilyShell } from '@/components/FamilyShell'
import { useCompanion } from '@/lib/companion-store'
import {
  useDemoProfile,
  useDeletePhoto,
  usePhotos,
  useUploadPhoto,
} from '@/lib/hooks'

export const Route = createFileRoute('/family/memory')({
  head: () => ({
    meta: [
      { title: 'Memory bank: You Little Companion' },
      {
        name: 'description',
        content:
          'Add the facts, people and photos that matter, so the companion can talk about her life accurately.',
      },
    ],
  }),
  component: MemoryBank,
})

function MemoryBank() {
  const { memories, addMemory } = useCompanion()
  const { data: profile } = useDemoProfile()
  const { data: photos } = usePhotos(profile?.elderId)
  const uploadPhoto = useUploadPhoto(profile?.elderId)
  const deletePhoto = useDeletePhoto(profile?.elderId)
  const [title, setTitle] = useState('')
  const [note, setNote] = useState('')
  const [pendingFile, setPendingFile] = useState<File | null>(null)
  const [photoCaption, setPhotoCaption] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDeletePhoto = (id: string) => {
    if (!window.confirm('Delete this photo? This cannot be undone.')) return
    deletePhoto.mutate(id, {
      onSuccess: () => toast('Photo removed'),
      onError: () =>
        toast("Couldn't delete that photo", {
          description: 'Please try again.',
        }),
    })
  }

  const uploadSelectedPhoto = () => {
    if (!profile || !pendingFile || !photoCaption.trim()) return
    uploadPhoto.mutate(
      {
        elderId: profile.elderId,
        addedBy: profile.familyId,
        caption: photoCaption.trim(),
        file: pendingFile,
      },
      {
        onSuccess: () => {
          toast('Added to the photo deck', {
            description: "It'll show up in Ma's rotating home-screen photos.",
          })
          setPendingFile(null)
          setPhotoCaption('')
          if (fileInputRef.current) fileInputRef.current.value = ''
        },
        onError: () => {
          toast("Couldn't upload that photo", {
            description: 'Please try again.',
          })
        },
      },
    )
  }

  return (
    <FamilyShell
      title="Memory bank"
      intro="Everything the companion knows about Ma's life comes from this page. It only uses what you've written here: it never invents details, fills gaps, or guesses at names and dates."
    >
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <ul className="flex flex-col gap-3">
          {memories.map((memory) => (
            <li
              key={memory.id}
              className="rounded-2xl border border-border bg-card p-5 shadow-soft"
            >
              <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
                <p className="font-semibold">{memory.title}</p>
                <span className="shrink-0 rounded-full bg-secondary px-3 py-1 text-xs text-secondary-foreground">
                  {memory.addedBy}
                </span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {memory.note}
              </p>
            </li>
          ))}
        </ul>

        <div className="flex flex-col gap-4">
          <form
            className="h-fit rounded-2xl border border-border bg-card p-5 shadow-soft"
            onSubmit={(event) => {
              event.preventDefault()
              if (!title.trim()) return
              addMemory({
                title: title.trim(),
                note: note.trim() || 'No extra detail added.',
                addedBy: profile?.familyName ?? 'Wei Ling',
              })
              setTitle('')
              setNote('')
              toast('Added to the memory bank')
            }}
          >
            <p className="font-semibold">Add a memory</p>
            <label
              htmlFor="memory-title"
              className="mt-4 block text-sm font-medium"
            >
              What is it about?
            </label>
            <input
              id="memory-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Her grandson, Ryan"
              className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
            />
            <label
              htmlFor="memory-note"
              className="mt-4 block text-sm font-medium"
            >
              Details worth remembering
            </label>
            <textarea
              id="memory-note"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={4}
              placeholder="Turns 9 in September. Plays badminton. She calls him Xiao Bao."
              className="mt-2 w-full resize-none rounded-xl border border-border bg-background px-4 py-3 outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              type="submit"
              className="mt-4 inline-flex min-h-11 w-full items-center justify-center rounded-xl bg-primary font-semibold text-primary-foreground"
            >
              Save memory
            </button>
          </form>

          <div className="rounded-2xl border border-border bg-card p-5 shadow-soft">
            <p className="font-semibold">Add a photo</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Shows up in the rotating photo deck on Ma's home screen.
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={(event) =>
                setPendingFile(event.target.files?.[0] ?? null)
              }
              className="mt-4 block w-full text-sm text-muted-foreground file:mr-3 file:min-h-11 file:rounded-xl file:border file:border-dashed file:border-border file:bg-background file:px-4 file:text-sm file:font-medium"
            />
            {pendingFile ? (
              <>
                <label
                  htmlFor="photo-caption"
                  className="mt-4 block text-sm font-medium"
                >
                  Caption
                </label>
                <input
                  id="photo-caption"
                  value={photoCaption}
                  onChange={(event) => setPhotoCaption(event.target.value)}
                  placeholder="Lunch with Wei Ling, last Sunday"
                  className="mt-2 min-h-11 w-full rounded-xl border border-border bg-background px-4 outline-none focus:ring-2 focus:ring-ring"
                />
                <button
                  type="button"
                  onClick={uploadSelectedPhoto}
                  disabled={!photoCaption.trim() || uploadPhoto.isPending}
                  className="mt-3 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-primary font-semibold text-primary-foreground disabled:opacity-50"
                >
                  <ImagePlus className="size-4" aria-hidden="true" />
                  {uploadPhoto.isPending ? 'Uploading...' : 'Add to photo deck'}
                </button>
              </>
            ) : null}
          </div>

          {photos && photos.length > 0 ? (
            <div className="rounded-2xl border border-border bg-card p-5 shadow-soft">
              <p className="font-semibold">Photos you've added</p>
              <ul className="mt-4 grid grid-cols-3 gap-3">
                {photos.map((photo) => (
                  <li key={photo.id} className="group relative">
                    <img
                      src={photo.imageUrl}
                      alt={photo.caption}
                      className="aspect-square w-full rounded-xl object-cover"
                    />
                    <button
                      type="button"
                      onClick={() => handleDeletePhoto(photo.id)}
                      disabled={deletePhoto.isPending}
                      aria-label={`Delete photo: ${photo.caption}`}
                      className="absolute right-1.5 top-1.5 inline-flex size-8 items-center justify-center rounded-full bg-foreground/70 text-background opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100 disabled:opacity-50"
                    >
                      <Trash2 className="size-4" aria-hidden="true" />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </div>
    </FamilyShell>
  )
}
