import { mount } from "@cypress/vue";

import PrimeVue from "primevue/config";

import AnalyzeAlertForm from "@/components/Alerts/AnalyzeAlertForm.vue";
import router from "@/router/index";
import Tooltip from "primevue/tooltip";

import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { genericObjectReadFactory } from "@mocks/genericObject";
import { userReadFactory } from "@mocks/user";
import { alertReadFactory } from "@mocks/alert";
import { Alert } from "@/services/api/alert";
import { TestingOptions } from "@pinia/testing";
import { testConfiguration } from "@/etc/configuration/test/index";

const testAlertTypeA = "testAlertTypeA";
const testAlertTypeB = "testAlertTypeB";
const testQueueA = "testQueueA";
const testQueueB = "testQueueB";
const testObservableTypeA = "file";
const testObservableTypeB = "ipv4";
const testNodeDirective = "testNodeDirective";

const testTime = new Date(Date.UTC(2022, 2, 29, 12, 0, 0, 0)).getTime();

const initialState = {
  alertTypeStore: {
    items: [
      genericObjectReadFactory({ value: testAlertTypeA }),
      genericObjectReadFactory({ value: testAlertTypeB }),
    ],
  },
  authStore: {
    user: userReadFactory({
      defaultAlertQueue: genericObjectReadFactory({ value: testQueueA }),
    }),
  },
  nodeDirectiveStore: {
    items: [genericObjectReadFactory({ value: testNodeDirective })],
  },
  observableTypeStore: {
    items: [
      genericObjectReadFactory({ value: testObservableTypeA }),
      genericObjectReadFactory({ value: testObservableTypeB }),
    ],
  },
  queueStore: {
    items: [
      genericObjectReadFactory({ value: testQueueA }),
      genericObjectReadFactory({ value: testQueueB }),
    ],
  },
};

function factory(options: TestingOptions = {}) {
  return mount(AnalyzeAlertForm, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        createCustomCypressPinia({ ...options, initialState: initialState }),
        PrimeVue,
        router,
      ],
      provide: { config: testConfiguration },
    },
  });
}

describe("AnalyzeAlertForm Setup", () => {
  it("renders all components as expected", () => {
    factory();
    cy.findByRole("tab").contains("Basic");
    cy.get("div").contains("Alert Details");
    cy.get("div").contains("Advanced");
    cy.get("div").contains("Observables");
    cy.get("button").contains("Analyze!");
  });
});

describe("AnalyzeAlertForm - Advanced Panel", () => {
  it("opens and closes the Advanced details panel when 'Advanced' expander clicked", () => {
    factory();
    // Click to open advanced panel
    cy.get("div").contains("Advanced").click();
    // Should have additional visible inputs
    cy.contains("Alert Datetime").should("be.visible");
    cy.contains("Alert Type").should("be.visible");
    cy.contains("Queue").should("be.visible");

    // Close and the inputs should no longer be visible
    cy.get("div").contains("Advanced").click();
    cy.contains("Alert Datetime").should("not.be.visible");
    cy.contains("Alert Type").should("not.be.visible");
    cy.contains("Queue").should("not.be.visible");
  });
  it("autofills details panel options with correct values", () => {
    cy.clock(testTime);
    factory();
    // Click to open advanced panel
    cy.get("div").contains("Advanced").click();
    // Should have additional visible inputs
    cy.get('[data-cy="alert-date"]').should("have.value", "03/29/2022 12:00");
    cy.get("#timezone").should("not.be.empty");
    cy.get("#type").should("have.text", "testAlertTypeA");
    cy.get("#queue").should("have.text", "testQueueA");
  });
});

const testObservableValueA = "1.2.3.4";
const testObservableValueB = "5.6.7.8";
const testObservableValueMultiA = "4.3.2.1,8.7.6.5";

const expectedCreateAlert = {
  owner: "analyst",
  queue: "testQueueA",
  type: "testAlertTypeA",
  eventTime: new Date("2022-03-29T12:00:00"),
};

