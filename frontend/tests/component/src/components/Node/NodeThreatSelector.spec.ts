import { mount } from "@cypress/vue";
import PrimeVue from "primevue/config";

import NodeThreatSelector from "@/components/Node/NodeThreatSelector.vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { nodeThreatRead } from "@/models/nodeThreat";
import { queueableObjectReadFactory } from "@mocks/genericObject";
import Tooltip from "primevue/tooltip";
import ToastService from "primevue/toastservice";
import { NodeThreat } from "@/services/api/nodeThreat";

function factory(
  args: {
    modelValue: nodeThreatRead[];
    queue: string;
    initialState: Record<string, unknown>;
    stubActions: boolean;
  } = {
    modelValue: [],
    queue: "external",
    initialState: {},
    stubActions: true,
  },
) {
  return mount(NodeThreatSelector, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        PrimeVue,
        ToastService,
        createCustomCypressPinia({
          initialState: args.initialState,
          stubActions: args.stubActions,
        }),
      ],
    },
    propsData: {
      modelValue: args.modelValue,
      queue: args.queue,
    },
  });
}

const threatTypeA = queueableObjectReadFactory({
  value: "threat type A",
});
const threatTypeB = queueableObjectReadFactory({
  value: "threat type B",
});

const threatA: nodeThreatRead = {
  types: [threatTypeA],
  ...queueableObjectReadFactory({
    value: "threat A",
  }),
};
const threatB: nodeThreatRead = {
  types: [threatTypeB],
  ...queueableObjectReadFactory({
    value: "threat B",
  }),
};

describe("NodeThreatSelector", () => {
  it("renders when there are no available threat options", () => {
    factory();
    cy.contains("No available options").should("be.visible");
    cy.contains("New").should("be.visible");
  });
  it("renders when there are threat options, but none selected", () => {
    factory({
      modelValue: [],
      queue: "external",

      initialState: {
        nodeThreatStore: { items: [threatA] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.contains("threat A")
      .should("be.visible")
      .parent()
      .parent()
      .invoke("attr", "aria-selected")
      .should("eq", "false");
    cy.contains("New").should("be.visible");
  });
  it("renders when there are threat options with 1 or more selected", () => {
    factory({
      modelValue: [threatB],
      queue: "external",

      initialState: {
        nodeThreatStore: { items: [threatA, threatB] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.contains("threat A")
      .should("be.visible")
      .parent()
      .parent()
      .invoke("attr", "aria-selected")
      .should("eq", "false");
    cy.contains("threat B")
      .should("be.visible")
      .parent()
      .parent()
      .invoke("attr", "aria-selected")
      .should("eq", "true");
    cy.contains("New").should("be.visible");
  });
  it("renders new threat panel correctly when no threat type options are available", () => {
    factory();
    cy.contains("New").click();
    cy.get('[data-cy="edit-threat-panel"]').should("be.visible");
    cy.findByPlaceholderText("My new threat").should("be.visible");
    cy.get('[data-cy="threat-types"]').should("be.visible").click();
    cy.findAllByText("No available options").should("have.length", 2);
  });
  it("correctly attempts to request new threat creation if name and threat type are provided", () => {
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatStore: { items: [threatA, threatB] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.contains("New").click();
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.findByPlaceholderText("My new threat").click().type("Test threat");
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type A").click();
    cy.get('[data-cy="save-threat-button"]').click();
    cy.get("@stub-1").should("have.been.calledWith", {
      value: "Test threat",
      queues: ["external"],
      types: ["threat type A"],
    });
  });
  it("will not request to create new threat if new threat panel is closed without saving", () => {
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatStore: { items: [threatA, threatB] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.contains("New").click();
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.findByPlaceholderText("My new threat").click().type("Test threat");
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type A").click();
    cy.get('[data-cy="close-edit-threat-panel-button"]').click();
    cy.get("@stub-1").should("not.have.been.called");
  });
  it("will correctly display an error message if attempt to create a new threat fails", () => {
    cy.stub(NodeThreat, "readAll").resolves([threatA, threatB]);
    cy.stub(NodeThreat, "create").rejects(new Error("404 request failed"));
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: false,
    });
    cy.contains("New").click();
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.findByPlaceholderText("My new threat").click().type("Test threat");
    cy.get('[data-cy="save-threat-button"]').should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type A").click();
    cy.get('[data-cy="save-threat-button"]').click();
    cy.contains("Action Failed").should("be.visible");
    cy.contains("404 request failed").should("be.visible");
    cy.get('[data-cy="edit-threat-panel"]').should("not.exist");
  });
  it("correctly attempts to request threat type update if existing threat types are changed", () => {
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatStore: { items: [threatA, threatB] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.get('[data-cy="edit-threat-button"]').first().click();
    cy.get('[data-cy="save-threat-button"]').should("not.be.disabled");
    cy.findByDisplayValue("threat A").should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type B").click();
    cy.get('[data-cy="save-threat-button"]').click();
    cy.get("@stub-3").should("have.been.calledWith", "testObject1", {
      types: ["threat type A", "threat type B"],
    });
  });
  it("will not request to edit existing threat's threat types if edit threat panel is closed without saving", () => {
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatStore: { items: [threatA, threatB] },
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: true,
    });
    cy.get('[data-cy="edit-threat-button"]').first().click();
    cy.get('[data-cy="save-threat-button"]').should("not.be.disabled");
    cy.findByDisplayValue("threat A").should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type B").click();
    cy.get('[data-cy="close-edit-threat-panel-button"]').click();
    cy.get("@stub-3").should("not.have.been.called");
  });
  it("will correctly display an error message if attempt to edit a threat's threat types fails", () => {
    cy.stub(NodeThreat, "readAll").resolves([threatA, threatB]);
    cy.stub(NodeThreat, "update").rejects(new Error("404 request failed"));
    factory({
      modelValue: [],
      queue: "external",
      initialState: {
        nodeThreatTypeStore: { items: [threatTypeA, threatTypeB] },
      },
      stubActions: false,
    });
    cy.get('[data-cy="edit-threat-button"]').first().click();
    cy.get('[data-cy="save-threat-button"]').should("not.be.disabled");
    cy.findByDisplayValue("threat A").should("be.disabled");
    cy.get('[data-cy="threat-types"]').click();
    cy.contains("threat type B").click();
    cy.get('[data-cy="save-threat-button"]').click();
    cy.contains("Action Failed").should("be.visible");
    cy.contains("404 request failed").should("be.visible");
    cy.get('[data-cy="edit-threat-panel"]').should("not.exist");
  });
});
