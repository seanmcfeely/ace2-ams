<!-- ManageAlerts.vue -->

<template>
  <div class="card">
    <p v-if="isLoggedIn">You're already logged in!</p>
    <p v-else>You need to log in...</p>

    <div class="flex align-items-center justify-content-center">
      <div class="surface-card p-4 shadow-2 border-round w-full lg:w-6">
        <div class="text-center mb-5">
          <div class="text-900 text-3xl font-medium mb-3">Welcome Back :)</div>
        </div>

        <div>
          <label for="username" class="block text-900 font-medium mb-2"
            >Username</label
          >
          <InputText
            id="username"
            type="text"
            class="w-full mb-3"
            v-model="username"
          />

          <label for="password" class="block text-900 font-medium mb-2"
            >Password</label
          >
          <InputText
            id="password"
            type="password"
            class="w-full mb-3"
            v-model="password"
          />

          <Button
            label="Log In"
            icon="pi pi-user"
            class="w-full"
            @click="login"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { mapState, mapGetters, mapActions } from "vuex";

  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import Checkbox from "primevue/checkbox";

  export default {
    components: {
      Button,
      InputText,
      Checkbox,
    },
    computed: {
      loginData() {
        return { username: this.username, password: this.password };
      },
      ...mapState({
        isLoggedIn: (state) => state.auth.loggedIn,
      }),
    },
    data() {
      return {
        username: null,
        password: null,
      };
    },
    methods: {
      async login() {
        await this.$store.dispatch("auth/login", this.loginData);
        this.resetData();
      },
      resetData() {
        (this.username = null), (this.password = null);
      },
    },
  };
</script>
