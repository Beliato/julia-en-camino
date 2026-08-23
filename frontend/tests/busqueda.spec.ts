import { describe, expect, it } from 'vitest'

import { interpretarBusqueda } from '~/utils/busqueda'

describe('interpretarBusqueda', () => {
  it('busca por texto cuando no hay prefijo', () => {
    expect(interpretarBusqueda('body manga corta')).toEqual({
      q: 'body manga corta',
    })
  })

  it('reconoce From: y devuelve la persona', () => {
    expect(interpretarBusqueda('From: Hannia')).toEqual({ persona: 'Hannia' })
  })

  it('no distingue mayusculas en el prefijo', () => {
    expect(interpretarBusqueda('from:Hannia')).toEqual({ persona: 'Hannia' })
    expect(interpretarBusqueda('FROM: Hannia')).toEqual({ persona: 'Hannia' })
  })

  it('acepta el prefijo en castellano', () => {
    expect(interpretarBusqueda('de: Alexandra')).toEqual({
      persona: 'Alexandra',
    })
  })

  it('tolera espacios alrededor de los dos puntos', () => {
    expect(interpretarBusqueda('  From  :  Ana Maria ')).toEqual({
      persona: 'Ana Maria',
    })
  })

  it('conserva el nombre completo con apellido', () => {
    expect(interpretarBusqueda('From: Alexandra Rey y Marius')).toEqual({
      persona: 'Alexandra Rey y Marius',
    })
  })

  it('devuelve null mientras solo se escribio el prefijo', () => {
    // Sin nombre no hay que pegarle al backend: la persona sigue tecleando
    expect(interpretarBusqueda('From:')).toBeNull()
    expect(interpretarBusqueda('From:   ')).toBeNull()
  })

  it('devuelve null con la barra vacia', () => {
    expect(interpretarBusqueda('')).toBeNull()
    expect(interpretarBusqueda('   ')).toBeNull()
  })

  it('no confunde un nombre que contiene la palabra from', () => {
    expect(interpretarBusqueda('almohada from ikea')).toEqual({
      q: 'almohada from ikea',
    })
  })
})
