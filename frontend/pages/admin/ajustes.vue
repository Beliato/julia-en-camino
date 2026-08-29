<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const config = useConfigStore()
const toast = useToast()

const shareToken = ref('')
const invitacionToken = ref('')
const copiadoInvitacion = ref(false)
const nombre = ref('')
const guardando = ref(false)
const copiado = ref(false)

const evento = reactive({ lugar: '', fecha: '', hora: '', texto: '' })
const guardandoEvento = ref(false)

const shareUrl = computed(() =>
  shareToken.value ? `${location.origin}/w/${shareToken.value}` : '',
)
const invitacionUrl = computed(() =>
  invitacionToken.value ? `${location.origin}/i/${invitacionToken.value}` : '',
)

onMounted(async () => {
  await config.fetch()
  nombre.value = config.nombreApp

  const api = useApi()
  const data = await api<{ share_token: string; invitacion_token: string }>(
    '/wishlist/link',
  )
  shareToken.value = data.share_token
  invitacionToken.value = data.invitacion_token

  // Los datos del evento se leen contra el token de la invitación: no
  // viajan en /config, que es público y sin token.
  const runtime = useRuntimeConfig()
  const inv = await $fetch<{
    evento_lugar: string | null
    evento_fecha: string | null
    evento_hora: string | null
    evento_texto: string | null
  }>(`/i/${data.invitacion_token}`, { baseURL: runtime.public.apiBase })
  evento.lugar = inv.evento_lugar ?? ''
  evento.fecha = inv.evento_fecha ?? ''
  evento.hora = inv.evento_hora ?? ''
  evento.texto = inv.evento_texto ?? ''
})

async function copiarLink() {
  await navigator.clipboard.writeText(shareUrl.value)
  copiado.value = true
  setTimeout(() => (copiado.value = false), 2000)
}

async function copiarInvitacion() {
  await navigator.clipboard.writeText(invitacionUrl.value)
  copiadoInvitacion.value = true
  setTimeout(() => (copiadoInvitacion.value = false), 2000)
}

async function guardarNombre() {
  guardando.value = true
  try {
    await config.guardar({ nombre_app: nombre.value.trim() })
    toast.add({ title: 'Nombre actualizado', color: 'green' })
  } catch {
    toast.add({ title: 'No se pudo actualizar el nombre', color: 'red' })
  } finally {
    guardando.value = false
  }
}

async function guardarEvento() {
  guardandoEvento.value = true
  try {
    // Se mandan los cuatro siempre: vaciar un campo tiene que poder
    // borrar ese renglón de la invitación.
    await config.guardar({
      evento_lugar: evento.lugar.trim(),
      evento_fecha: evento.fecha.trim(),
      evento_hora: evento.hora.trim(),
      evento_texto: evento.texto.trim(),
    })
    toast.add({ title: 'Invitación actualizada', color: 'green' })
  } catch {
    toast.add({ title: 'No se pudo guardar', color: 'red' })
  } finally {
    guardandoEvento.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <UButton
        variant="ghost"
        color="gray"
        icon="i-heroicons-arrow-left"
        to="/admin"
        aria-label="Volver al catálogo"
      />
      <h2 class="text-xl font-medium text-pink-800 dark:text-pink-200">
        Ajustes
      </h2>
    </div>

    <UCard>
      <template #header>
        <h3 class="font-medium">Invitación al baby shower</h3>
      </template>
      <div class="space-y-3">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Este es el link para invitar. Muestra la invitación y el formulario
          para confirmar asistencia — no muestra la lista de regalos.
        </p>
        <div class="flex gap-2">
          <UInput
            :model-value="invitacionUrl"
            readonly
            class="flex-1"
            aria-label="Link de la invitación"
          />
          <UButton
            :icon="copiadoInvitacion ? 'i-heroicons-check' : 'i-heroicons-clipboard'"
            :color="copiadoInvitacion ? 'green' : 'pink'"
            @click="copiarInvitacion"
          >
            {{ copiadoInvitacion ? 'Copiado' : 'Copiar' }}
          </UButton>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Antes de mandarlo, cargá los datos del evento acá abajo.
        </p>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <h3 class="font-medium">Compartir la wishlist</h3>
      </template>
      <div class="space-y-3">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Link aparte, para quien pregunte qué hace falta. Verán solo los
          items por comprar y podrán reservar qué regalar — sin crear cuenta.
        </p>
        <div class="flex gap-2">
          <UInput :model-value="shareUrl" readonly class="flex-1" aria-label="Link de la wishlist" />
          <UButton
            :icon="copiado ? 'i-heroicons-check' : 'i-heroicons-clipboard'"
            :color="copiado ? 'green' : 'pink'"
            @click="copiarLink"
          >
            {{ copiado ? 'Copiado' : 'Copiar' }}
          </UButton>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Cualquiera con el link puede ver y reservar — compártelo solo con
          el círculo cercano.
        </p>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <h3 class="font-medium">Nombre de la app</h3>
      </template>
      <form class="flex gap-2" @submit.prevent="guardarNombre">
        <UInput v-model="nombre" required class="flex-1" aria-label="Nombre de la app" />
        <UButton type="submit" :loading="guardando">Guardar</UButton>
      </form>
    </UCard>

    <UCard>
      <template #header>
        <h3 class="font-medium">Datos del baby shower</h3>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Se muestran en el centro de la invitación. Lo que dejes vacío no
          aparece.
        </p>
      </template>
      <form class="space-y-3" @submit.prevent="guardarEvento">
        <UFormGroup label="Texto de invitación">
          <UTextarea
            v-model="evento.texto"
            :rows="2"
            placeholder="Acompañanos a celebrar la llegada de Julia"
          />
        </UFormGroup>
        <UFormGroup label="Fecha">
          <UInput v-model="evento.fecha" placeholder="Sábado 15 de noviembre" />
        </UFormGroup>
        <UFormGroup label="Hora">
          <UInput v-model="evento.hora" placeholder="De 4 a 7 de la tarde" />
        </UFormGroup>
        <UFormGroup label="Lugar">
          <UInput v-model="evento.lugar" placeholder="Salón El Jardín, Av. Siempre Viva 123" />
        </UFormGroup>
        <div class="flex justify-end">
          <UButton type="submit" :loading="guardandoEvento">Guardar</UButton>
        </div>
      </form>
    </UCard>
  </div>
</template>
