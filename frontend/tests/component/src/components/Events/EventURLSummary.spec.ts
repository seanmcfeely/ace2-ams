import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import { testConfiguration } from "@/etc/configuration/test/index";
import EventURLSummary from "@/components/Events/EventURLSummary.vue";
import router from "@/router/index";
import { Alert } from "@/services/api/alert";
import { observableReadFactory } from "@mocks/observable";
import { genericObjectReadFactory } from "@mocks/genericObject";

const props = {
  eventAlertUuids: ["uuidA"],
};

function factory() {
  return mount(EventURLSummary, {
    global: {
      plugins: [PrimeVue, createPinia(), router],
      provide: { config: testConfiguration },
    },
    propsData: props,
  });
}

describe("EventURLSummary", () => {
  it("renders correctly when request to fetch URLs successfully returns results", () => {
    cy.stub(Alert, "readObservables")
      .withArgs(props.eventAlertUuids)
      .returns([
        observableReadFactory(),
        observableReadFactory({
          value: "www.microsoft.com",
          type: genericObjectReadFactory({ value: "url" }),
        }),
        observableReadFactory({
          value: "www.amazon.com",
          type: genericObjectReadFactory({ value: "url" }),
        }),
        observableReadFactory({
          value: "www.google.com",
          type: genericObjectReadFactory({ value: "url" }),
        }),
      ]);
    factory();
    cy.findByRole("listbox").children().should("have.length", 3);
    cy.findByRole("listbox")
      .children()
      .eq(0)
      .should("have.text", "www.amazon.com");
    cy.findByRole("listbox")
      .children()
      .eq(1)
      .should("have.text", "www.google.com");
    cy.findByRole("listbox")
      .children()
      .eq(2)
      .should("have.text", "www.microsoft.com");
    cy.findByRole("listbox").children().eq(0).click(); // test copy to clipboard doesn't error
  });
  it("renders correctly when request to fetch URLs successfully returns empty", () => {
    cy.stub(Alert, "readObservables")
      .withArgs(props.eventAlertUuids)
      .returns([]);
    factory();
    cy.findByRole("listbox").should(
      "contain.text",
      "This event doesn't have any URL observables.",
    );
  });
  it("renders correctly when request to fetch URLs fails with an error string", () => {
    cy.stub(Alert, "readObservables")
      .withArgs(props.eventAlertUuids)
      .callsFake(async () => {
        throw "404 request failed";
      });
    factory();
    cy.get("[data-cy=error-banner]").should(
      "contain.text",
      "404 request failed",
    );
    cy.findByRole("listbox").should(
      "contain.text",
      "This event doesn't have any URL observables.",
    );
  });
  it("renders correctly when request to fetch URLs fails with an Error", () => {
    cy.stub(Alert, "readObservables")
      .withArgs(props.eventAlertUuids)
      .rejects(new Error("404 request failed"));
    factory();
    cy.get("[data-cy=error-banner]").should(
      "contain.text",
      "404 request failed",
    );
    cy.findByRole("listbox").should(
      "contain.text",
      "This event doesn't have any URL observables.",
    );
  });
});
