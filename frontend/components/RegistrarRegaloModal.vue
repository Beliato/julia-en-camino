<script setup lang="ts">
import type { Etapa, Item, OrigenRegalo } from '~/types/api'
import { ETAPAS, ETAPA_LABEL } from '~/types/api'

const emit = defineEmits<{ close: []; done: [] }>()

const regalos = useRegalosStore()
const items = useItemsStore()
const categorias = useCategoriasStore()
const toast = useToast()

// Objeto: se elige uno existente o se crea acá mismo. La mayoría de los
// regalos llegan sin haber pasado por el catálogo.
const modoNuevo = ref(false)
const SIN_ITEM = 0
const itemId = ref<number>(SIN_ITEM)
const busquedaItem = ref('')
const nombreNuevo = ref('')
const etapa = ref<Etapa>('CUALQUIERA')
// -1 y no 0: USelectMenu resuelve la etiqueta con `if (!modelValue)`
// (SelectMenu.vue:402), así que un centinela falsy se muestra como
// campo vacío en vez de "Sin categoría".
const SIN_CATEGORIA = -1
const nuevaCategoria = ref('')
const creandoCategoria = ref(false)
const categoriaId = ref<number>(SIN_CATEGORIA)

const origen = ref<OrigenRegalo>('REGALO')
const persona = ref('')
const cantidad = ref(1)
const fecha = ref(new Date().toISOString().slice(0, 10))
const nota = ref('')
const guardando = ref(false)

onMounted(async () => {
  await Promise.all([
    items.fetchAll(),
    regalos.fetchPersonas(),
    categorias.fetchAll(),
  ])
})

const opcionesCategoria = computed(() => [
  { value: SIN_CATEGORIA, label: 'Sin categoría' },
  ...categorias.categorias.map((c) => ({ value: c.id, label: c.nombre })),
])

const itemsFiltrados = computed(() => {
  const q = busquedaItem.value.trim().toLowerCase()
  const lista = q
    ? items.items.filter((i) => i.nombre.toLowerCase().includes(q))
    : items.items
  return lista.slice(0, 50).map((i: Item) => ({
    value: i.id,
    label:
      i.cantidad > 1
        ? `${i.nombre} (${i.cantidad_recibida}/${i.cantidad})`
        : i.nombre,
  }))
})

const sugerencias = computed(() => {
  const q = persona.value.trim().toLowerCase()
  if (!q) return regalos.personas.slice(0, 6)
  return regalos.personas
    .filter((p) => p.toLowerCase().includes(q) && p.toLowerCase() !== q)
    .slice(0, 6)
})

const puedeGuardar = computed(() => {
  const objetoOk = modoNuevo.value
    ? !!nombreNuevo.value.trim()
    : itemId.value !== SIN_ITEM
  const personaOk = origen.value === 'NOSOTROS' || !!persona.value.trim()
  return objetoOk && personaOk
})

/** Id de la categoría a usar, creándola antes si hace falta. */
async function resolverCategoria(): Promise<number | null> {
  if (creandoCategoria.value && nuevaCategoria.value.trim()) {
    const nombre = nuevaCategoria.value.trim()
    // El nombre de categoría es único en la base. Si ya existe se
    // reutiliza: fallar el registro entero del regalo por un duplicado
    // sería desproporcionado, y escribir una que ya está es habitual.
    const existente = categorias.categorias.find(
      (c) => c.nombre.toLowerCase() === nombre.toLowerCase(),
    )
    if (existente) return existente.id
    const creada = await categorias.crear(nombre)
    return creada.id
  }
  return categoriaId.value === SIN_CATEGORIA ? null : categoriaId.value
}

