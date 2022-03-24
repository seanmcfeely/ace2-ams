// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import AnalyzeAlertForm from "@/components/Alerts/AnalyzeAlertForm.vue";
import router from "@/router/index";

describe("AnalyzeAlertForm", () => {
  it("renders", () => {
    mount(AnalyzeAlertForm, {
      global: {
        plugins: [PrimeVue, createPinia(), router],
      },
    });
  });
});
