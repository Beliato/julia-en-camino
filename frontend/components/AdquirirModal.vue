<script setup lang="ts">
import type { Item, OrigenRegalo } from '~/types/api'
import { ORIGENES_CON_PERSONA } from '~/types/api'

const props = defineProps<{ item: Item }>()
const emit = defineEmits<{ close: []; done: [] }>()

const items = useItemsStore()
const toast = useToast()

const origen = ref<OrigenRegalo>('NOSOTROS')
const llevaPersona = computed(() => ORIGENES_CON_PERSONA.includes(origen.value))
const gifterName = ref('')
const guardando = ref(false)

const faltantes = computed(
  () => props.item.cantidad - props.item.cantidad_recibida,
)

async function confirmar() {
  guardando.value = true
  try {
    await items.adquirir(
      props.item.id,
      origen.value,
      llevaPersona.value ? gifterName.value.trim() || null : null,
    )
    emit('done')
    emit('close')
  } catch (e: unknown) {
    const status = (e as { statusCode?: number }).statusCode
    toast.add({
      title: 'No se pudo marcar como adquirido',
      description:
        status === 409
          ? 'Hay unidades reservadas: resolvelas desde "Regalos en camino" primero.'
          : undefined,
      color: 'red',
    })
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <UModal :model-value="true" @update:model-value="emit('close')">
    <UCard>
      <template #header>
        <h3 class="text-lg font-medium">Marcar como adquirido</h3>
      </template>

      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          <span class="font-medium">{{ props.item.nombre }}</span>
          <span v-if="props.item.cantidad > 1">
            — se marcarán las {{ faltantes }} unidades que faltan
          </span>
        </p>

        <UFormGroup label="¿Cómo lo obtuvieron?">
          <URadioGroup
            v-model="origen"
            :options="[
              { value: 'NOSOTROS', label: 'Lo compramos nosotros' },
              { value: 'REGALO', label: 'Fue un regalo' },
              { value: 'PRESTADO', label: 'Nos lo prestaron' },
            ]"
          />
        </UFormGroup>

        <UFormGroup
          v-if="llevaPersona"
          :label="origen === 'PRESTADO' ? '¿Quién lo prestó?' : '¿Quién lo regaló?'"
        >
          <UInput v-model="gifterName" placeholder="Nombre de la persona" />
        </UFormGroup>

        <div class="flex justify-end gap-2">
          <UButton variant="ghost" color="gray" @click="emit('close')">
            Cancelar
          </UButton>
          <UButton :loading="guardando" @click="confirmar">
            Confirmar
          </UButton>
        </div>
      </div>
    </UCard>
  </UModal>
</template>
