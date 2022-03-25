// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import { testConfiguration } from "@/etc/configuration/test/index";
import EventObservableSummary from "@/components/Events/EventObservableSummary.vue";
import router from "@/router/index";

const props = {
  eventUuid: "uuid",
};

describe("EventObservableSummary", () => {
  it("renders", () => {
    mount(EventObservableSummary, {
      global: {
        plugins: [PrimeVue, createPinia(), router],
        provide: { config: testConfiguration },
      },
      propsData: props,
    });
  });
});
