<script setup lang="ts">
/** La invitación al baby shower y el formulario para confirmar.
 *
 * Vive en su propia página, con un link distinto al de la wishlist. Si
 * ya se respondió desde este navegador se muestra lo que se eligió, con
 * la opción de cambiarlo.
 */
interface DatosEvento {
  lugar: string | null
  fecha: string | null
  hora: string | null
  texto: string | null
  aviso: string | null
  imagen_url: string | null
}

// Los datos llegan desde la página, que ya los pidió con el token: así
// este componente no vuelve a llamar a la API.
const props = defineProps<{ token: string; evento: DatosEvento }>()

const runtime = useRuntimeConfig()
const toast = useToast()

const hayDatosDelEvento = computed(() =>
  Boolean(
    props.evento.lugar ||
      props.evento.fecha ||
      props.evento.hora ||
      props.evento.texto,
  ),
)
const { respuesta, cargar, guardar, olvidar } = useRsvpLocal()

// Lámina propia si la invitación tiene una; si no, la que viene con la
// app, que sirve para varias tandas del mismo baby shower.
const LAMINA_POR_DEFECTO = '/invitacion-julia.webp'
const lamina = computed(() => props.evento.imagen_url || LAMINA_POR_DEFECTO)

const nombre = ref('')
const asistira = ref<'SI' | 'NO'>('SI')
const comentario = ref('')
const enviando = ref(false)
const laminaOk = ref(true)

onMounted(cargar)

const puedeEnviar = computed(() => !!nombre.value.trim())

async function enviar() {
  if (!puedeEnviar.value) return
  enviando.value = true
  try {
    await $fetch(`/i/${props.token}/rsvp`, {
      method: 'POST',
      baseURL: runtime.public.apiBase,
      body: {
        nombre: nombre.value.trim(),
        asistira: asistira.value === 'SI',
        comentario: comentario.value.trim() || null,
      },
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
  <section>
    <!-- Los datos van encima de la lámina, en su franja central vacía, y
         no quemados en la imagen: si cambia la hora se edita desde
         Ajustes en vez de volver a exportar desde Illustrator.
         El bloque se posiciona en porcentajes para acompañar el escalado
         de la imagen en cualquier ancho. -->
    <div v-if="laminaOk" class="relative mx-auto w-full max-w-md">
      <img
        :src="lamina"
        alt="Invitación al baby shower de Julia"
        class="w-full rounded-xl shadow-sm"
        @error="laminaOk = false"
      >
      <div
        v-if="hayDatosDelEvento"
        class="absolute inset-x-[12%] top-[38%] text-center text-[#4A240E]"
      >
        <p
          v-if="evento.texto"
          class="text-[2.6vw] leading-snug sm:text-xs"
        >
          {{ evento.texto }}
        </p>
        <p
          v-if="evento.fecha"
          class="mt-[3%] font-serif text-[4vw] italic sm:text-lg"
        >
          {{ evento.fecha }}
        </p>
        <p v-if="evento.hora" class="text-[3vw] sm:text-sm">
          {{ evento.hora }}
        </p>
        <p
          v-if="evento.lugar"
          class="mt-[3%] text-[3vw] font-medium sm:text-sm"
        >
          {{ evento.lugar }}
        </p>
      </div>
    </div>

    <div class="mx-auto mt-6 max-w-md">
      <!-- Aviso configurable: la fecha límite para confirmar, o por dónde
           más se puede avisar. Va afuera de las dos tarjetas para que se
           vea igual antes y después de responder. -->
      <p
        v-if="evento.aviso"
        class="mb-3 text-center text-sm text-neutral-600 dark:text-neutral-400"
      >
        {{ evento.aviso }}
      </p>

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
          <UFormGroup label="Comentarios para Julia">
            <UTextarea
              v-model="comentario"
              :rows="3"
              placeholder="Un mensaje para cuando sepa leer…"
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
