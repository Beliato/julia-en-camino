<script setup lang="ts">
/** Botones para adjuntar una foto: cámara o galería.
 *
 * El botón de cámara solo se muestra en pantallas táctiles. En
 * escritorio el atributo `capture` se ignora y abriría el mismo
 * explorador de archivos que el otro botón, así que tener los dos
 * ahí solo confunde.
 *
 * Los `accept` van en `image/*` a propósito: con una lista explícita de
 * MIME types, Safari en iPhone no ofrece la opción de sacar la foto.
 * Lo que llegue se normaliza en `comprimirImagen`.
 */
import { comprimirImagen } from '~/utils/comprimirImagen'

withDefaults(
  defineProps<{
    cargando?: boolean
    etiqueta?: string
    size?: 'xs' | 'sm'
    /** Solo íconos, para montarlo encima de una foto sin taparla. */
    compacto?: boolean
  }>(),
  {
    cargando: false,
    etiqueta: 'Agregar foto',
    size: 'sm',
    compacto: false,
  },
)

const emit = defineEmits<{ seleccion: [file: File] }>()

const inputCamara = ref<HTMLInputElement>()
const inputGaleria = ref<HTMLInputElement>()
const tactil = ref(false)
const preparando = ref(false)

onMounted(() => {
  tactil.value = window.matchMedia('(pointer: coarse)').matches
})

async function onArchivo(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  // Se limpia antes de procesar para poder volver a elegir la misma foto
  input.value = ''
  if (!file) return

  preparando.value = true
  try {
    emit('seleccion', await comprimirImagen(file))
  } finally {
    preparando.value = false
  }
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <UButton
      v-if="tactil"
      :variant="compacto ? 'solid' : 'outline'"
      :color="compacto ? 'white' : 'primary'"
      :size="size"
      icon="i-heroicons-camera"
      :loading="cargando || preparando"
      :aria-label="compacto ? 'Tomar foto' : undefined"
      @click="inputCamara?.click()"
    >
      <template v-if="!compacto">Tomar foto</template>
    </UButton>
    <UButton
      :variant="compacto ? 'solid' : 'outline'"
      :color="compacto ? 'white' : 'primary'"
      :size="size"
      icon="i-heroicons-photo"
      :loading="cargando || preparando"
      :aria-label="compacto ? etiqueta : undefined"
      @click="inputGaleria?.click()"
    >
      <template v-if="!compacto">{{ tactil ? 'Galería' : etiqueta }}</template>
    </UButton>

    <input
      ref="inputCamara"
      type="file"
      accept="image/*"
      capture="environment"
      class="hidden"
      @change="onArchivo"
    >
    <input
      ref="inputGaleria"
      type="file"
      accept="image/*"
      class="hidden"
      @change="onArchivo"
    >
  </div>
</template>
