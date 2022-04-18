// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import EventDetectionsSummary from "@/components/Events/EventDetectionsSummary.vue";
import router from "@/router/index";

const props = {
  eventUuid: "uuid",
};

describe("EventDetectionsSummary", () => {
  it("renders", () => {
    mount(EventDetectionsSummary, {
      global: {
        plugins: [PrimeVue, createPinia(), router],
      },
      propsData: props,
    });
  });
});