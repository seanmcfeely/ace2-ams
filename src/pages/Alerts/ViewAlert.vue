<!-- ManageAlerts.vue -->

<template>
  <pre>{{ prettyAlert }}</pre>
</template>

<script>
  import { mapGetters } from "vuex";

  export default {
    computed: {
      lastObservableIndex() {
        return this.observables.length - 1;
      },
      ...mapGetters({
        openAlert: "alerts/openAlert",
      }),
      prettyAlert() {
        return JSON.stringify(this.openAlert, null, 2);
      },
    },
    async created() {
      console.log(this.openAlert);
      console.log(this.$route.params);
      await this.$store.dispatch(
        "alerts/openAlert",
        this.$route.params.alertID,
      );
    },
  };
</script>
