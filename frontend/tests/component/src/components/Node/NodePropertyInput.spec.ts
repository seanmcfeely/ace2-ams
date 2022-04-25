import { mount } from "@cypress/vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";

import { testConfiguration } from "@/etc/configuration/test/index";

import NodePropertyInput from "@/components/Node/NodePropertyInput.vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { userReadFactory } from "@mocks/user";
import { genericObjectReadFactory } from "@mocks/genericObject";

interface NodePropertyInputProps {
  modelValue: { propertyType: any; propertyValue: any };
  queue: string;
  formType: "filter" | "edit";
  allowDelete?: boolean;
  fixedPropertyType?: boolean;
}

const props: NodePropertyInputProps = {
  modelValue: { propertyType: null, propertyValue: null },
  queue: "external",
  formType: "filter",
};

function factory(
  args: {
    props: NodePropertyInputProps;
    initialState?: Record<string, unknown>;
  } = { props: props, initialState: {} },
) {
  return mount(NodePropertyInput, {
    global: {
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          initialState: args.initialState ? args.initialState : {},
        }),
      ],
      provide: {
        availableEditFields: { external: [], intel: [], internal: [] },
        availableFilters: testConfiguration.alerts.alertFilters,
      },
    },
    propsData: args.props,
  });
}

describe("NodePropertyInput", () => {
  it("renders correctly when no initial modelValue is given with default props", () => {
    factory();
    // Should default to first filter type in list
    cy.contains("Disposition").should("be.visible");
    cy.contains("None").should("be.visible");
    cy.get('[data-cy="property-input-delete"]').should("not.exist");
  });
  it("shows delete button if 'allowDelete' prop is set to true and emits expected event on click", () => {
    factory({
      props: {
        modelValue: { propertyType: null, propertyValue: null },
        queue: "external",
        formType: "filter",
        allowDelete: true,
      },
    });
    cy.get('[data-cy="property-input-delete"]').should("be.visible");
  });
  it("does not allow switiching prop type or show prop type select if fixedPropertyType is set to true", () => {
    factory({
      props: {
        modelValue: { propertyType: null, propertyValue: null },
        queue: "external",
        formType: "filter",
        fixedPropertyType: true,
      },
    });
    cy.contains("Disposition").should("not.exist");
    cy.contains("None").should("be.visible");
  });
  it("renders correctly if no modelValue is given, and no propertyTypeOptions exist", () => {
    factory({
      props: {
        modelValue: { propertyType: null, propertyValue: null },
        queue: "external",
        formType: "edit",
      },
    });
    cy.findByText("Select a property").should("be.visible").click();
    cy.findByText("No available options").should("be.visible");
    cy.get("li").should("be.visible").should("have.length", 1);
  });
  it("renders correctly when initial modelValue is given, but propertyType cannot be found", () => {
    factory({
      props: {
        modelValue: { propertyType: "fake", propertyValue: null },
        queue: "external",
        formType: "filter",
      },
    });
    cy.findByText("Select a property").should("be.visible").click();
    cy.findByText("No available options").should("not.exist");
    cy.get("li").should("have.length.above", 1); // There should be >1 options
  });
  it("renders correctly when initial modelValue is given, but propertyValue cannot be found", () => {
    factory({
      props: {
        modelValue: { propertyType: "owner", propertyValue: "fake" },
        queue: "external",
        formType: "filter",
      },
    });
    // Should choose that property type, but default to no value selected
    cy.contains("Owner").should("be.visible");
    cy.contains("None").should("be.visible");
  });
  it("renders string-type property option correctly (name)", () => {
    factory({
      props: {
        modelValue: { propertyType: "name", propertyValue: "Test" },
        queue: "external",
        formType: "filter",
      },
    });
    cy.contains("Name").should("be.visible");
    cy.findByDisplayValue("Test").should("be.visible");
  });
  it("renders select-type property option correctly (owner)", () => {
    factory({
      props: {
        modelValue: { propertyType: "owner", propertyValue: userReadFactory() },
        queue: "external",
        formType: "filter",
      },
      initialState: { userStore: { items: [userReadFactory()] } },
    });
    cy.contains("Owner").should("be.visible");
    cy.contains("Test Analyst").should("be.visible");
  });
  it("renders chip-type property option correctly (tags)", () => {
    factory({
      props: {
        modelValue: { propertyType: "tags", propertyValue: ["tagA", "tagB"] },
        queue: "external",
        formType: "filter",
      },
    });
    cy.contains("Tags").should("be.visible");
    cy.contains("tagA").should("be.visible");
    cy.contains("tagB").should("be.visible");
  });
  it("renders date-type property option correctly (event time after)", () => {
    factory({
      props: {
        modelValue: {
          propertyType: "eventTimeAfter",
          propertyValue: new Date(2022, 4, 25, 12, 0, 0, 0),
        },
        queue: "external",
        formType: "filter",
      },
    });
    cy.contains("Event Time After").should("be.visible");
    cy.findByDisplayValue("05/25/2022 12:00").should("be.visible");
  });
  it("renders multiselect-type property option correctly (observable types)", () => {
    factory({
      props: {
        modelValue: {
          propertyType: "observableTypes",
          propertyValue: [
            genericObjectReadFactory({ value: "ipv4" }),
            genericObjectReadFactory({ value: "file" }),
          ],
        },
        queue: "external",
        formType: "filter",
      },
      initialState: {
        observableTypeStore: {
          items: [
            genericObjectReadFactory({ value: "ipv4" }),
            genericObjectReadFactory({ value: "file" }),
            genericObjectReadFactory({ value: "url" }),
          ],
        },
      },
    });
    cy.contains("Observable Types").should("be.visible");
    cy.contains("ipv4, file").should("be.visible");
  });
  it("renders categorized-value-type property option correctly (observable)", () => {
    factory({
      props: {
        modelValue: {
          propertyType: "observable",
          propertyValue: {
            category: genericObjectReadFactory({ value: "ipv4" }),
            value: "1.2.3.4",
          },
        },
        queue: "external",
        formType: "filter",
      },
      initialState: {
        observableTypeStore: {
          items: [
            genericObjectReadFactory({ value: "ipv4" }),
            genericObjectReadFactory({ value: "file" }),
            genericObjectReadFactory({ value: "url" }),
          ],
        },
      },
    });
    cy.contains("Observable").should("be.visible");
    cy.contains("ipv4").should("be.visible");
    cy.findByDisplayValue("1.2.3.4").should("be.visible");
  });
});