async function guardar() {
  if (!puedeGuardar.value) return
  guardando.value = true
  try {
    const categoria_id = modoNuevo.value ? await resolverCategoria() : null
    await regalos.registrar({
      ...(modoNuevo.value
        ? {
            item_nuevo: {
              nombre: nombreNuevo.value.trim(),
              etapa: etapa.value,
              categoria_id,
            },
          }
        : { item_id: itemId.value }),
      persona: origen.value === 'REGALO' ? persona.value.trim() : '',
      origen: origen.value,
      cantidad: cantidad.value,
      fecha: fecha.value,
      nota: nota.value.trim() || null,
    })
    toast.add({
      title: '¡Anotado! 🎁',
      description:
        origen.value === 'REGALO'
          ? `Gracias a ${persona.value.trim()} quedó registrado.`
          : 'Quedó registrado como comprado por ustedes.',
      color: 'pink',
    })
    emit('done')
    emit('close')
  } catch {
    toast.add({ title: 'No se pudo registrar', color: 'red' })
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <!-- Tope de alto con el cuerpo scrolleable y los botones anclados
       abajo. Sin esto el modal medía 671px y en una laptop de 620px el
       botón Registrar quedaba fuera de la pantalla: se llegaba
       scrolleando, pero no se veía que hubiera que hacerlo. -->
  <UModal
    :model-value="true"
    :ui="{ height: 'max-h-[85vh]' }"
    @update:model-value="emit('close')"
  >
    <UCard
      :ui="{
        base: 'flex max-h-[85vh] flex-col',
        body: { base: 'min-h-0 flex-1 overflow-y-auto' },
      }"
    >
      <template #header>
        <h3 class="text-lg font-medium">Registrar un regalo</h3>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Anotá qué recibieron y de parte de quién.
        </p>
      </template>

      <form id="form-registrar-regalo" class="space-y-4" @submit.prevent="guardar">
        <UFormGroup label="¿Qué recibieron?" required>
          <template v-if="!modoNuevo">
            <USelectMenu
              v-model="itemId"
              v-model:query="busquedaItem"
              :options="itemsFiltrados"
              value-attribute="value"
              option-attribute="label"
              searchable
              placeholder="Buscá en el catálogo…"
            />
            <UButton
              variant="link"
              size="xs"
              icon="i-heroicons-plus"
              class="mt-1"
              @click="modoNuevo = true"
            >
              No está en la lista, agregarlo
            </UButton>
          </template>
          <template v-else>
            <UInput v-model="nombreNuevo" placeholder="Nombre del objeto" autofocus />
            <!-- USelectMenu y no USelect: este value es numérico y el
                 select nativo devolvería el id como texto. -->
            <USelectMenu
              v-if="!creandoCategoria"
              v-model="categoriaId"
              class="mt-2"
              :options="opcionesCategoria"
              value-attribute="value"
              option-attribute="label"
              aria-label="Categoría del objeto"
            />
            <UInput
              v-else
              v-model="nuevaCategoria"
              class="mt-2"
              placeholder="Nombre de la categoría nueva"
              aria-label="Nombre de la categoría nueva"
            />
            <UButton
              variant="link"
              size="xs"
              :icon="creandoCategoria ? undefined : 'i-heroicons-plus'"
              class="mt-1"
              @click="creandoCategoria = !creandoCategoria"
            >
              {{
                creandoCategoria
                  ? 'Usar una categoría existente'
                  : 'Crear categoría nueva'
              }}
            </UButton>
            <USelect
              v-model="etapa"
              class="mt-2"
              :options="ETAPAS.map((e) => ({ value: e, label: ETAPA_LABEL[e] }))"
            />
            <UButton variant="link" size="xs" class="mt-1" @click="modoNuevo = false">
              Elegir uno del catálogo
            </UButton>
          </template>
        </UFormGroup>

        <UFormGroup label="¿De dónde vino?">
          <URadioGroup
            v-model="origen"
            :options="[
              { value: 'REGALO', label: 'Nos lo regalaron' },
              { value: 'NOSOTROS', label: 'Lo compramos nosotros' },
            ]"
          />
        </UFormGroup>

        <UFormGroup v-if="origen === 'REGALO'" label="¿Quién lo regaló?" required>
          <UInput v-model="persona" placeholder="Nombre de la persona" />
          <div v-if="sugerencias.length > 0" class="mt-2 flex flex-wrap gap-1">
            <UButton
              v-for="s in sugerencias"
              :key="s"
              size="xs"
              variant="soft"
              color="pink"
              @click="persona = s"
            >
              {{ s }}
            </UButton>
          </div>
        </UFormGroup>

        <!-- Apilados en celular. En dos columnas el input de fecha recibe
             122px y su min-content es 144: Safari de iOS no encoge por
             debajo de ese mínimo y empuja el modal a lo ancho, obligando
             a pellizcar la pantalla. -->
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <UFormGroup label="¿Cuántos?">
            <UInput v-model.number="cantidad" type="number" min="1" max="99" />
          </UFormGroup>
          <UFormGroup label="¿Cuándo?">
            <UInput v-model="fecha" type="date" />
          </UFormGroup>
        </div>

        <UFormGroup label="Nota (opcional)">
          <UTextarea v-model="nota" :rows="2" placeholder="Algo para recordar…" />
        </UFormGroup>

      </form>

      <!-- Los botones salen del <form> para quedar anclados en el pie;
           el atributo form los mantiene atados al submit. -->
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="ghost" color="gray" @click="emit('close')">
            Cancelar
          </UButton>
          <UButton
            type="submit"
            form="form-registrar-regalo"
            :loading="guardando"
            :disabled="!puedeGuardar"
          >
            Registrar
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>
