import { mount } from "@cypress/vue";

import PrimeVue from "primevue/config";

import ObservableLeaf from "@/components/Observables/ObservableLeaf.vue";
import router from "@/router/index";
import {
  observableAction,
  observableTreeRead,
} from "../../../../../src/models/observable";
import { observableTreeReadFactory } from "../../../../mocks/observable";
import { genericObjectReadFactory } from "@mocks/genericObject";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { testConfiguration } from "@/etc/configuration/test";
import { ObservableInstance } from "@/services/api/observable";
import ToastService from "primevue/toastservice";

interface ObservableLeafProps {
  observable: observableTreeRead;
  showCopyToClipboard?: boolean;
  showActionsMenu?: boolean;
  showTags?: boolean;
}

const defaultProps: ObservableLeafProps = {
  observable: observableTreeReadFactory(),
};

function factory(
  args: {
    props: ObservableLeafProps;
    config: Record<string, unknown>;
  } = {
    props: defaultProps,
    config: testConfiguration,
  },
) {
  mount(ObservableLeaf, {
    global: {
      plugins: [PrimeVue, ToastService, createCustomCypressPinia(), router],
      provide: {
        config: args.config,
        nodeType: "alerts",
      },
    },
    propsData: args.props,
  });
}

const observableWithTags = observableTreeReadFactory({
  value: "Observable w/ Tags",
  children: [],
  tags: [genericObjectReadFactory({ value: "testTag" })],
});

const observableWithMetadata = observableTreeReadFactory({
  value: "Observable w/ Metadata",
  firstAppearance: true,
  nodeMetadata: { display: { type: "custom type", value: "custom value" } },
});

const observableWithForDetectionEnabled = observableTreeReadFactory({
  value: "Observable w/ For Detection Enabled",
  firstAppearance: true,
  forDetection: true,
});

