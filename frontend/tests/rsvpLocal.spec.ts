import { beforeEach, describe, expect, it } from 'vitest'

import { useRsvpLocal } from '~/composables/useRsvpLocal'

const INV_A = 'token-invitacion-a'
const INV_B = 'token-invitacion-b'

function respuesta(over = {}) {
  return {
    token: 'token-edicion-1',
    nombre: 'Hannia Solano',
    asistira: true,
    cantidad: '',
    comentario: '',
    ...over,
  }
}

describe('respuesta local del invitado', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('guarda la respuesta bajo su invitacion', () => {
    const { respuestas, guardar } = useRsvpLocal()
    guardar(INV_A, respuesta())

    expect(respuestas.value[INV_A]!.nombre).toBe('Hannia Solano')
    expect(JSON.parse(localStorage.getItem('julia_rsvp')!)[INV_A].token).toBe(
      'token-edicion-1',
    )
  })

  it('cada invitacion guarda su propia respuesta', () => {
    // Alguien puede estar invitado a dos eventos y contestar distinto.
    const { respuestas, guardar } = useRsvpLocal()
    guardar(INV_A, respuesta({ asistira: true }))
    guardar(INV_B, respuesta({ token: 'otro', asistira: false }))

    expect(respuestas.value[INV_A]!.asistira).toBe(true)
    expect(respuestas.value[INV_B]!.asistira).toBe(false)
  })

  it('cargar recupera lo guardado en una visita anterior', () => {
    localStorage.setItem(
      'julia_rsvp',
      JSON.stringify({ [INV_A]: respuesta({ nombre: 'Ana' }) }),
    )
    const { respuestas, cargar } = useRsvpLocal()
    cargar()

    expect(respuestas.value[INV_A]!.nombre).toBe('Ana')
  })

  it('olvidar borra solo esa invitacion', () => {
    const { respuestas, guardar, olvidar } = useRsvpLocal()
    guardar(INV_A, respuesta())
    guardar(INV_B, respuesta({ token: 'otro' }))
    olvidar(INV_A)

    expect(respuestas.value[INV_A]).toBeUndefined()
    expect(respuestas.value[INV_B]).toBeDefined()
  })

  it('descarta el formato viejo, que no tenia token ni invitacion', () => {
    // Sin token no hay forma de saber que respuesta editaria, y sin
    // invitacion tampoco a cual pertenecia: se vuelve al formulario.
    localStorage.setItem(
      'julia_rsvp',
      JSON.stringify({ nombre: 'Ana', asistira: true }),
    )
    const { respuestas, cargar } = useRsvpLocal()
    cargar()

    expect(respuestas.value).toEqual({})
  })

  it('tolera localStorage corrupto sin romper', () => {
    localStorage.setItem('julia_rsvp', 'no-es-json')
    const { respuestas, cargar } = useRsvpLocal()
    cargar()

    expect(respuestas.value).toEqual({})
  })

  it('guardar de nuevo pisa la respuesta anterior de esa invitacion', () => {
    const { respuestas, guardar } = useRsvpLocal()
    guardar(INV_A, respuesta({ nombre: 'Ana' }))
    guardar(INV_A, respuesta({ nombre: 'Ana Perez' }))

    expect(Object.keys(respuestas.value)).toHaveLength(1)
    expect(respuestas.value[INV_A]!.nombre).toBe('Ana Perez')
  })
})
