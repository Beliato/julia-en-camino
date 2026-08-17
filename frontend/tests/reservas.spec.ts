import { beforeEach, describe, expect, it } from 'vitest'

import { useReservasLocales } from '~/composables/useReservasLocales'

describe('reservas locales del invitado', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('guarda el token y el nombre del objeto', () => {
    const { reservas, guardar } = useReservasLocales()
    guardar(7, 'token-abc', 'Cuna colecho')
    expect(reservas.value[7]).toEqual({
      token: 'token-abc',
      nombre: 'Cuna colecho',
    })
    expect(JSON.parse(localStorage.getItem('julia_reservas')!)).toEqual({
      7: { token: 'token-abc', nombre: 'Cuna colecho' },
    })
  })

  it('cargar recupera lo guardado en una visita anterior', () => {
    localStorage.setItem(
      'julia_reservas',
      JSON.stringify({ 3: { token: 'tok-3', nombre: 'Mecedora' } }),
    )
    const { reservas, cargar } = useReservasLocales()
    cargar()
    expect(reservas.value[3]!.nombre).toBe('Mecedora')
  })

  it('migra el formato viejo, que guardaba solo el token', () => {
    // La app ya estaba en uso: quien reservó antes tiene { id: "uuid" } y
    // no puede perder su reserva.
    localStorage.setItem('julia_reservas', JSON.stringify({ 5: 'tok-viejo' }))
    const { reservas, cargar } = useReservasLocales()
    cargar()
    expect(reservas.value[5]).toEqual({ token: 'tok-viejo', nombre: '' })
  })

  it('olvidar elimina solo esa reserva', () => {
    const { reservas, guardar, olvidar } = useReservasLocales()
    guardar(1, 'tok-1', 'Uno')
    guardar(2, 'tok-2', 'Dos')
    olvidar(1)
    expect(reservas.value[1]).toBeUndefined()
    expect(reservas.value[2]!.token).toBe('tok-2')
  })

  it('tolera localStorage corrupto sin romper', () => {
    localStorage.setItem('julia_reservas', 'no-es-json')
    const { reservas, cargar } = useReservasLocales()
    cargar()
    expect(reservas.value).toEqual({})
  })
})
