import { defineStore } from 'pinia'

const NOMBRE_DEFAULT = 'Julia en Camino'

interface ConfigApi {
  nombre_app: string
  evento_lugar: string | null
  evento_fecha: string | null
  evento_hora: string | null
  evento_texto: string | null
}

export const useConfigStore = defineStore('config', {
  state: () => ({
    nombreApp: NOMBRE_DEFAULT,
    eventoLugar: '' as string,
    eventoFecha: '' as string,
    eventoHora: '' as string,
    eventoTexto: '' as string,
    cargado: false,
  }),
  getters: {
    /** Si no se cargó ningún dato, la invitación no muestra el bloque. */
    hayDatosDelEvento: (state) =>
      !!(
        state.eventoLugar ||
        state.eventoFecha ||
        state.eventoHora ||
        state.eventoTexto
      ),
  },
  actions: {
    _aplicar(data: ConfigApi) {
      this.nombreApp = data.nombre_app
      this.eventoLugar = data.evento_lugar ?? ''
      this.eventoFecha = data.evento_fecha ?? ''
      this.eventoHora = data.evento_hora ?? ''
      this.eventoTexto = data.evento_texto ?? ''
    },
    async fetch() {
      if (this.cargado) return
      try {
        const config = useRuntimeConfig()
        const data = await $fetch<ConfigApi>('/config', {
          baseURL: config.public.apiBase,
        })
        this._aplicar(data)
        this.cargado = true
      } catch {
        // Sin backend disponible se mantiene el default — la UI no se rompe.
      }
    },
    /** Guarda desde Ajustes. Solo manda lo que se le pasa. */
    async guardar(cambios: Partial<ConfigApi>) {
      const api = useApi()
      const data = await api<ConfigApi>('/config', {
        method: 'PATCH',
        body: cambios,
      })
      this._aplicar(data)
      return data
    },
    setNombre(nombre: string) {
      this.nombreApp = nombre
    },
  },
})
