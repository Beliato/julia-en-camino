<script setup lang="ts">
/** Marca de posición para los items que todavía no tienen foto.
 *
 * Sin esto la tarjeta sin foto queda más baja que las demás y la grilla
 * se ve despareja. La flor es el mismo motivo que separa las secciones
 * en la página pública.
 */
withDefaults(defineProps<{ alto?: string }>(), { alto: 'h-40' })
</script>

<template>
  <div
    :class="[
      alto,
      'flex w-full items-center justify-center rounded-lg bg-gradient-to-b from-pink-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800',
    ]"
    aria-hidden="true"
  >
    <span class="text-3xl text-pink-300 dark:text-pink-200/30">❀</span>
  </div>
</template>
