// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import router from "@/router/index";
import { testConfiguration } from "@/etc/configuration/test/index";
import ViewEvent from "@/pages/Events/ViewEvent.vue";
import { Event } from "@/services/api/event";
import { useEventStore } from "@/stores/event";
import { eventReadFactory } from "@mocks/events";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { userReadFactory } from "@mocks/user";
import { genericObjectReadFactory } from "@mocks/genericObject";

const factory = (): void => {
  const getStub = cy.stub(Event, "read");
  getStub.as("readEvent").resolves(
    eventReadFactory({
      analysisTypes: ["testAnalysisType"],
      queue: genericObjectReadFactory({ value: "external" }),
    }),
  );

  mount(ViewEvent, {
    global: {
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          stubActions: false,
          initialState: { authStore: { user: userReadFactory() } },
        }),
        router,
      ],
      provide: { config: testConfiguration },
    },
  });
};

describe("ViewEvent", () => {
  it("renders", () => {
    factory();
    cy.get("@readEvent").should("be.calledOnce");
  });
  it("attempts to reload if reloadRequest is set to true", () => {
    factory();
    cy.get("body").then(() => {
      const eventStore = useEventStore();
      eventStore.requestReload = true;
    });
    cy.wait(500);
    cy.get("@readEvent").should("be.calledTwice");
  });
  it("switches section as expected", () => {
    factory();
    cy.contains("Information").click();
    cy.contains("Alert Summary").click();
    cy.get("#event-section-title").should("contain.text", "Alert Summary");
  });
  it("copies link to open event without error", () => {
    factory();
    cy.get('[data-cy="event-details-link"]').click();
  });
});
