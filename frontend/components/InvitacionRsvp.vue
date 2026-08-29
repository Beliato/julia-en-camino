<script setup lang="ts">
/** La invitación al baby shower y el formulario para confirmar.
 *
 * Vive en la página pública porque se comparte con el mismo link que la
 * wishlist. Si ya se respondió desde este navegador se muestra lo que se
 * eligió, con la opción de cambiarlo.
 */
const props = defineProps<{ token: string }>()

const runtime = useRuntimeConfig()
const toast = useToast()
const { respuesta, cargar, guardar, olvidar } = useRsvpLocal()

const LAMINA = '/invitacion-julia.webp'

const nombre = ref('')
const asistira = ref<'SI' | 'NO'>('SI')
const enviando = ref(false)
const laminaOk = ref(true)

onMounted(cargar)

const puedeEnviar = computed(() => !!nombre.value.trim())

async function enviar() {
  if (!puedeEnviar.value) return
  enviando.value = true
  try {
    await $fetch(`/w/${props.token}/rsvp`, {
      method: 'POST',
      baseURL: runtime.public.apiBase,
      body: { nombre: nombre.value.trim(), asistira: asistira.value === 'SI' },
    })
    guardar({ nombre: nombre.value.trim(), asistira: asistira.value === 'SI' })
    toast.add({
      title:
        asistira.value === 'SI' ? '¡Te esperamos! 💕' : 'Gracias por avisar',
      color: 'pink',
    })
  } catch {
    toast.add({
      title: 'No se pudo enviar',
      description: 'Probá de nuevo en un momento.',
      color: 'red',
    })
  } finally {
    enviando.value = false
  }
}

function volverAResponder() {
  nombre.value = respuesta.value?.nombre ?? ''
  asistira.value = respuesta.value?.asistira === false ? 'NO' : 'SI'
  olvidar()
}
</script>

<template>
  <section class="mt-12">
    <img
      v-if="laminaOk"
      :src="LAMINA"
      alt="Invitación al baby shower de Julia"
      class="mx-auto w-full max-w-md rounded-xl shadow-sm"
      @error="laminaOk = false"
    >

    <div class="mx-auto mt-6 max-w-md">
      <!-- Ya respondió desde este navegador -->
      <UCard v-if="respuesta">
        <p class="text-sm text-neutral-600 dark:text-neutral-400">
          {{ respuesta.asistira ? '¡Te esperamos!' : 'Nos avisaste que no vas a poder.' }}
        </p>
        <p class="mt-1 font-medium">
          {{ respuesta.nombre }}
        </p>
        <UButton
          variant="link"
          size="xs"
          class="mt-1 px-0"
          @click="volverAResponder"
        >
          Cambiar mi respuesta
        </UButton>
      </UCard>

      <UCard v-else>
        <form class="space-y-3" @submit.prevent="enviar">
          <UFormGroup label="¿Cómo te llamás?" required>
            <UInput v-model="nombre" placeholder="Tu nombre" />
          </UFormGroup>
          <UFormGroup label="¿Vas a poder venir?">
            <USelect
              v-model="asistira"
              :options="[
                { value: 'SI', label: 'Sí, ahí estaré' },
                { value: 'NO', label: 'No voy a poder' },
              ]"
            />
          </UFormGroup>
          <UButton
            type="submit"
            block
            :loading="enviando"
            :disabled="!puedeEnviar"
          >
            Confirmar
          </UButton>
        </form>
      </UCard>
    </div>
  </section>
</template>
