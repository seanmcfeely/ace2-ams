// Example Cypress Vue component test that we might use one day
// NOTE: This test is not fully functional at this point.

import { mount } from "@cypress/vue";
import PrimeVue from "primevue/config";

import EditEventModal from "@/components/Modals/EditEventModal.vue";
import { Event } from "@/services/api/event";
import { eventReadFactory, mockEventUUID } from "@mocks/events";
import { testConfiguration } from "@/etc/configuration/test/index";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import {
  genericObjectReadFactory,
  queueableObjectReadFactory,
} from "@mocks/genericObject";
import ToastService from "primevue/toastservice";

import Tooltip from "primevue/tooltip";
import { userReadFactory } from "@mocks/user";

import CommentEditor from "@/components/Comments/CommentEditor.vue";
import ThreatSelector from "@/components/Threat/ThreatSelector.vue";
import { Threat } from "@/services/api/threat";
import { ThreatActor } from "@/services/api/threatActor";
import { ThreatType } from "@/services/api/threatType";
import { EventPreventionTool } from "@/services/api/eventPreventionTool";
import { EventRemediation } from "@/services/api/eventRemediation";
import { EventSeverity } from "@/services/api/eventSeverity";
import { EventStatus } from "@/services/api/eventStatus";
import { EventType } from "@/services/api/eventType";
import { EventVector } from "@/services/api/eventVector";
import { User } from "@/services/api/user";
import { eventCommentReadFactory } from "@mocks/comment";
import { EventComment } from "@/services/api/eventComment";

function factory(args = { stubActions: true }) {
  const initialState = {
    modalStore: {
      openModals: ["EditEventModal"],
    },
    authStore: { user: userReadFactory() },
  };
  const wrapper = mount(EditEventModal, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          initialState: initialState,
          stubActions: args.stubActions,
        }),
        ToastService,
      ],
      provide: {
        availableEditFields: testConfiguration.events.eventEditableProperties,
        availableFilters: testConfiguration.events.eventFilters,
      },
    },
    propsData: {
      eventUuid: mockEventUUID,
      name: "EditEventModal",
    },
  });
  return wrapper;
}

