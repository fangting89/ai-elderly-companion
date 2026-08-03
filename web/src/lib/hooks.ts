import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  acceptFamilyNudge,
  addMedication,
  deletePhoto,
  getCheckInOpener,
  getDemoProfile,
  getLatestFamilyNote,
  getMedications,
  getPhotos,
  getTodaysDoses,
  markDoseTaken,
  pointAndAsk,
  sendCheckInReply,
  sendFamilyNote,
  setLanguage,
  uploadPhoto,
} from '@/lib/api'

export function useDemoProfile() {
  return useQuery({
    queryKey: ['demo-profile'],
    queryFn: getDemoProfile,
    staleTime: Infinity,
  })
}

export function usePhotos(elderId: string | undefined) {
  return useQuery({
    queryKey: ['photos', elderId],
    queryFn: () => getPhotos(elderId!),
    enabled: Boolean(elderId),
  })
}

export function useUploadPhoto(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: uploadPhoto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['photos', elderId] })
    },
  })
}

export function useLatestFamilyNote(elderId: string | undefined) {
  return useQuery({
    queryKey: ['family-note', elderId],
    queryFn: () => getLatestFamilyNote(elderId!),
    enabled: Boolean(elderId),
    // Refetch on window focus (default) so the elder's Home screen picks up
    // a new note without a manual reload after family sends one.
  })
}

export function useSendFamilyNote(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: sendFamilyNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['family-note', elderId] })
    },
  })
}

export function useSetLanguage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: setLanguage,
    onSuccess: () => {
      // demo-profile has staleTime: Infinity, so this needs an explicit
      // invalidate for the language change to actually propagate.
      queryClient.invalidateQueries({ queryKey: ['demo-profile'] })
    },
  })
}

export function usePointAndAsk() {
  return useMutation({ mutationFn: pointAndAsk })
}

export function useMedications(elderId: string | undefined) {
  return useQuery({
    queryKey: ['medications', elderId],
    queryFn: () => getMedications(elderId!),
    enabled: Boolean(elderId),
  })
}

export function useAddMedication(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: addMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', elderId] })
      queryClient.invalidateQueries({ queryKey: ['todays-doses', elderId] })
    },
  })
}

export function useTodaysDoses(elderId: string | undefined) {
  return useQuery({
    queryKey: ['todays-doses', elderId],
    queryFn: () => getTodaysDoses(elderId!),
    enabled: Boolean(elderId),
  })
}

export function useMarkDoseTaken(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: markDoseTaken,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todays-doses', elderId] })
    },
  })
}

export function useCheckInOpener(elderId: string | undefined) {
  return useQuery({
    queryKey: ['check-in-opener', elderId],
    queryFn: () => getCheckInOpener(elderId!),
    enabled: Boolean(elderId),
  })
}

export function useSendCheckInReply() {
  return useMutation({ mutationFn: sendCheckInReply })
}

export function useAcceptFamilyNudge(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: acceptFamilyNudge,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['check-in-opener', elderId] })
    },
  })
}

export function useDeletePhoto(elderId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deletePhoto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['photos', elderId] })
    },
  })
}
