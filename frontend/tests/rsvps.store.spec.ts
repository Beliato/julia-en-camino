import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { Rsvp } from '~/stores/rsvps'
import { useRsvpsStore } from '~/stores/rsvps'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
mockNuxtImport('useApi', () => () => apiMock)

function rsvp(over: Partial<Rsvp> = {}): Rsvp {
  return {
    id: 1,
    invitacion_id: 1,
    nombre: 'Ana',
    asistira: true,
    cantidad: null,
    comentario: null,
    created_at: '2026-09-01T12:00:00Z',
    ...over,
  }
}

describe('store rsvps', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.mockReset()
  })

  it('fetchAll guarda las respuestas y los totales', async () => {
    const store = useRsvpsStore()
    apiMock.mockResolvedValue({
      asisten: 2,
      no_asisten: 1,
      respuestas: [rsvp(), rsvp({ id: 2 }), rsvp({ id: 3, asistira: false })],
    })

    await store.fetchAll()

    expect(apiMock).toHaveBeenCalledWith('/rsvps')
    expect(store.asisten).toBe(2)
    expect(store.noAsisten).toBe(1)
    expect(store.respuestas).toHaveLength(3)
    expect(store.cargando).toBe(false)
  })

  it('cargando vuelve a false aunque falle', async () => {
    const store = useRsvpsStore()
    apiMock.mockRejectedValue(new Error('sin red'))

    await expect(store.fetchAll()).rejects.toThrow()
    expect(store.cargando).toBe(false)
  })

  it('eliminar una que asiste baja ese contador', async () => {
    const store = useRsvpsStore()
    store.respuestas = [rsvp({ id: 1 }), rsvp({ id: 2 })]
    store.asisten = 2
    apiMock.mockResolvedValue(undefined)

    await store.eliminar(1)

    expect(apiMock).toHaveBeenCalledWith('/rsvps/1', { method: 'DELETE' })
    expect(store.respuestas.map((r) => r.id)).toEqual([2])
    expect(store.asisten).toBe(1)
  })

  it('eliminar una que no asiste baja el otro contador', async () => {
    const store = useRsvpsStore()
    store.respuestas = [rsvp({ id: 1, asistira: false })]
    store.asisten = 0
    store.noAsisten = 1
    apiMock.mockResolvedValue(undefined)

    await store.eliminar(1)

    expect(store.noAsisten).toBe(0)
    expect(store.asisten).toBe(0)
  })

  it('eliminar algo que no esta en el listado no toca los contadores', async () => {
    const store = useRsvpsStore()
    store.respuestas = [rsvp({ id: 1 })]
    store.asisten = 1
    apiMock.mockResolvedValue(undefined)

    await store.eliminar(99)

    expect(store.asisten).toBe(1)
    expect(store.respuestas).toHaveLength(1)
  })
})
