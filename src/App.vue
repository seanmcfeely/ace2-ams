<!-- App.vue -->
<!-- Main Entrypoint to the app -->

<template>
  <TheHeader />
  <router-view />
</template>

<script>
  import TheHeader from "@/components/UserInterface/TheHeader";
  export default {
    components: { TheHeader },
  };
</script>