describe("EditEventModal", () => {
  beforeEach(() => {
    cy.stub(EventPreventionTool, "readAll").returns([
      queueableObjectReadFactory({
        value: "Test Prevention Tool",
        queues: [genericObjectReadFactory({ value: "external" })],
      }),
    ]);
    cy.stub(EventSeverity, "readAll").returns([]);
    cy.stub(EventRemediation, "readAll").returns([
      queueableObjectReadFactory({
        value: "Test Remediation",
        queues: [genericObjectReadFactory({ value: "external" })],
      }),
    ]);
    cy.stub(EventStatus, "readAll").returns([]);
    cy.stub(EventType, "readAll").returns([]);
    cy.stub(ThreatActor, "readAll").returns([]);
    cy.stub(Threat, "readAll").returns([]);
    cy.stub(ThreatType, "readAll").returns([]);
    cy.stub(EventVector, "readAll").returns([]);
    cy.stub(User, "readAll").returns([userReadFactory()]);
  });

  it("renders", () => {
    cy.stub(Event, "read").returns(eventReadFactory());
    factory();
  });
  it("correctly pre-loads the form with existing event data", () => {
    cy.stub(Event, "read").returns(
      eventReadFactory({
        queue: genericObjectReadFactory({ value: "external" }),
      }),
    );
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains("Name")
        .siblings()
        .eq(0)
        .find("input")
        .should("have.value", "Test Event");
      cy.contains("Owner")
        .siblings()
        .eq(0)
        .find("span")
        .should("have.text", "Test Analyst");
      // cy.contains("Owner").siblings().eq(0).find('span').should("have.text", "None") // Needs to be fixed
      cy.contains("Comment").should("exist");
      wrapper.findComponent(CommentEditor);
      cy.contains("Prevention Tools").siblings().eq(0).contains("None");
      cy.contains("Remediation").siblings().eq(0).contains("None");
      cy.contains("Threats").should("exist");
      wrapper.findComponent(ThreatSelector);
      cy.contains("Event Time")
        .siblings()
        .eq(0)
        .find("input")
        .should("contain.value", "")
        .invoke("attr", "placeholder")
        .should("equal", "Enter a date!");
    });
  });
  it("correctly submits updated event data", () => {
    cy.stub(Event, "read").returns(
      eventReadFactory({
        queue: genericObjectReadFactory({ value: "external" }),
      }),
    );
    cy.stub(Event, "update")
      .withArgs([
        {
          uuid: "testEvent1",
          name: "New Name",
          owner: "analyst",
          preventionTools: ["Test Prevention Tool"],
          remediations: ["Test Remediation"],
          eventTime: new Date("2022-04-12T16:00:00.000Z"),
          historyUsername: "analyst",
        },
      ])
      .as("updateEvent")
      .resolves();
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains("Name")
        .siblings()
        .eq(0)
        .find("input")
        .clear()
        .type("New Name");
      cy.contains("Prevention Tools").siblings().eq(0).contains("None").click();
      cy.contains("Test Prevention Tool").click();
      cy.contains("Remediation").siblings().eq(0).contains("None").click();
      cy.contains("Test Remediation").click();
      cy.contains("Event Time")
        .siblings()
        .eq(0)
        .find("input")
        .click()
        .type("04/12/2022 16:00:00")
        .type("{enter}");

      cy.contains("Save").click();

      cy.get("@updateEvent").should("have.been.calledOnce");

      cy.contains("Edit Event").should("not.exist");
    });
  });
  it("correctly submits updated event comment", () => {
    cy.stub(Event, "read").returns(
      eventReadFactory({
        queue: genericObjectReadFactory({ value: "external" }),
        comments: [eventCommentReadFactory()],
      }),
    );
    cy.stub(Event, "update")
      .withArgs([
        {
          uuid: "testEvent1",
          historyUsername: "analyst",
          owner: "analyst",
        },
      ])
      .as("updateEvent")
      .resolves();
    cy.stub(EventComment, "update")
      .withArgs("commentUuid1", {
        username: "analyst",
        value: "New Comment",
      })
      .as("updateComment")
      .resolves();
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form
      cy.get('[data-cy="edit-comment-button"]').click();
      cy.get('[data-cy="updated-comment-value"]').clear().type("New Comment");
      cy.get('[data-cy="save-comment-button"]').click();
      cy.contains("Save").click();

      cy.get("@updateEvent").should("have.been.calledOnce");
      cy.get("@updateComment").should("have.been.calledOnce");

      cy.contains("Edit Event").should("not.exist");
    });
  });
  it("correctly displays error if event cannot be fetched with Error", () => {
    cy.stub(Event, "read").rejects(
      new Error("404 request could not be completed"),
    );
    factory();
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains(
        "Could not load event data: 404 request could not be completed",
      ).should("be.visible");

      // Checks for the modal content main content div and error div
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .should("have.length", 2);
      // Checks that nothing is in the main content div (form shouldn't load if there was an error)
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .eq(0)
        .children()
        .children()
        .should("have.length", 0);
    });

    cy.get(".p-message-close-icon").click();
    cy.contains(
      "Could not load event data: 404 request could not be completed",
    ).should("not.exist");
  });
  it("correctly displays error if event cannot be fetched with error string", () => {
    cy.stub(Event, "read").callsFake(async () => {
      throw "404 request could not be completed";
    });
    factory();
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains(
        "Could not load event data: 404 request could not be completed",
      ).should("be.visible");

      // Checks for the modal content main content div and error div
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .should("have.length", 2);
      // Checks that nothing is in the main content div (form shouldn't load if there was an error)
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .eq(0)
        .children()
        .children()
        .should("have.length", 0);
    });
    cy.get(".p-message-close-icon").click();
    cy.contains(
      "Could not load event data: 404 request could not be completed",
    ).should("not.exist");
  });
  it("correctly displays error if event has invalid queue", () => {
    cy.stub(Event, "read").returns(eventReadFactory());
    factory();
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains(
        "Could not load event data: Could not load settings for this event queue: testObject",
      ).should("be.visible");

      // Checks for the modal content main content div and error div
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .should("have.length", 2);
      // Checks that nothing is in the main content div (form shouldn't load if there was an error)
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .eq(0)
        .children()
        .children()
        .should("have.length", 0);
    });
  });
  it("correctly displays error if event cannot be updated with Error", () => {
    cy.stub(Event, "read").returns(
      eventReadFactory({
        queue: genericObjectReadFactory({ value: "external" }),
      }),
    );
    cy.stub(Event, "update")
      .withArgs([
        {
          uuid: "testEvent1",
          name: "New Name",
          owner: "analyst",
          preventionTools: ["Test Prevention Tool"],
          remediations: ["Test Remediation"],
          eventTime: new Date("2022-04-12T16:00:00.000Z"),
          historyUsername: "analyst",
        },
      ])
      .as("updateEvent")
      .rejects(new Error("404 request could not be completed"));
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains("Name")
        .siblings()
        .eq(0)
        .find("input")
        .clear()
        .type("New Name");
      cy.contains("Prevention Tools").siblings().eq(0).contains("None").click();
      cy.contains("Test Prevention Tool").click();
      cy.contains("Remediation").siblings().eq(0).contains("None").click();
      cy.contains("Test Remediation").click();
      cy.contains("Event Time")
        .siblings()
        .eq(0)
        .find("input")
        .click()
        .type("04/12/2022 16:00:00")
        .type("{enter}");

      cy.contains("Save").click();

      cy.get("@updateEvent").should("have.been.calledOnce");

      cy.contains(
        "Could not update event: 404 request could not be completed",
      ).should("be.visible");

      // Checks that the error and form elements are all visible together
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .eq(0)
        .children()
        .children()
        .should("have.length", 8);
    });
  });
  it("correctly displays error if event cannot be updated with error string", () => {
    cy.stub(Event, "read").returns(
      eventReadFactory({
        queue: genericObjectReadFactory({ value: "external" }),
      }),
    );
    cy.stub(Event, "update")
      .withArgs([
        {
          uuid: "testEvent1",
          name: "New Name",
          owner: "analyst",
          preventionTools: ["Test Prevention Tool"],
          remediations: ["Test Remediation"],
          eventTime: new Date("2022-04-12T16:00:00.000Z"),
          historyUsername: "analyst",
        },
      ])
      .as("updateEvent")
      .callsFake(async () => {
        throw "404 request could not be completed";
      });
    const wrapper = factory({
      stubActions: false,
    });
    wrapper.then((wrapper) => {
      wrapper.vm.modalStore.open("EditEventModal"); // This will trigger initialization of the form

      cy.contains("Name")
        .siblings()
        .eq(0)
        .find("input")
        .clear()
        .type("New Name");
      cy.contains("Prevention Tools").siblings().eq(0).contains("None").click();
      cy.contains("Test Prevention Tool").click();
      cy.contains("Remediation").siblings().eq(0).contains("None").click();
      cy.contains("Test Remediation").click();
      cy.contains("Event Time")
        .siblings()
        .eq(0)
        .find("input")
        .click()
        .type("04/12/2022 16:00:00")
        .type("{enter}");

      cy.contains("Save").click();

      cy.get("@updateEvent").should("have.been.calledOnce");

      cy.contains(
        "Could not update event: 404 request could not be completed",
      ).should("be.visible");

      // Checks that the error and form elements are all visible together
      cy.get('[data-cy="edit-event-modal"]')
        .children(".p-dialog-content")
        .eq(0)
        .children()
        .children()
        .should("have.length", 8);
    });
  });
});
