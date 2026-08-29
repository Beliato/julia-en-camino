<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const rsvps = useRsvpsStore()
const toast = useToast()

const aBorrar = ref<{ id: number; nombre: string } | null>(null)

onMounted(() => rsvps.fetchAll())

const vienen = computed(() => rsvps.respuestas.filter((r) => r.asistira))
const noVienen = computed(() => rsvps.respuestas.filter((r) => !r.asistira))

function cuando(iso: string): string {
  return new Date(iso).toLocaleDateString('es', {
    day: 'numeric',
    month: 'long',
  })
}

async function borrar() {
  if (!aBorrar.value) return
  try {
    await rsvps.eliminar(aBorrar.value.id)
    toast.add({ title: 'Respuesta eliminada', color: 'green' })
  } catch {
    toast.add({ title: 'No se pudo eliminar', color: 'red' })
  } finally {
    aBorrar.value = null
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-xl font-medium text-pink-800 dark:text-pink-200">
        Baby shower
      </h2>
      <UButton
        variant="ghost"
        color="gray"
        icon="i-heroicons-arrow-left"
        to="/admin"
      >
        Volver al catálogo
      </UButton>
    </div>

    <div
      class="rounded-xl border border-neutral-200 bg-gradient-to-b from-pink-50 to-neutral-100 p-4 dark:border-neutral-800 dark:from-neutral-900 dark:to-neutral-900/50"
    >
      <div class="flex flex-wrap items-baseline gap-x-2">
        <p class="font-serif text-2xl italic text-pink-800 dark:text-pink-200">
          {{ rsvps.asisten }}
        </p>
        <p class="text-sm text-neutral-600 dark:text-neutral-400">
          {{ rsvps.asisten === 1 ? 'persona confirmó' : 'personas confirmaron' }}
        </p>
        <span
          v-if="rsvps.noAsisten > 0"
          class="ml-auto text-xs text-neutral-500 dark:text-neutral-400"
        >
          {{ rsvps.noAsisten }} no van a poder
        </span>
      </div>
    </div>

    <div v-if="rsvps.cargando" class="py-10 text-center">
      <UIcon name="i-heroicons-heart" class="h-8 w-8 animate-pulse text-pink-400" />
    </div>

    <UCard v-else-if="rsvps.respuestas.length === 0">
      <p class="py-6 text-center text-sm text-gray-500 dark:text-gray-400">
        Todavía nadie respondió la invitación.
      </p>
    </UCard>

    <template v-else>
      <UCard v-if="vienen.length > 0">
        <template #header>
          <h3 class="text-sm font-medium">Vienen ({{ vienen.length }})</h3>
        </template>
        <ul class="divide-y divide-neutral-200 dark:divide-neutral-800">
          <li
            v-for="r in vienen"
            :key="r.id"
            class="flex items-center justify-between gap-2 py-2"
          >
            <span class="min-w-0 truncate text-sm font-medium">{{ r.nombre }}</span>
            <span class="ml-auto text-xs text-gray-500 dark:text-gray-400">
              {{ cuando(r.created_at) }}
            </span>
            <UButton
              variant="ghost"
              color="gray"
              icon="i-heroicons-trash"
              size="xs"
              :aria-label="`Eliminar la respuesta de ${r.nombre}`"
              @click="aBorrar = { id: r.id, nombre: r.nombre }"
            />
          </li>
        </ul>
      </UCard>

      <UCard v-if="noVienen.length > 0">
        <template #header>
          <h3 class="text-sm font-medium">No pueden ({{ noVienen.length }})</h3>
        </template>
        <ul class="divide-y divide-neutral-200 dark:divide-neutral-800">
          <li
            v-for="r in noVienen"
            :key="r.id"
            class="flex items-center justify-between gap-2 py-2"
          >
            <span class="min-w-0 truncate text-sm">{{ r.nombre }}</span>
            <UButton
              variant="ghost"
              color="gray"
              icon="i-heroicons-trash"
              size="xs"
              :aria-label="`Eliminar la respuesta de ${r.nombre}`"
              @click="aBorrar = { id: r.id, nombre: r.nombre }"
            />
          </li>
        </ul>
      </UCard>
    </template>

    <ConfirmModal
      v-if="aBorrar"
      titulo="Eliminar respuesta"
      :descripcion="`Se borra la respuesta de «${aBorrar.nombre}». Si vuelve a confirmar, entra de nuevo.`"
      confirm-label="Eliminar"
      @close="aBorrar = null"
      @confirm="borrar"
    />
  </div>
</template>
