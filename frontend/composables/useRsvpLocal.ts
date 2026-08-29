/** Recuerda la respuesta hecha desde este navegador, por invitación.
 *
 * Guarda además el `token_edicion` que devuelve la API: es la única
 * credencial para cambiar esa respuesta en vez de crear otra. Sin él,
 * cambiar de opinión dejaba viva la respuesta vieja y sumaba una nueva.
 *
 * Se guarda por invitación porque alguien puede estar invitado a más de
 * un evento y responder distinto en cada uno.
 */

const STORAGE_KEY = 'julia_rsvp'

export interface RsvpLocal {
  token: string
  nombre: string
  asistira: boolean
  comentario: string
}

type PorInvitacion = Record<string, RsvpLocal>

function leer(): PorInvitacion {
  if (!import.meta.client) return {}
  try {
    const crudo = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    // El formato original guardaba una sola respuesta suelta, sin token
    // ni invitación. No se puede saber a cuál pertenecía ni editarla, así
    // que se descarta: quien esté en ese caso vuelve a ver el formulario.
    if (crudo && typeof crudo === 'object' && 'nombre' in crudo) return {}
    return crudo as PorInvitacion
  } catch {
    return {}
  }
}

export function useRsvpLocal() {
  const respuestas = useState<PorInvitacion>('rsvp-local', () => ({}))

  function persistir(valor: PorInvitacion) {
    respuestas.value = valor
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(valor))
    }
  }

  function cargar() {
    respuestas.value = leer()
  }

  function guardar(invitacion: string, valor: RsvpLocal) {
    persistir({ ...respuestas.value, [invitacion]: valor })
  }

  function olvidar(invitacion: string) {
    persistir(
      Object.fromEntries(
        Object.entries(respuestas.value).filter(([k]) => k !== invitacion),
      ),
    )
  }

  return { respuestas, cargar, guardar, olvidar }
}
