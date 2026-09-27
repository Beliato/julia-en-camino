import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { usePreviewDelLink } from '~/composables/usePreviewDelLink'

const { headMock } = vi.hoisted(() => ({ headMock: vi.fn() }))
mockNuxtImport('useHead', () => headMock)

/** Devuelve el content de una etiqueta del último useHead(). */
function meta(clave: string): string | undefined {
  const etiquetas = headMock.mock.calls.at(-1)?.[0]?.meta ?? []
  return etiquetas.find(
    (m: Record<string, string>) => m.name === clave || m.property === clave,
  )?.content
}

describe('preview del link compartido', () => {
  beforeEach(() => headMock.mockReset())

  it('la descripción va en las tres etiquetas que leen los lectores', () => {
    // WhatsApp usa og:, Twitter las suyas, y description es el piso.
    usePreviewDelLink({ descripcion: 'Acá van algunas ideas' })

    expect(meta('description')).toBe('Acá van algunas ideas')
    expect(meta('og:description')).toBe('Acá van algunas ideas')
    expect(meta('twitter:description')).toBe('Acá van algunas ideas')
  })

  it('sin título no se pisa el del sitio', () => {
    // Cada página decide si cambia el título; la que no lo pasa se queda
    // con el de nuxt.config, y para eso no tiene que emitir la etiqueta.
    usePreviewDelLink({ descripcion: 'Solo la descripción' })

    expect(meta('og:title')).toBeUndefined()
    expect(meta('twitter:title')).toBeUndefined()
  })

  it('con título lo cambia en las dos etiquetas', () => {
    usePreviewDelLink({
      titulo: 'Ideas de regalos para Julia',
      descripcion: 'Acá van algunas ideas',
    })

    expect(meta('og:title')).toBe('Ideas de regalos para Julia')
    expect(meta('twitter:title')).toBe('Ideas de regalos para Julia')
  })
})
