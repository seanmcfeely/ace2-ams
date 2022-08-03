// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";

import router from "@/router/index";
import { testConfiguration } from "@/etc/configuration/test/index";
import Tooltip from "primevue/tooltip";

import ManageEvents from "@/pages/Events/ManageEvents.vue";
import { userReadFactory } from "@mocks/user";

function factory() {
  mount(ManageEvents, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          initialState: {
            authStore: {
              user: userReadFactory(),
            },
            currentUserSettingsStore: {
              queues: {
                alerts: { value: "external" },
                events: { value: "external" },
              },
            },
          },
        }),
        router,
        ToastService,
      ],
      provide: { config: testConfiguration, objectType: "events" },
    },
  });
}

describe("ManageEvents", () => {
  it("renders", () => {
    factory();
  });
  it("sets filters and reloads if query params are added to route", () => {
    factory();
    cy.get("body").then(() => {
      const route = Cypress.vue.$router;
      route.push("/manage_events?name=test");
    });
    cy.wait(1000);
    cy.get("@stub-1").should("be.calledWith", {
      objectType: "events",
      filters: { name: { included: ["test"], notIncluded: [] } },
    });
  });
});
