// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import PrimeVue from "primevue/config";

import FilterModal from "@/components/Modals/FilterModal.vue";
import { alertFilterParams } from "@/models/alert";
import { eventFilterParams } from "@/models/event";
import { genericObjectReadFactory } from "@mocks/genericObject";
import { testConfiguration } from "@/etc/configuration/test";

const externalQueue = genericObjectReadFactory({ value: "external" });
const internalQueue = genericObjectReadFactory({ value: "internal" });

function factory(
  args: {
    filters: { alerts: alertFilterParams; events: eventFilterParams };
  } = { filters: { alerts: {}, events: {} } },
) {
  return mount(FilterModal, {
    global: {
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          stubActions: false,
          initialState: {
            currentUserSettingsStore: {
              queues: {
                alerts: externalQueue,
                events: externalQueue,
              },
            },
            filterStore: args.filters,
            queueStore: {
              items: [externalQueue, internalQueue],
            },
          },
        }),
      ],
      provide: {
        nodeType: "alerts",
        rangeFilters: testConfiguration.alerts.alertRangeFilters,
        availableFilters: testConfiguration.alerts.alertFilters,
      },
    },
    propsData: {
      name: "FilterModal",
    },
  }).then((wrapper) => {
    wrapper.vm.modalStore.open("FilterModal");
    cy.get("[data-cy=FilterModal]").should("be.visible");
    cy.findAllByText("Edit Filters").should("be.visible");
    cy.findAllByText("external").should("be.visible"); // queue selector
    cy.findAllByText("Clear").should("be.visible");
    cy.findAllByText("Add").should("be.visible");
    cy.findAllByText("Cancel").should("be.visible");
    cy.findAllByText("Submit").should("be.visible");
  });
}

describe("FilterModal", () => {
  it("renders correctly when no current filters are set", () => {
    factory();
    cy.get('[data-cy="filter-input"]').should("not.exist");
  });
  it("renders correctly when there are current filters are set", () => {
    factory({
      filters: {
        alerts: {
          name: {
            included: ["test name", "test name 2"],
            notIncluded: ["test name 3"],
          },
        },
        events: {},
      },
    });
    cy.get('[data-cy="filter-input"]').should("have.length", 3);
    cy.findAllByText("Name").should("have.length", 3);
    cy.findByDisplayValue("test name").should("be.visible");
    cy.get('[data-cy="filter-not-included-switch"]')
      .eq(0)
      .should("not.be.checked")
      .parent()
      .parent()
      .should("be.visible");
    cy.findByDisplayValue("test name 2").should("be.visible");
    cy.get('[data-cy="filter-not-included-switch"]')
      .eq(1)
      .should("not.be.checked")
      .parent()
      .parent()
      .should("be.visible");
    cy.findByDisplayValue("test name 3").should("be.visible");
    cy.get('[data-cy="filter-not-included-switch"]')
      .eq(2)
      .should("be.checked")
      .parent()
      .parent()
      .should("be.visible");
  });
  it("clears filters in filter form when 'Clear' button clicked", () => {
    factory({
      filters: {
        alerts: { name: { included: ["test name"], notIncluded: [] } },
        events: {},
      },
    });
    cy.get('[data-cy="filter-input"]').should("have.length", 1);
    cy.contains("Clear").click();
    cy.get('[data-cy="filter-input"]').should("not.exist");
  });
  it("closes the modal without doing anything when 'Cancel' button clicked", () => {
    factory();
    cy.contains("Cancel").click();
    cy.get("[data-cy=FilterModal]").should("not.exist");
  });
  it("adds a filter input when the 'Add' button is clicked", () => {
    factory();
    cy.get('[data-cy="filter-input"]').should("not.exist");
    cy.contains("Add").click();
    cy.get('[data-cy="filter-input"]').should("have.length", 1);
    cy.contains("Disposition").should("be.visible");
  });
  it("clears filter store when 'Submit' button is clicked and no filter inputs are in form", () => {
    factory({
      filters: {
        alerts: { name: { included: ["test name"], notIncluded: [] } },
        events: {},
      },
    });
    cy.contains("Clear").click();
    cy.contains("Submit").click();
    cy.get("@spy-5").should("have.been.calledOnceWith", {
      nodeType: "alerts",
    }); //clearAll
    cy.get("[data-cy=FilterModal]").should("not.exist");
  });
  it("updates filter store with filters in form when 'Submit' button is clicked", () => {
    factory({
      filters: {
        alerts: { name: { included: ["test name"], notIncluded: [] } },
        events: {},
      },
    });
    cy.contains("Add").click();
    cy.get('[data-cy="filter-input"]').should("have.length", 2);
    cy.contains("Disposition").click();
    cy.get("[aria-label='Name']").last().click();
    cy.get('[data-cy="property-input-value"]')
      .last()
      .click()
      .type("test value 2");
    cy.get('[data-cy="filter-not-included-switch"]')
      .eq(1)
      .parent()
      .parent()
      .click();
    cy.contains("Submit").click();
    cy.get("@spy-1").should("have.been.calledOnceWith", {
      nodeType: "alerts",
      filters: {
        name: { included: ["test name"], notIncluded: ["test value 2"] },
      },
    }); //bulkSetFilters
    cy.get("[data-cy=FilterModal]").should("not.exist");
  });
});