describe("AnalyzeAlertForm - Form submission", () => {
  it("correctly creates an alert with all 'single'-type observables", () => {
    cy.clock(testTime);

    const stub = cy.stub(Alert, "createAndRead");
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert",
        name: "Manual Alert",
        observables: [
          { type: "ipv4", value: testObservableValueA },
          { type: "ipv4", value: testObservableValueB },
        ],
      })
      .as("CreateAlertA")
      .resolves(alertReadFactory({ uuid: "alertA" }));

    factory({ stubActions: false });

    // Add first observable
    cy.get("[name=observable-type]").click();
    cy.get('[aria-label="ipv4"]').click();
    cy.get("[name=observable-value] input").type(testObservableValueA);

    // Add second observable
    cy.get("#add-observable").click();
    cy.get("[name=observable-type]").eq(1).click();
    cy.get('[aria-label="ipv4"]').eq(1).click();
    cy.get("[name=observable-value] input").eq(1).type(testObservableValueB);

    // Submit
    cy.contains("Analyze!").eq(0).click();
    cy.get("@CreateAlertA").should("have.been.called");

    // Should route to last created alert
    cy.url().should("contain", "alertA");
  });
  it("correctly creates an alert with observables with directives attached", () => {
    cy.clock(testTime);

    const stub = cy.stub(Alert, "createAndRead");
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert",
        name: "Manual Alert",
        observables: [
          {
            type: "ipv4",
            value: testObservableValueA,
            directives: ["testNodeDirective"],
          },
        ],
      })
      .as("CreateAlertA")
      .resolves(alertReadFactory({ uuid: "alertA" }));

    factory({ stubActions: false });

    // Add first observable
    cy.get("[name=observable-type]").click();
    cy.get('[aria-label="ipv4"]').click();
    cy.get("[name=observable-value] input").type(testObservableValueA);
    cy.contains("No directives selected").click();
    cy.contains("testNodeDirective").click();

    // Submit
    cy.contains("Analyze!").eq(0).click();
    cy.get("@CreateAlertA").should("have.been.called");

    // Should route to last created alert
    cy.url().should("contain", "alertA");
  });
  it("correctly creates an alert with 'multi'-type observables", () => {
    cy.clock(testTime);

    const stub = cy.stub(Alert, "createAndRead");
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert",
        name: "Manual Alert",
        observables: [
          { type: "ipv4", value: "4.3.2.1" },
          { type: "ipv4", value: "8.7.6.5" },
        ],
      })
      .as("CreateAlertA")
      .resolves(alertReadFactory({ uuid: "alertA" }));

    factory({ stubActions: false });

    // Add first observable
    cy.get("[name=observable-type]").click();
    cy.get('[aria-label="ipv4"]').click();

    // Switch to multi-type and enter input
    cy.get("[name=observable-value] button").click();
    cy.get("[name=observable-value] textarea").type(testObservableValueMultiA);

    // Submit
    cy.contains("Analyze!").eq(0).click();

    cy.get("@CreateAlertA").should("have.been.called");

    // Should route to last created alert
    cy.url().should("contain", "alertA");
  });
  it("correctly creates multiple alerts with all 'single'-type observables", () => {
    cy.clock(testTime);

    const stub = cy.stub(Alert, "createAndRead");
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert 1.2.3.4",
        name: "Manual Alert 1.2.3.4",
        observables: [{ type: "ipv4", value: testObservableValueA }],
      })
      .as("CreateAlertA")
      .resolves(alertReadFactory({ uuid: "alertA" }));
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert 5.6.7.8",
        name: "Manual Alert 5.6.7.8",
        observables: [{ type: "ipv4", value: testObservableValueB }],
      })
      .as("CreateAlertB")
      .resolves(alertReadFactory({ uuid: "alertB" }));

    factory({ stubActions: false });

    // Add first observable
    cy.get("[name=observable-type]").click();
    cy.get('[aria-label="ipv4"]').click();
    cy.get("[name=observable-value] input").type(testObservableValueA);

    // Add second observable
    cy.get("#add-observable").click();
    cy.get("[name=observable-type]").eq(1).click();
    cy.get('[aria-label="ipv4"]').eq(1).click();
    cy.get("[name=observable-value] input").eq(1).type(testObservableValueB);

    // Submit using multi-add
    cy.get(".p-splitbutton > .p-button-icon-only").click();
    cy.contains("Create multiple alerts").click();

    cy.get("@CreateAlertA").should("have.been.called");
    cy.get("@CreateAlertB").should("have.been.called");

    // Should route to last created alert
    cy.url().should("contain", "alertB");
  });
  it("correctly creates multiple alerts with 'multi'-type observables", () => {
    cy.clock(testTime);

    const stub = cy.stub(Alert, "createAndRead");
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert 1.2.3.4",
        name: "Manual Alert 1.2.3.4",
        observables: [{ type: "ipv4", value: testObservableValueA }],
      })
      .as("CreateAlertA")
      .resolves(alertReadFactory({ uuid: "alertA" }));
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert 4.3.2.1",
        name: "Manual Alert 4.3.2.1",
        observables: [{ type: "ipv4", value: "4.3.2.1" }],
      })
      .as("CreateAlertB")
      .resolves(alertReadFactory({ uuid: "alertB" }));
    stub
      .withArgs({
        ...expectedCreateAlert,
        alert: true,
        alertDescription: "Manual Alert 8.7.6.5",
        name: "Manual Alert 8.7.6.5",
        observables: [{ type: "ipv4", value: "8.7.6.5" }],
      })
      .as("CreateAlertC")
      .resolves(alertReadFactory({ uuid: "alertC" }));

    factory({ stubActions: false });

    // Add first observable
    cy.get("[name=observable-type]").click();
    cy.get('[aria-label="ipv4"]').click();
    cy.get("[name=observable-value] input").type(testObservableValueA);

    // Add second observable(s)
    cy.get("#add-observable").click();
    cy.get("[name=observable-type]").eq(1).click();
    cy.get('[aria-label="ipv4"]').eq(1).click();
    // toggle to multi-add
    cy.get("[name=observable-value] button").eq(1).click();
    cy.get("[name=observable-value] textarea").type(testObservableValueMultiA);

    // Submit using multi-add
    cy.get(".p-splitbutton > .p-button-icon-only").click();
    cy.contains("Create multiple alerts").click();

    cy.get("@CreateAlertA").should("have.been.called");
    cy.get("@CreateAlertB").should("have.been.called");
    cy.get("@CreateAlertC").should("have.been.called");

    // Should route to last created alert, which will end up being B
    cy.url().should("contain", "alertC");
  });
  it("correctly displays errors if alert creation fails", () => {
    factory();
  });
});