const ipv4Observable = observableTreeReadFactory({
  value: "1.2.3.4",
  firstAppearance: true,
  type: genericObjectReadFactory({ value: "ipv4" }),
});
describe("ObservableLeaf", () => {
  it("renders correctly with all optional props set to false", () => {
    factory({
      props: {
        observable: observableWithTags,
        showCopyToClipboard: false,
        showActionsMenu: false,
        showTags: false,
      },
      config: testConfiguration,
    });
    cy.contains("testObservableType: Observable w/ Tags")
      .should("be.visible")
      .should("have.css", { color: "black" });
    cy.findByRole("button").should("not.exist");
  });
  it("renders correctly with default props", () => {
    factory({
      props: { observable: observableWithTags },
      config: testConfiguration,
    });
    cy.contains("testObservableType: Observable w/ Tags")
      .should("be.visible")
      .should("have.css", { color: "black" });
    cy.findAllByRole("button").should("have.length", 2);
    cy.get("span").contains("testTag");
  });
  it("loads common and observable type-specific actions from config, if available", () => {
    factory({
      props: { observable: ipv4Observable },
      config: testConfiguration,
    });

    const expectedMenuItems = ["Enable Detection", "Subheader", "IPV4 Command"];

    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.findAllByRole("menuitem")
      .should("have.length", 3)
      .each((menuItem, index) => {
        cy.wrap(menuItem).should("have.text", expectedMenuItems[index]);
      });
  });
  it("observable actions menu toggle button will not show if no actions are available", () => {
    factory({
      props: { observable: observableWithTags },
      config: {
        observables: { commonObservableActions: [], observableMetadata: [] },
      },
    });
    cy.get("[data-cy='show-actions-menu-button']").should("not.exist");
  });
  it("loads style from config, if available", () => {
    factory({
      props: { observable: ipv4Observable },
      config: testConfiguration,
    });
    cy.contains("ipv4: 1.2.3.4")
      .should("be.visible")
      .should("have.css", { color: "blue" });
  });
  it("attempts to open modal when 'modal'-type observable action clicked", () => {
    factory({
      props: { observable: observableWithForDetectionEnabled },
      config: testConfiguration,
    });
    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Update Expiration").click();
    cy.get("@stub-6").should("have.been.calledOnce");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("displays error message if 'modal'-type observable action clicked, but modal isn't available", () => {
    const missingModalObservableAction: observableAction = {
      type: "modal",
      label: "Open Modal",
      description: "Open a modal",
      icon: "pi pi-link",
    };

    factory({
      props: { observable: observableWithTags },
      config: {
        observables: {
          commonObservableActions: [missingModalObservableAction],
          observableMetadata: [],
        },
      },
    });
    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Open Modal").click();

    cy.get("[data-cy='observable-action-error']")
      .contains("'Open Modal' Failed")
      .should("be.visible");
    cy.get("[data-cy='observable-action-error']")
      .contains("No modal has been configured for this action.")
      .should("be.visible");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("attempts to run command when 'command'-type observable action clicked", () => {
    cy.stub(ObservableInstance, "update")
      .withArgs("observableUuid1", { forDetection: true })
      .as("updateObservable")
      .resolves();

    factory({
      props: { observable: observableWithTags },
      config: testConfiguration,
    });
    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Enable Detection").click();

    cy.get("@updateObservable").should("have.been.calledOnce");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("displays error message if 'command'-type observable action clicked, but command isn't available", () => {
    const missingCommandObservableAction: observableAction = {
      type: "command",
      label: "Execute Command",
      description: "Execute a command",
      icon: "pi pi-link",
    };

    factory({
      props: { observable: observableWithTags },
      config: {
        observables: {
          commonObservableActions: [missingCommandObservableAction],
          observableMetadata: [],
        },
      },
    });
    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Execute Command").click();
    cy.get("[data-cy='observable-action-error']")
      .contains("'Execute Command' Failed")
      .should("be.visible");
    cy.get("[data-cy='observable-action-error']")
      .contains("No command has been configured for this action.")
      .should("be.visible");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("displays error message if 'command'-type observable action clicked, but command fails", () => {
    cy.stub(ObservableInstance, "update")
      .withArgs("observableUuid1", { forDetection: true })
      .as("updateObservable")
      .rejects(new Error("404 request failed"));

    factory({
      props: { observable: observableWithTags },
      config: testConfiguration,
    });
    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Enable Detection").click();

    cy.get("@updateObservable").should("have.been.calledOnce");
    cy.get("[data-cy='observable-action-error']")
      .contains("'Enable Detection' Failed")
      .should("be.visible");
    cy.get("[data-cy='observable-action-error']")
      .contains("Error: 404 request failed")
      .should("be.visible");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("displays error message if 'url'-type observable action clicked, but URL isn't available", () => {
    const urlTypeObservableAction: observableAction = {
      type: "url",
      label: "Go to URL",
      description: "Test url",
      icon: "pi pi-link",
    };

    factory({
      props: { observable: observableWithTags },
      config: {
        observables: {
          commonObservableActions: [urlTypeObservableAction],
          observableMetadata: [],
        },
      },
    });

    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Go to URL").click();
    cy.get("[data-cy='observable-action-error']")
      .contains("'Go to URL' Failed")
      .should("be.visible");
    cy.get("[data-cy='observable-action-error']")
      .contains("No URL has been configured for this action.")
      .should("be.visible");
    cy.findByRole("menu").should("not.exist"); // Menu should have been closed
  });
  it("displays an observables value using node metadata if available", () => {
    factory({
      props: { observable: observableWithMetadata },
      config: testConfiguration,
    });
    cy.get("span").should(
      "contain.text",
      "custom type (testObservableType): custom value",
    );
  });
  it("sets the alert filters to the an observable's type and value when clicked", () => {
    factory({
      props: { observable: observableWithTags },
      config: testConfiguration,
    });
    cy.contains("Observable w/ Tags").click();
    cy.get("@stub-1").should("have.been.calledWith", {
      nodeType: "alerts",
      filters: {
        observable: {
          category: observableWithTags.type,
          value: observableWithTags.value,
        },
      },
    });
  });
});

// Because this test changes the testing URL, it needs to be isolated
describe("ObservableLeaf URL test", () => {
  it("attempts to reroute to given URL when 'url'-type observable action clicked", () => {
    const urlTypeObservableAction: observableAction = {
      type: "url",
      label: "Go to URL",
      description: "Test url",
      icon: "pi pi-link",
      url: "www.google.com",
    };

    factory({
      props: { observable: observableWithTags },
      config: {
        observables: {
          commonObservableActions: [urlTypeObservableAction],
          observableMetadata: [],
        },
      },
    });

    cy.get("[data-cy='show-actions-menu-button']").click();
    cy.contains("Go to URL").click();
    cy.location("pathname").should("contain", "www.google.com");
  });
});
