import { mount } from "@cypress/vue";
import PrimeVue from "primevue/config";

import AlertTableExpansion from "@/components/Alerts/AlertTableExpansion.vue";

import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { observableInAlertRead } from "@/models/observable";
import { observableInAlertReadFactory } from "@mocks/observable";
import router from "@/router/index";
import { analysisMetadataReadFactory } from "@mocks/analysisMetadata";
import { metadataTagReadFactory } from "@mocks/metadata";

interface AlertTableExpansionProps {
  observables: observableInAlertRead[] | null;
}

const defaultProps: AlertTableExpansionProps = {
  observables: null,
};

function factory(
  args = {
    props: defaultProps,
  },
) {
  return mount(AlertTableExpansion, {
    global: {
      plugins: [createCustomCypressPinia(), PrimeVue, router],
      provide: { nodeType: "alerts" },
    },
    propsData: args.props,
  });
}

describe("AlertTableExpansion", () => {
  it("renders with observables prop set to null (loading state)", () => {
    factory();
    cy.get("ul").should("be.visible");
    cy.get('[data-cy="loading-observable"]').should("have.length", 4);
  });
  it("renders with observables prop set to empty", () => {
    factory({ props: { observables: [] } });
    cy.get("ul").should("not.exist");
    cy.contains("No observables exist for this alert.");
  });
  it("renders with observables containing observables with tags", () => {
    factory({
      props: {
        observables: [
          observableInAlertReadFactory(),
          observableInAlertReadFactory({
            value: "TestObservable2",
            analysisMetadata: analysisMetadataReadFactory({
              tags: [metadataTagReadFactory({ value: "analysisTag1" })],
            }),
            tags: [metadataTagReadFactory({ value: "testTag" })],
          }),
        ],
      },
    });
    // Check that the observables (and any tags) showed up
    cy.get("li").contains("testObservableType : TestObservable");
    cy.get("li").contains("testObservableType : TestObservable2");
    cy.get("li").eq(1).contains("testTag");
    cy.get("li").eq(1).contains("analysisTag1");
  });
  it("renders with observables containing observables with tags", () => {
    const observable = observableInAlertReadFactory();
    factory({
      props: {
        observables: [observable],
      },
    });
    cy.contains("testObservableType : TestObservable").click();
    cy.get("@stub-1").should("have.been.calledWith", {
      nodeType: "alerts",
      filters: {
        observable: [{ category: observable.type, value: observable.value }],
      },
    });
  });
});
