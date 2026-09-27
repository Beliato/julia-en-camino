/** El texto que se ve al compartir un link por WhatsApp.
 *
 * Quien arma ese recuadro es un robot que no ejecuta JavaScript: solo lee
 * el HTML que devuelve el servidor. Por eso el texto tiene que ser fijo y
 * no salir de datos que la página pide después de cargar — si dependiera
 * de eso, el recuadro quedaría con el texto de la app o vacío.
 *
 * Nuxt renderiza estas etiquetas en el servidor, así que llamar a esto
 * desde una página alcanza para que el robot las vea.
 *
 * Los textos por defecto del sitio viven en nuxt.config.ts; esto los pisa
 * solo en la página que lo llama, porque la wishlist y la invitación se
 * comparten con gente distinta y no dicen lo mismo.
 */
export function usePreviewDelLink(opciones: {
  titulo?: string
  descripcion: string
}) {
  const { titulo, descripcion } = opciones

  useHead({
    meta: [
      { name: 'description', content: descripcion },
      { property: 'og:description', content: descripcion },
      { name: 'twitter:description', content: descripcion },
      ...(titulo
        ? [
            { property: 'og:title', content: titulo },
            { name: 'twitter:title', content: titulo },
          ]
        : []),
    ],
  })
}
