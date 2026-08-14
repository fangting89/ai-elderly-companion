const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export type Language = 'English' | 'Mandarin Chinese' | 'Malay' | 'Tamil'

export type DemoProfile = {
  elderId: string
  elderName: string
  familyId: string
  familyName: string
  preferredLanguage: Language
}

export type Photo = {
  id: string
  imageUrl: string
  caption: string
}

export type Medication = {
  id: string
  name: string
  dosage: string
  timesPerDay: string[]
}

export type Dose = {
  logId: string
  medicationName: string
  dosage: string
  scheduledFor: string
  status: 'pending' | 'taken' | 'missed'
}

export type PointAndAskResult = {
  classification: 'explain' | 'scam' | 'unclear'
  riskLevel: 'low' | 'medium' | 'high'
  explanation: string | null
  contentSummary: string
}

export type FamilyNote = {
  id: string
  senderName: string
  relation: string | null
  text: string
  createdAt: string
}

async function toJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text()
    throw new Error(`${response.status} ${response.statusText}: ${body}`)
  }
  return response.json() as Promise<T>
}

export async function getDemoProfile(): Promise<DemoProfile> {
  const response = await fetch(`${API_BASE_URL}/api/demo-profile`)
  return toJson<DemoProfile>(response)
}

export async function getPhotos(elderId: string): Promise<Photo[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/photos?${new URLSearchParams({ elder_id: elderId })}`,
  )
  const photos =
    await toJson<{ id: string; image_url: string; caption: string }[]>(response)
  return photos.map((p) => ({
    id: p.id,
    imageUrl: `${API_BASE_URL}${p.image_url}`,
    caption: p.caption,
  }))
}

export async function uploadPhoto(params: {
  elderId: string
  addedBy: string
  caption: string
  file: File
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('added_by', params.addedBy)
  body.set('caption', params.caption)
  body.set('file', params.file)
  const response = await fetch(`${API_BASE_URL}/api/photos`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}

export async function getLatestFamilyNote(
  elderId: string,
): Promise<FamilyNote | null> {
  const response = await fetch(
    `${API_BASE_URL}/api/family-notes/latest?${new URLSearchParams({ elder_id: elderId })}`,
  )
  const note = await toJson<{
    id: string
    senderName: string
    relation: string | null
    text: string
    createdAt: string
  } | null>(response)
  return note
}

export async function sendFamilyNote(params: {
  elderId: string
  senderName: string
  relation: string
  text: string
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('sender_name', params.senderName)
  body.set('relation', params.relation)
  body.set('text', params.text)
  const response = await fetch(`${API_BASE_URL}/api/family-notes`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}

export async function setLanguage(params: {
  elderId: string
  language: Language
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('language', params.language)
  const response = await fetch(`${API_BASE_URL}/api/profile/language`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}

export async function pointAndAsk(params: {
  elderId: string
  file: File
}): Promise<PointAndAskResult> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('file', params.file)
  const response = await fetch(`${API_BASE_URL}/api/point-and-ask`, {
    method: 'POST',
    body,
  })
  return toJson<PointAndAskResult>(response)
}

export async function getMedications(elderId: string): Promise<Medication[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/medications?${new URLSearchParams({ elder_id: elderId })}`,
  )
  return toJson<Medication[]>(response)
}

export async function addMedication(params: {
  elderId: string
  name: string
  dosage: string
  timesPerDay: string
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('name', params.name)
  body.set('dosage', params.dosage)
  body.set('times_per_day', params.timesPerDay)
  const response = await fetch(`${API_BASE_URL}/api/medications`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}

export async function getTodaysDoses(elderId: string): Promise<Dose[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/medications/today?${new URLSearchParams({ elder_id: elderId })}`,
  )
  return toJson<Dose[]>(response)
}

export async function markDoseTaken(logId: string): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/medications/${logId}/taken`,
    {
      method: 'POST',
    },
  )
  await toJson<{ status: string }>(response)
}

export type CheckInOpener = {
  text: string
  lineType: 'family_nudge' | 'reminiscence' | 'daily_checkin'
  familyNudgeAccepted: boolean
}

export async function getCheckInOpener(
  elderId: string,
): Promise<CheckInOpener | null> {
  const response = await fetch(
    `${API_BASE_URL}/api/check-in/opener?${new URLSearchParams({ elder_id: elderId })}`,
  )
  return toJson<CheckInOpener | null>(response)
}

export type CheckInReply = { reply: string; canContinue: boolean }

export async function sendCheckInReply(params: {
  elderId: string
  text: string
}): Promise<CheckInReply> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('text', params.text)
  const response = await fetch(`${API_BASE_URL}/api/check-in`, {
    method: 'POST',
    body,
  })
  return toJson<CheckInReply>(response)
}

export async function acceptFamilyNudge(elderId: string): Promise<void> {
  const body = new FormData()
  body.set('elder_id', elderId)
  const response = await fetch(
    `${API_BASE_URL}/api/check-in/family-nudge-accepted`,
    {
      method: 'POST',
      body,
    },
  )
  await toJson<{ status: string }>(response)
}

export async function deletePhoto(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/photos/${id}`, {
    method: 'DELETE',
  })
  await toJson<{ status: string }>(response)
}

export type Activity = {
  icon: string
  title: string
  schedule: string
}

export async function getActivities(): Promise<Activity[]> {
  const response = await fetch(`${API_BASE_URL}/api/activities`)
  return toJson<Activity[]>(response)
}

export type CalendarEvent = {
  id: string
  title: string
  eventType: 'appointment' | 'medication' | 'other'
  startTime: string
  notes: string | null
}

export async function getCalendarEvents(
  elderId: string,
): Promise<CalendarEvent[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/calendar?${new URLSearchParams({ elder_id: elderId })}`,
  )
  return toJson<CalendarEvent[]>(response)
}

export async function addCalendarEvent(params: {
  elderId: string
  title: string
  startTime: string
  notes: string
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('title', params.title)
  body.set('start_time', params.startTime)
  body.set('notes', params.notes)
  const response = await fetch(`${API_BASE_URL}/api/calendar`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}

export type MemoryFact = {
  id: string
  text: string
  addedByName: string
}

export async function getMemoryFacts(elderId: string): Promise<MemoryFact[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/memory-bank/facts?${new URLSearchParams({ elder_id: elderId })}`,
  )
  return toJson<MemoryFact[]>(response)
}

export async function addMemoryFact(params: {
  elderId: string
  addedBy: string
  text: string
}): Promise<void> {
  const body = new FormData()
  body.set('elder_id', params.elderId)
  body.set('added_by', params.addedBy)
  body.set('text', params.text)
  const response = await fetch(`${API_BASE_URL}/api/memory-bank/facts`, {
    method: 'POST',
    body,
  })
  await toJson<{ status: string }>(response)
}
