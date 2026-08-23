<script setup lang="ts">
/** Cuánto falta para que esté todo listo, de un vistazo.
 *
 * Es lo que convierte el catálogo en algo que se lee y no solo en una
 * lista que se recorre. Los tres números responden preguntas distintas:
 * cuánto se avanzó, qué está por llegar, y qué falta agradecer — este
 * último vive en la otra pantalla y es el más fácil de olvidar.
 */
import type { Item } from '~/types/api'

const props = defineProps<{
  items: Item[]
  enCamino: number
  sinAgradecer: number
}>()

const resueltos = computed(
  () => props.items.filter((i) => i.estado === 'ADQUIRIDO').length,
)
const total = computed(() => props.items.length)
const porcentaje = computed(() =>
  total.value === 0 ? 0 : Math.round((resueltos.value / total.value) * 100),
)
</script>

<template>
  <div
    v-if="total > 0"
    class="rounded-xl border border-neutral-200 bg-gradient-to-b from-pink-50 to-neutral-100 p-4 dark:border-neutral-800 dark:from-neutral-900 dark:to-neutral-900/50"
  >
    <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1">
      <p class="font-serif text-2xl italic text-pink-800 dark:text-pink-200">
        {{ resueltos }} de {{ total }}
      </p>
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        ya lo tienen
      </p>
      <span
        v-if="enCamino > 0 || sinAgradecer > 0"
        class="ml-auto flex flex-wrap gap-2 text-xs"
      >
        <UBadge v-if="enCamino > 0" color="amber" variant="subtle">
          {{ enCamino }} en camino
        </UBadge>
        <ULink
          v-if="sinAgradecer > 0"
          to="/admin/regalos"
          class="rounded-full bg-pink-100 px-2 py-0.5 font-medium text-pink-800 hover:bg-pink-200 dark:bg-pink-950 dark:text-pink-200"
        >
          {{ sinAgradecer }} sin agradecer
        </ULink>
      </span>
    </div>

    <div
      class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-neutral-200 dark:bg-neutral-800"
    >
      <div
        class="h-full rounded-full bg-pink-600 transition-all duration-500 dark:bg-pink-400"
        :style="{ width: `${porcentaje}%` }"
      />
    </div>
  </div>
</template>
