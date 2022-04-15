// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createPinia } from "pinia";

import PrimeVue from "primevue/config";

import { testConfiguration } from "@/etc/configuration/test/index";
import EventURLDomainSummary from "@/components/Events/EventURLDomainSummary.vue";
import router from "@/router/index";
import { Event } from "@/services/api/event";

const props = {
  eventUuid: "uuid",
};

function factory() {
  return mount(EventURLDomainSummary, {
    global: {
      plugins: [PrimeVue, createPinia(), router],
      provide: { config: testConfiguration },
    },
    propsData: props,
  });
}

describe("EventURLDomainSummary", () => {
  it("renders correctly when request to fetch data fails", () => {
    cy.stub(Event, "readUrlDomainSummary")
      .withArgs("uuid")
      .rejects(new Error("404 Request failed"));
    factory();
    cy.get("[data-cy=error-banner]")
      .should("be.visible")
      .should("contain.text", "404 Request failed");
    cy.get("canvas").should("not.exist");
    cy.contains("URL Domain Summary results empty.").should("be.visible");
  });
  it("renders correctly when request to fetch data successfully returns empty", () => {
    cy.stub(Event, "readUrlDomainSummary")
      .withArgs("uuid")
      .returns({ domains: [] });
    factory();
    cy.get("canvas").should("not.exist");
    cy.contains("URL Domain Summary results empty.").should("be.visible");
  });
  it("renders correctly when request to fetch data successfully returns results", () => {
    cy.stub(Event, "readUrlDomainSummary")
      .withArgs("uuid")
      .returns({
        domains: [
          { domain: "google.com", count: 10 },
          { domain: "youtube.com", count: 5 },
        ],
      });
    factory();
    cy.get("canvas").should("be.visible");
    cy.findByRole("table").should("be.visible");
    cy.get("tr").should("have.length", 3);
    cy.get("tr").eq(0).children().eq(0).should("contain.text", "Domain");
    cy.get("tr").eq(0).children().eq(1).should("contain.text", "Count");
    cy.get("tr").eq(1).children().eq(0).should("contain.text", "google.com");
    cy.get("tr").eq(1).children().eq(1).should("contain.text", "10");
    cy.get("tr").eq(2).children().eq(0).should("contain.text", "youtube.com");
    cy.get("tr").eq(2).children().eq(1).should("contain.text", "5");
  });
});
