import { defineStore } from 'pinia'

export interface Rsvp {
  id: number
  invitacion_id: number
  nombre: string
  asistira: boolean
  comentario: string | null
  created_at: string
}

export const useRsvpsStore = defineStore('rsvps', {
  state: () => ({
    respuestas: [] as Rsvp[],
    asisten: 0,
    noAsisten: 0,
    cargando: false,
  }),
  actions: {
    async fetchAll() {
      const api = useApi()
      this.cargando = true
      try {
        const data = await api<{
          asisten: number
          no_asisten: number
          respuestas: Rsvp[]
        }>('/rsvps')
        this.respuestas = data.respuestas
        this.asisten = data.asisten
        this.noAsisten = data.no_asisten
      } finally {
        this.cargando = false
      }
    },
    async eliminar(id: number) {
      const api = useApi()
      await api(`/rsvps/${id}`, { method: 'DELETE' })
      const quitada = this.respuestas.find((r) => r.id === id)
      this.respuestas = this.respuestas.filter((r) => r.id !== id)
      if (quitada?.asistira) this.asisten -= 1
      else if (quitada) this.noAsisten -= 1
    },
  },
})
