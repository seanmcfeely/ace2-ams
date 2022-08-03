// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import PrimeVue from "primevue/config";

import router from "@/router/index";
import { testConfiguration } from "@/etc/configuration/test/index";
import Tooltip from "primevue/tooltip";
import ToastService from "primevue/toastservice";

import ManageAlerts from "@/pages/Alerts/ManageAlerts.vue";
import { userReadFactory } from "@mocks/user";

const factory = () => {
  mount(ManageAlerts, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        ToastService,
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
      ],
      provide: { config: testConfiguration, objectType: "alerts" },
    },
  });
};

describe("ManageAlerts", () => {
  it("renders", () => {
    factory();
  });
  it("sets filters and reloads if query params are added to route", () => {
    factory();
    cy.get("body").then(() => {
      const route = Cypress.vue.$router;
      route.push("/manage_alerts?name=test");
    });
    cy.wait(1000);
    cy.get("@stub-1").should("be.calledWith", {
      objectType: "alerts",
      filters: { name: { included: ["test"], notIncluded: [] } },
    });
  });
});
