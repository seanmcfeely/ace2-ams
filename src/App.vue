<!-- App.vue -->
<!-- Main Entrypoint to the app -->

<template>
  <TheHeader />
  <router-view />
</template>

<script>
  import TheHeader from "@/components/UserInterface/TheHeader";
  import auth from "@/services/api/auth";

  export default {
    components: { TheHeader },

    created() {
      setInterval(() => {
        if (this.$route.name !== "Login") {
          auth.validate().catch(() => {
            console.debug("redirecting to login page");
            this.$router.replace({ name: "Login" });
          });
        }
      }, 60000);
    },
  };
</script>

<style lang="scss">
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
  }

  #nav {
    padding: 30px;

    a {
      font-weight: bold;
      color: #2c3e50;

      &.router-link-exact-active {
        color: #42b983;
      }
    }
  }
</style>
