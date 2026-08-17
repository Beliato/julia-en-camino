import { describe, expect, it, vi } from 'vitest'

import { calcularMedidas, comprimirImagen } from '~/utils/comprimirImagen'

describe('calcularMedidas', () => {
  it('no agranda una imagen que ya entra', () => {
    expect(calcularMedidas(800, 600)).toEqual({ ancho: 800, alto: 600 })
  })

  it('escala por el lado mas largo conservando la proporcion', () => {
    // Una foto apaisada de celular: 4032x3024 (4:3)
    const r = calcularMedidas(4032, 3024)
    expect(r.ancho).toBe(1600)
    expect(r.alto).toBe(1200)
  })

  it('toma el alto cuando la foto es vertical', () => {
    const r = calcularMedidas(3024, 4032)
    expect(r.alto).toBe(1600)
    expect(r.ancho).toBe(1200)
  })

  it('no divide por cero con medidas vacias', () => {
    expect(calcularMedidas(0, 0)).toEqual({ ancho: 0, alto: 0 })
  })
})

describe('comprimirImagen', () => {
  it('deja pasar lo que no es imagen sin tocarlo', async () => {
    const pdf = new File(['x'], 'guia.pdf', { type: 'application/pdf' })
    expect(await comprimirImagen(pdf)).toBe(pdf)
  })

  it('devuelve el original si el navegador no puede decodificar', async () => {
    // Caso real: un HEIC en un navegador que no lo soporta. Preferimos
    // que falle el backend con un mensaje claro antes que perder la foto.
    vi.stubGlobal(
      'createImageBitmap',
      vi.fn().mockRejectedValue(new Error('formato no soportado')),
    )
    const heic = new File(['x'], 'IMG_0001.heic', { type: 'image/heic' })
    expect(await comprimirImagen(heic)).toBe(heic)
    vi.unstubAllGlobals()
  })
})
