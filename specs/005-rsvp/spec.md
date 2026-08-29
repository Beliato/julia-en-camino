# 005 — Confirmación de asistencia al baby shower

## Por qué

El diseño original de Stitch traía un RSVP y en la tanda 004 se decidió
sacarlo, dejándolo anotado como "spec aparte" si algún día hacía falta.
Hizo falta.

## Qué se construye

1. **Una sección en la página pública** con la lámina de la invitación y
   un formulario de dos campos: nombre y si va a poder venir o no.
2. **Una pantalla en el admin** para ir viendo quiénes confirmaron.

## Decisiones

1. **Sin identidad, igual que las reservas.** La invitación se comparte
   con el mismo link que la wishlist; nadie crea cuenta. El envío va con
   el mismo límite de 10 por minuto que las reservas.

2. **Se acepta que alguien responda dos veces.** El navegador recuerda
   la respuesta en localStorage y muestra lo elegido con opción a
   cambiarlo, pero eso no es un control: basta otro teléfono. Deduplicar
   por nombre obligaría a adivinar si «Ana» y «Ana Pérez» son la misma
   persona, y equivocarse ahí borra la respuesta de alguien. Se prefiere
   que el admin pueda borrar duplicados a mano.

3. **La lámina se rasteriza.** El SVG que llegó de Illustrator pesa
   12,4 MB, y optimizado con svgo sigue en 6,4 MB — inviable para la
   página que la familia abre desde el celular con datos. Rasterizado a
   WebP de 1000px queda en 86 KB, unas 140 veces menos, y a la vista es
   el mismo dibujo.

4. **La respuesta se puede borrar pero no editar desde el admin.** Un
   nombre mal escrito lo escribió quien respondió; corregirlo por ellos
   invita a inventar. Borrar y que vuelva a confirmar es más honesto.

## Lo que no entra

- **Cuántos acompañantes trae cada uno.** No se pidió. Si hace falta
  para calcular comida, se agrega después con un campo numérico.
- **Fecha, hora y lugar del evento.** La lámina no los trae y no se
  inventan (ver Pendiente).

## Pendiente

La invitación **no dice cuándo ni dónde**: el centro de la lámina está
vacío. Alguien puede confirmar sin saber a qué se está anotando. Hay que
resolverlo antes de compartir el link, sea reexportando el SVG con los
datos puestos o agregándolos como texto debajo de la imagen.
