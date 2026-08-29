# 005 — Confirmación de asistencia al baby shower

## Por qué

El diseño original de Stitch traía un RSVP y en la tanda 004 se decidió
sacarlo, dejándolo anotado como "spec aparte" si algún día hacía falta.
Hizo falta.

## Qué se construye

1. **Una página propia para la invitación**, con su propio link, donde
   la lámina y el formulario son lo único que hay.
2. **Una pantalla en el admin** para ir viendo quiénes confirmaron.

## Decisiones

1. **Dos links independientes.** La wishlist se pasa solo a quien
   pregunta qué hace falta; la invitación se manda a todos los
   convidados. Con un token compartido, invitar a alguien al shower
   sería mostrarle también la lista de regalos, que no es lo que se
   quiere. Por eso `wishlist_config` guarda dos tokens y ninguno sirve
   para lo del otro.

   Como corolario, los datos del evento salieron de `GET /config`, que
   es público y sin token, y se sirven solo contra `GET /i/{token}`: el
   lugar y la hora no tienen por qué ser consultables sin el link.

2. **Sin identidad, igual que las reservas.** Nadie crea cuenta. El
   envío va con el mismo límite de 10 por minuto que las reservas.

3. **Se acepta que alguien responda dos veces.** El navegador recuerda
   la respuesta en localStorage y muestra lo elegido con opción a
   cambiarlo, pero eso no es un control: basta otro teléfono. Deduplicar
   por nombre obligaría a adivinar si «Ana» y «Ana Pérez» son la misma
   persona, y equivocarse ahí borra la respuesta de alguien. Se prefiere
   que el admin pueda borrar duplicados a mano.

4. **La lámina se rasteriza.** El SVG que llegó de Illustrator pesa
   12,4 MB, y optimizado con svgo sigue en 6,4 MB — inviable para una
   página que se abre desde el celular con datos. Rasterizado a WebP de
   1000px queda en 86 KB, unas 140 veces menos, y a la vista es el mismo
   dibujo.

5. **Lugar, fecha, hora y texto van encima de la lámina, no quemados en
   ella.** El centro del dibujo está vacío a propósito. Se guardan en
   `wishlist_config` y se editan desde Ajustes, así cambiar la hora no
   obliga a reexportar desde Illustrator. Son texto libre y no fecha y
   hora tipadas: se escriben una vez y se leen tal cual («Sábado 15 de
   noviembre», «de 4 a 7 de la tarde»), así que tipar solo agregaría
   problemas de formato y zona horaria sin ganar nada.

6. **El aviso sobre la confirmación va aparte del texto de la lámina.**
   Es una instrucción («confirmá antes del 7 de noviembre, acá o con los
   papás»), no parte del dibujo, así que se muestra encima del
   formulario y no sobre la imagen. Se ve igual antes y después de
   responder: la fecha límite sigue importando si alguien quiere
   cambiar lo que contestó.

7. **La respuesta se puede borrar pero no editar desde el admin.** Un
   nombre mal escrito lo escribió quien respondió; corregirlo por ellos
   invita a inventar. Borrar y que vuelva a confirmar es más honesto.

## Lo que no entra

- **Cuántos acompañantes trae cada uno.** No se pidió. Si hace falta
  para calcular comida, se agrega después con un campo numérico.
- **Un recordatorio o aviso a quien no respondió.** Implicaría guardar
  contactos, que hoy no se piden.

## Pendiente

Cargar los datos del evento desde Ajustes antes de mandar el link. Sin
ellos la invitación se muestra sin fecha ni lugar.
