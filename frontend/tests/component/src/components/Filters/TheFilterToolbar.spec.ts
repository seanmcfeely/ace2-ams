import { createCustomCypressPinia } from "@tests/cypressHelpers";

import PrimeVue from "primevue/config";
import { testConfiguration } from "@/etc/configuration/test/index";
import Tooltip from "primevue/tooltip";

import TheFilterToolbar from "@/components/Filters/TheFilterToolbar.vue";
import router from "@/router/index";
import { mount } from "@cypress/vue";
import { alertFilterParams } from "@/models/alert";
import { eventFilterParams } from "@/models/event";
import FilterChipContainerVue from "@/components/Filters/FilterChipContainer.vue";
import DateRangePickerVue from "@/components/UserInterface/DateRangePicker.vue";
import { genericObjectReadFactory } from "@mocks/genericObject";
import { userReadFactory } from "@mocks/user";
import { eventStatusRead } from "@/models/eventStatus";
import { genericObjectRead } from "@/models/base";
import { queueRead } from "@/models/queue";

const user = userReadFactory();
const externalQueue = genericObjectReadFactory({ value: "external" });

function factory(
  filters: { alerts: alertFilterParams; events: eventFilterParams } = {
    alerts: {},
    events: {},
  },
  filterType = "alerts",
  eventOpentStatusItems: eventStatusRead[] = [],
  currentUserSettingsStore = {
    queues: {
      alerts: externalQueue,
      events: externalQueue,
    },
  },
) {
  return mount(TheFilterToolbar, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          initialState: {
            authStore: { user: user },
            currentUserSettingsStore: currentUserSettingsStore,
            filterStore: filters,
            alertDispositionStore: {
              items: [genericObjectReadFactory()],
            },
            eventStatusStore: {
              items: eventOpentStatusItems,
            },
          },
        }),
        router,
      ],
      provide: {
        objectType: filterType,
        rangeFilters: testConfiguration.alerts.alertRangeFilters,
        availableFilters: testConfiguration.alerts.alertFilters,
      },
    },
  });
}
// Nothing will show because there is no queue set to decide the available columns
describe("TheFilterToolbar", () => {
  it("renders as expected when no filters are applied", () => {
    factory().then((wrapper) => {
      cy.contains("Quick Add").should("be.visible");
      cy.wrap(wrapper.findComponent(FilterChipContainerVue)).should("exist");
      cy.wrap(wrapper.findComponent(DateRangePickerVue)).should("exist");
    });
  });
  it("renders as expected when there are filters applied", () => {
    factory({
      alerts: {
        name: { included: ["test name"], notIncluded: [] },
        eventTimeAfter: {
          included: [new Date(2022, 4, 22, 12, 0, 0)],
          notIncluded: [],
        },
        eventTimeBefore: {
          included: [new Date(2022, 4, 23, 12, 0, 0)],
          notIncluded: [],
        },
      },
      events: {},
    });
    cy.contains("Name:").should("be.visible");
    cy.contains("test name").should("be.visible");
    cy.contains("2022-05-22T16:00:00").should("be.visible"); // filter chip
    cy.contains("2022-05-23T16:00:00").should("be.visible"); // filter chip
    cy.findByDisplayValue("05/22/2022 16:00:00").should("be.visible"); // date range picker
    cy.findByDisplayValue("05/23/2022 16:00:00").should("be.visible"); // date range picker
  });
  it("opens quick add panel when quick add filter button clicked", () => {
    factory();
    cy.contains("Quick Add").click();
    cy.get('[data-cy="quick-add-filter-panel"]').should("be.visible");
    cy.get('[data-cy="filter-input"]').should("be.visible");
    cy.get('[data-cy="quick-add-filter-submit-button"]').should("be.visible");
  });
  it("correctly attempts to add an included filter when submit button clicked in quick add panel ", () => {
    factory();
    cy.contains("Quick Add").click();
    cy.get('[data-cy="quick-add-filter-panel"]').should("be.visible");
    cy.get('[data-cy="quick-add-filter-submit-button"]').click();
    cy.get("@stub-2").should("have.been.calledOnceWith", {
      objectType: "alerts",
      filterName: "disposition",
      filterValue: { value: "None" },
      isIncluded: true,
    }); // set filter
    cy.get('[data-cy="quick-add-filter-panel"]').should("not.exist");
  });
  it("correctly attempts to add a not included filter when submit button clicked in quick add panel ", () => {
    factory();
    cy.contains("Quick Add").click();
    cy.get('[data-cy="quick-add-filter-panel"]').should("be.visible");
    cy.get('[data-cy="filter-not-included-switch"]').parent().parent().click();
    cy.get('[data-cy="quick-add-filter-submit-button"]').click();
    cy.get("@stub-2").should("have.been.calledOnceWith", {
      objectType: "alerts",
      filterName: "disposition",
      filterValue: { value: "None" },
      isIncluded: false,
    }); // set filter
    cy.get('[data-cy="quick-add-filter-panel"]').should("not.exist");
  });
  it("opens the edit modal when 'Edit' button clicked in filter menu dropdown", () => {
    factory();
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Edit").click();
    cy.get("@stub-7").should("have.been.calledOnceWith", "EditFilterModal"); // Open modal
  });
  it("resets filters when 'Reset' button clicked in filter menu dropdown", () => {
    factory();
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Reset").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "alerts",
    }); // clear all
    cy.get("@stub-1").should("have.been.calledOnceWith", {
      objectType: "alerts",
      filters: {
        disposition: {
          included: [
            {
              value: "None",
            },
          ],
          notIncluded: [],
        },
        owner: {
          included: [
            user,
            {
              username: "none",
              displayName: "None",
            },
          ],
          notIncluded: [],
        },
        queue: {
          included: [externalQueue],
          notIncluded: [],
        },
      },
    }); // set filters to defaults
  });
  it("resets filters when 'Reset' button clicked in filter menu dropdown and currentUserSettingsStore is empty", () => {
    factory(
      {
        alerts: {},
        events: {},
      },
      "alerts",
      [],
      {
        queues: {
          alerts: null as unknown as queueRead,
          events: null as unknown as queueRead,
        },
      },
    );
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Reset").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "alerts",
    }); // clear all
    cy.get("@stub-1").should("have.been.calledOnceWith", {
      objectType: "alerts",
      filters: {
        disposition: {
          included: [
            {
              value: "None",
            },
          ],
          notIncluded: [],
        },
        owner: {
          included: [
            user,
            {
              username: "none",
              displayName: "None",
            },
          ],
          notIncluded: [],
        },
        queue: {
          included: [externalQueue],
          notIncluded: [],
        },
      },
    }); // set filters to defaults
  });
  it("resets filters when 'Reset' button clicked in filter menu dropdown when filterType is events", () => {
    factory(
      {
        alerts: {},
        events: {},
      },
      "events",
    );
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Reset").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "events",
    }); // clear all
    cy.get("@stub-1").should("have.been.calledOnceWith", {
      objectType: "events",
      filters: {
        queue: {
          included: [externalQueue],
          notIncluded: [],
        },
      },
    }); // set filters to defaults
  });
  it("resets filters when 'Reset' button clicked in filter menu dropdown when filterType is events and currentUserSettingsStore is empty", () => {
    factory(
      {
        alerts: {},
        events: {},
      },
      "events",
      [],
      {
        queues: {
          alerts: null as unknown as queueRead,
          events: null as unknown as queueRead,
        },
      },
    );
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Reset").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "events",
    }); // clear all
    cy.get("@stub-1").should("have.been.calledOnceWith", {
      objectType: "events",
      filters: {
        queue: {
          included: [externalQueue],
          notIncluded: [],
        },
      },
    }); // set filters to defaults
  });
  it("resets filters when 'Reset' button clicked in filter menu dropdown when filterType is events and openStatus is available", () => {
    const openEventStatus = {
      ...genericObjectReadFactory({ value: "OPEN" }),
      queues: [],
    };
    factory(
      {
        alerts: {},
        events: {},
      },
      "events",
      [openEventStatus],
    );
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Reset").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "events",
    }); // clear all
    cy.get("@stub-1").should("have.been.calledOnceWith", {
      objectType: "events",
      filters: {
        status: {
          included: [openEventStatus],
          notIncluded: [],
        },
        queue: {
          included: [externalQueue],
          notIncluded: [],
        },
      },
    }); // set filters to defaults
  });
  it("clears filters when 'Clear All' button clicked in filter menu dropdown", () => {
    factory();
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Clear All").click();
    cy.get("@stub-5").should("have.been.calledOnceWith", {
      objectType: "alerts",
    }); // clear all
  });
  it("does not throw error when 'Copy Link' clicked", () => {
    factory({
      alerts: {
        name: { included: ["test name"], notIncluded: [] },
      },
      events: {},
    });
    cy.get('[data-cy="edit-filter-button"]').siblings().click();
    cy.contains("Copy Link").click();
  });
});
