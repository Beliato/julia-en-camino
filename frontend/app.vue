<template>
  <!-- Salto al contenido: el hero de la wishlist ocupa una pantalla
       entera, así que con teclado había que tabular todo eso antes de
       llegar a la lista. Solo aparece al enfocarlo. -->
  <a
    href="#contenido"
    class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-pink-600 focus:px-4 focus:py-2 focus:text-white"
  >
    Saltar al contenido
  </a>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
