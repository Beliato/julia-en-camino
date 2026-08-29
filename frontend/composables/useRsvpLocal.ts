/** Recuerda que este navegador ya respondió la invitación.
 *
 * Igual que con las reservas, quien entra no tiene cuenta: lo único que
 * evita que conteste dos veces sin darse cuenta es acordarse acá. No es
 * un control de verdad —basta con otro teléfono— y no pretende serlo:
 * el admin puede borrar duplicados.
 */

const STORAGE_KEY = 'julia_rsvp'

export interface RsvpLocal {
  nombre: string
  asistira: boolean
}

function leer(): RsvpLocal | null {
  if (!import.meta.client) return null
  try {
    const crudo = localStorage.getItem(STORAGE_KEY)
    return crudo ? (JSON.parse(crudo) as RsvpLocal) : null
  } catch {
    return null
  }
}

export function useRsvpLocal() {
  const respuesta = useState<RsvpLocal | null>('rsvp-local', () => null)

  function cargar() {
    respuesta.value = leer()
  }

  function guardar(valor: RsvpLocal) {
    respuesta.value = valor
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(valor))
    }
  }

  function olvidar() {
    respuesta.value = null
    if (import.meta.client) localStorage.removeItem(STORAGE_KEY)
  }

  return { respuesta, cargar, guardar, olvidar }
}
