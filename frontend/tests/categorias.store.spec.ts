import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useCategoriasStore } from '~/stores/categorias'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
mockNuxtImport('useApi', () => () => apiMock)

describe('store categorias', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.mockReset()
  })

  it('fetchAll trae la lista', async () => {
    const store = useCategoriasStore()
    apiMock.mockResolvedValue([
      { id: 1, nombre: 'Ropa' },
      { id: 2, nombre: 'Higiene' },
    ])

    await store.fetchAll()

    expect(apiMock).toHaveBeenCalledWith('/categorias')
    expect(store.categorias).toHaveLength(2)
  })

  it('crear la agrega al listado', async () => {
    const store = useCategoriasStore()
    store.categorias = [{ id: 1, nombre: 'Ropa' }]
    apiMock.mockResolvedValue({ id: 2, nombre: 'Juguetes' })

    const creada = await store.crear('Juguetes')

    expect(apiMock).toHaveBeenCalledWith('/categorias', {
      method: 'POST',
      body: { nombre: 'Juguetes' },
    })
    expect(creada.id).toBe(2)
    expect(store.categorias).toHaveLength(2)
  })

  it('crear deja el listado ordenado alfabeticamente', async () => {
    // El selector las muestra en este orden, así que ordenar al crear
    // evita tener que volver a pedir la lista entera.
    const store = useCategoriasStore()
    store.categorias = [
      { id: 1, nombre: 'Ropa' },
      { id: 2, nombre: 'Higiene' },
    ]
    apiMock.mockResolvedValue({ id: 3, nombre: 'Juguetes' })

    await store.crear('Juguetes')

    expect(store.categorias.map((c) => c.nombre)).toEqual([
      'Higiene',
      'Juguetes',
      'Ropa',
    ])
  })
})
