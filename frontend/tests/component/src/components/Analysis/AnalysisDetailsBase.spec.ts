import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import AnalysisDetailsBase from "@/components/Analysis/AnalysisDetailsBase.vue";
import router from "@/router/index";

describe("AnalysisDetailsBase", () => {
  it("renders", () => {
    mount(AnalysisDetailsBase, {
      global: {
        plugins: [PrimeVue, createPinia(), router],
      },
    });

    cy.contains("Basic Analysis").should("be.visible");
  });
});
