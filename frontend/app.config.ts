// Nuxt UI combina lo que se pone acá con sus clases por defecto usando
// tailwind-merge: el resultado es `twMerge(default, esto)`. Por eso alcanza
// con escribir lo que cambia — cuando dos clases chocan (`ease-in` contra
// `ease-[...]`), gana la de acá.
//
// Esa misma regla obliga a una cosa en el movimiento reducido: una clase
// con variante (`motion-reduce:translate-y-0`) no choca con la misma clase
// sin variante (`translate-y-4`), así que la de Nuxt UI queda. Lo que se
// hace es agregar la variante que la neutraliza cuando el usuario pidió
// menos movimiento, y dejar que el orden de Tailwind —las variantes van
// después— la haga ganar.
//
// Se descartó `strategy: 'override'`, que reemplazaría los strings
// enteros: Nuxt UI la lee solo a nivel global, así que habría cambiado
// también cómo se combinan los `:ui` del proyecto y la posición de los
// toasts.

// Salida fuerte para entrar y salir; definida en assets/css/main.css.
const CURVA = 'ease-[var(--ease-out-fuerte)]'

export default defineAppConfig({
  ui: {
    primary: 'pink',
    gray: 'neutral',

    notifications: {
      position: 'top-0 bottom-auto',
    },

    notification: {
      transition: {
        enterActiveClass: CURVA,
        // Los toasts viven arriba (ver `notifications.position`), pero
        // Nuxt UI los hace entrar con `translate-y-2`, desde abajo,
        // pensando en su ubicación por defecto. En el celular, donde van a
        // lo ancho, tienen que bajar desde arriba. En escritorio siguen
        // entrando desde la derecha, que es el borde al que se pegan.
        enterFromClass:
          '-translate-y-2 motion-reduce:translate-y-0 motion-reduce:sm:translate-x-0',
        // Salir con `ease-in` retrasa justo el momento que se está mirando.
        leaveActiveClass: CURVA,
      },
    },

    modal: {
      overlay: {
        transition: {
          enter: `${CURVA} duration-[250ms]`,
          leave: `${CURVA} duration-200`,
        },
      },
      // 250ms con una curva fuerte se siente más ágil que los 300ms con la
      // `ease-out` de Tailwind. La salida sigue siendo más corta que la
      // entrada: cerrar es una respuesta, no algo que haya que mirar.
      transition: {
        enter: `${CURVA} duration-[250ms]`,
        leave: `${CURVA} duration-200`,
        // El modal se sigue desvaneciendo con movimiento reducido; lo que
        // se quita es el desplazamiento y el cambio de escala.
        enterFrom: 'motion-reduce:translate-y-0 motion-reduce:sm:scale-100',
        leaveTo: 'motion-reduce:translate-y-0 motion-reduce:sm:scale-100',
      },
    },

    dropdown: {
      // El origen desde el botón lo pone assets/css/main.css, siguiendo la
      // ubicación que eligió popper.
      transition: {
        enterActiveClass: CURVA,
        leaveActiveClass: CURVA,
        enterFromClass: 'motion-reduce:scale-100',
        leaveToClass: 'motion-reduce:scale-100',
      },
    },

    selectMenu: {
      transition: {
        leaveActiveClass: CURVA,
      },
    },
  },
})
