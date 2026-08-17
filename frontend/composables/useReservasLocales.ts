/** Reservas hechas desde este navegador.
 *
 * Como los invitados no tienen cuenta, el `token_deshacer` que devuelve la
 * API al reservar es la única credencial para liberar esa reserva. Se guarda
 * en localStorage junto al nombre del objeto, para poder mostrarle a la
 * persona qué fue lo que apartó.
 */

const STORAGE_KEY = 'julia_reservas'

export interface ReservaLocal {
  token: string
  nombre: string
}

type ReservasLocales = Record<number, ReservaLocal>

function leer(): ReservasLocales {
  if (!import.meta.client) return {}
  try {
    const crudo = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    // El formato original guardaba solo el token: { [itemId]: "uuid" }.
    // Se migra al leer para no romperle la reserva a quien ya la hizo.
    return Object.fromEntries(
      Object.entries(crudo).map(([id, valor]) => [
        id,
        typeof valor === 'string' ? { token: valor, nombre: '' } : valor,
      ]),
    ) as ReservasLocales
  } catch {
    return {}
  }
}

export function useReservasLocales() {
  const reservas = useState<ReservasLocales>('reservas-locales', () => ({}))

  function persistir(valor: ReservasLocales) {
    reservas.value = valor
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(valor))
    }
  }

  function cargar() {
    reservas.value = leer()
  }

  function guardar(itemId: number, token: string, nombre: string) {
    persistir({ ...reservas.value, [itemId]: { token, nombre } })
  }

  function olvidar(itemId: number) {
    persistir(
      Object.fromEntries(
        Object.entries(reservas.value).filter(([id]) => Number(id) !== itemId),
      ),
    )
  }

  return { reservas, cargar, guardar, olvidar }
}
