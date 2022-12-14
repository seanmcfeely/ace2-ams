<!-- App.vue -->
<!-- Main Entrypoint to the app -->

<template>
  <TheHeader style="position: sticky; top: 0; z-index: 1" />
  <router-view />
</template>

<script setup>
  import { onBeforeMount, provide } from "vue";
  import { useRoute, useRouter } from "vue-router";

  import { populateCommonStores } from "@/stores/helpers";
  import TheHeader from "@/components/UserInterface/TheHeader.vue";
  import authApi from "@/services/api/auth";
  import { useAuthStore } from "@/stores/auth";

  import { configuration } from "@/etc/configuration/index";
  import { testConfiguration } from "@/etc/configuration/test/index";

  const testingModeEnabled = import.meta.env.VITE_TESTING_MODE;
  /* istanbul ignore next */
  const config =
    testingModeEnabled === "yes" ? testConfiguration : configuration;

  provide("config", config);

  const authStore = useAuthStore();

  onBeforeMount(async () => {
    const route = useRoute();
    const router = useRouter();

    // Create a 60s interval to check if the user is still authenticated.
    // If they are not authenticated, kick them back to the Login page.
    setInterval(async () => {
      if (route.name !== "Login") {
        await authApi.validate().catch(() => {
          console.debug("redirecting to login page");
          router.replace({ name: "Login" });
        });
      }
    }, 60000);

    // If the user is authenticated, load their most recent filters from
    // localStorage and populate some of the stores with items from
    // the API that will be used throughout the application.
    if (authStore.isAuthenticated) {
      await populateCommonStores();
    }
  });
</script>
