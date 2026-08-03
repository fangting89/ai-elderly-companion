import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'

export type CalendarEvent = {
  id: string
  title: string
  day: string
  time: string
  withWhom?: string
}

export type MemoryItem = {
  id: string
  title: string
  note: string
  addedBy: string
}

// Medication, Chat, and the elder's preferred language all now use real API
// data (see @/lib/hooks) -- this store only holds what's still mock:
// Calendar and Memory Bank facts.
const initialEvents: CalendarEvent[] = [
  {
    id: 'e1',
    title: 'Lunch with Wei Ling',
    day: 'Sunday',
    time: '12:30 PM',
    withWhom: 'Your daughter',
  },
  {
    id: 'e2',
    title: 'Polyclinic check-up',
    day: 'Tuesday',
    time: '10:00 AM',
    withWhom: 'Bukit Merah Polyclinic',
  },
  {
    id: 'e3',
    title: 'Morning qigong at the pavilion',
    day: 'Wednesday',
    time: '7:30 AM',
    withWhom: 'Neighbours',
  },
]

const initialMemories: MemoryItem[] = [
  {
    id: 'b1',
    title: 'Grew up in Chinatown',
    note: 'Lived above a provision shop on Sago Lane until she was 19. Loves talking about the old street food stalls.',
    addedBy: 'Wei Ling',
  },
  {
    id: 'b2',
    title: 'Late husband — Ah Seng',
    note: 'Married 47 years. He was a bus captain. She likes remembering him, but prefers gentle mentions, not questions.',
    addedBy: 'Wei Ling',
  },
  {
    id: 'b3',
    title: 'Favourite music',
    note: 'Teresa Teng, and old Hokkien opera recordings.',
    addedBy: 'Kok Wai',
  },
]

type Store = {
  events: CalendarEvent[]
  memories: MemoryItem[]
  addEvent: (event: Omit<CalendarEvent, 'id'>) => void
  addMemory: (memory: Omit<MemoryItem, 'id'>) => void
}

const CompanionContext = createContext<Store | null>(null)

export function CompanionProvider({ children }: { children: ReactNode }) {
  const [events, setEvents] = useState<CalendarEvent[]>(initialEvents)
  const [memories, setMemories] = useState<MemoryItem[]>(initialMemories)

  const addEvent = useCallback((event: Omit<CalendarEvent, 'id'>) => {
    setEvents((prev) => [...prev, { ...event, id: `e${Date.now()}` }])
  }, [])

  const addMemory = useCallback((memory: Omit<MemoryItem, 'id'>) => {
    setMemories((prev) => [{ ...memory, id: `b${Date.now()}` }, ...prev])
  }, [])

  const value = useMemo<Store>(
    () => ({ events, memories, addEvent, addMemory }),
    [events, memories, addEvent, addMemory],
  )

  return (
    <CompanionContext.Provider value={value}>
      {children}
    </CompanionContext.Provider>
  )
}

export function useCompanion() {
  const ctx = useContext(CompanionContext)
  if (!ctx)
    throw new Error('useCompanion must be used inside CompanionProvider')
  return ctx
}
