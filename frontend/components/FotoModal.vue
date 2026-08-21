<script setup lang="ts">
/** Muestra una foto en grande dentro de un marco.
 *
 * El marco son los 1.5rem de padding: el fondo lo pone el panel del
 * propio UModal, así que no hace falta pintarlo de nuevo. La X vive
 * dentro de esa banda, y mide exactamente 1.5rem de alto para no
 * desbordarla ni pisar la foto.
 */
defineProps<{ url: string; alt?: string }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <UModal
    :model-value="true"
    :ui="{ width: 'sm:max-w-3xl' }"
    @update:model-value="emit('close')"
  >
    <div class="relative p-6">
      <img
        :src="url"
        :alt="alt ?? ''"
        class="max-h-[70vh] w-full rounded object-contain"
      >
      <UButton
        variant="ghost"
        color="gray"
        size="xs"
        icon="i-heroicons-x-mark"
        :padded="false"
        class="absolute right-0 top-0 h-6 w-6 justify-center"
        aria-label="Cerrar"
        @click="emit('close')"
      />
    </div>
  </UModal>
</template>
