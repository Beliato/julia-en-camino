/** Interpreta lo que se escribe en la barra de búsqueda del admin.
 *
 * `From: Hannia` (o `de: Hannia`) busca por quién regaló, con
 * coincidencia parcial. Cualquier otra cosa busca por nombre y
 * descripción, como siempre.
 */

export interface CriterioBusqueda {
  q?: string
  persona?: string
}

const PREFIJO_PERSONA = /^\s*(?:from|de)\s*:\s*(.*)$/i

/** Devuelve null cuando todavía no hay nada que buscar.
 *
 * Incluye el caso de haber escrito solo `From:`: sin nombre no tiene
 * sentido pegarle al backend mientras la persona sigue tecleando.
 */
export function interpretarBusqueda(texto: string): CriterioBusqueda | null {
  const porPersona = PREFIJO_PERSONA.exec(texto)
  if (porPersona) {
    const persona = (porPersona[1] ?? '').trim()
    return persona ? { persona } : null
  }
  const q = texto.trim()
  return q ? { q } : null
}
