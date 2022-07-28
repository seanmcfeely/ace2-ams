import { visitUrl } from "./helpers";

describe("ViewAlert.vue", () => {
  describe("No Database Changes", () => {
    before(() => {
      cy.resetDatabase();
      cy.login();

      // Add the test alert to the database
      cy.request({
        method: "POST",
        url: "/api/test/add_alerts",
        body: {
          template: "small.json",
          count: 1,
        },
      });
    });

    beforeEach(() => {
      // Intercept the API call that loads the alert data
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );

      cy.intercept(
        "GET",
        "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/summary/url_domain",
      ).as("getAlertUrlDomainSummary");

      visitUrl({
        url: "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a",
        extraIntercepts: ["@getAlert", "@getAlertUrlDomainSummary"],
      });
    });

    it("will reroute to the Manage Alerts page with observable filter applied when observable clicked", () => {
      // Intercept the API call that loads the alerts
      cy.intercept(
        "GET",
        "/api/alert/?sort=event_time%7Cdesc&limit=10&offset=0&observable=email_subject%7CHello",
      ).as("getAlerts");

      // Find the email subject observable and click
      cy.contains("email_subject: Hello").click();

      // Should have been rerouted
      cy.url().should("contain", "/manage_alerts");

      // Wait for the API call to fetch the alerts to finish
      cy.wait("@getAlerts").its("state").should("eq", "Complete");

      // Check which alerts are visible (should be 1 (1 checkbox visible for the header row))
      cy.get(".p-checkbox-box").should("have.length", 2);

      // Verify in the filter modal that the correct filter is set
      cy.get(".p-splitbutton-menubutton").click();
      cy.get(".p-menuitem:nth-child(1) > .p-menuitem-link").click();
      cy.get(".p-dialog-footer > :nth-child(2)").click();
      cy.get(".formgrid > :nth-child(1) > .p-dropdown > .p-dropdown-label")
        .first()
        .should("have.text", "Observable");
      cy.get(
        ".col > :nth-child(1) > :nth-child(1) > .p-dropdown > .p-dropdown-label",
      )
        .eq(0)
        .should("have.text", "email_subject");
      cy.get(".col > :nth-child(1) > :nth-child(2) > input").should(
        "have.value",
        "Hello",
      );

      // Close the modal to finish
      cy.get(".p-dialog-header-icon").click();
    });

    it("collapses and expands the alert details when header is clicked", () => {
      // Details table panel should start out open
      cy.get(":nth-child(1) > .header-cell").should("be.visible");

      // Click the toggle
      cy.get(".p-accordion-toggle-icon").click();

      // The details panel should no longer be visible/open
      cy.get(":nth-child(1) > .header-cell").should("not.be.visible");

      // Click the toggle again
      cy.get(".p-accordion-toggle-icon").click();

      // Details table panel should be open/visible again
      cy.get(":nth-child(1) > .header-cell").should("be.visible");
    });
  });

  describe("Database Changes", () => {
    beforeEach(() => {
      cy.resetDatabase();
      cy.login();

      // Add the test alert to the database
      cy.request({
        method: "POST",
        url: "/api/test/add_alerts",
        body: {
          template: "small.json",
          count: 1,
        },
      });

      // Intercept the API call that loads the alert data
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );

      cy.intercept(
        "GET",
        "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/summary/url_domain",
      ).as("getAlertUrlDomainSummary");

      visitUrl({
        url: "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a",
        extraIntercepts: ["@getAlert", "@getAlertUrlDomainSummary"],
      });
    });

    // Disposition
    it("should make a request to update and get updated alert when disposition is set", () => {
      cy.intercept("PATCH", "/api/alert/").as("updateAlert");
      cy.intercept("POST", "/api/alert/comment").as("createComment");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );

      // Open disposition modal
      cy.get("[data-cy=disposition-button]").click();

      cy.get(".p-dialog-content").should("be.visible");
      // Select first option
      cy.get('[aria-label="FALSE_POSITIVE"]').click();
      // Add a comment
      cy.get(".p-inputtextarea").click().type("test disposition comment!");
      // Submit
      cy.get(".p-dialog-footer > .p-button").click();
      cy.get(".p-dialog-content").should("not.exist");

      cy.intercept("PATCH", "/api/alert/").as("updateAlert");

      cy.wait("@updateAlert").its("state").should("eq", "Complete");
      cy.wait("@createComment").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");
    });

    // Comment
    it("should make a request to add comment and get updated alert when comment is added", () => {
      cy.intercept({
        path: "/api/alert/comment/",
        method: "POST",
      }).as("createComment");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );

      // Open comment modal
      cy.get("[data-cy=comment-button]").click();

      cy.get(".p-dialog-content").should("be.visible");
      // Add a comment
      cy.get(".p-inputtextarea").click().type("testing regular comment!");
      // Submit
      cy.get(".p-dialog-footer > :nth-child(2)").click();
      cy.get(".p-dialog-content").should("not.exist");

      cy.wait("@createComment").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");
    });

    // Take Ownership
    it("should make a request to update and get updated alert take ownership is clicked", () => {
      cy.intercept("PATCH", "/api/alert/").as("updateAlert");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );

      // Click button

      cy.get("[data-cy=take-ownership-button]").click();
      cy.wait("@updateAlert").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");
    });

    // Assign
    it("should make a request to update owner and get updated alert when owner is set", () => {
      cy.intercept("PATCH", "/api/alert/").as("updateAlert");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );
      // Open assign modal
      cy.get("[data-cy=assign-button]").click();

      cy.get(".p-dialog-content").should("be.visible");
      // Select first option
      cy.get(".p-dropdown-label").click();
      cy.get('[aria-label="Analyst Alice"]').click();
      // Submit
      cy.get(".p-dialog-footer > :nth-child(2)").click();
      cy.get(".p-dialog-content").should("not.exist");

      cy.wait("@updateAlert").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");
    });

    // Tag
    it("should make a request to update tags and get updated alert when tag added through modal", () => {
      cy.intercept("PATCH", "/api/alert/").as("updateAlert");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );
      cy.intercept("GET", "/api/metadata/tag/?offset=0").as("getObjectTags");

      // Open tag modal
      cy.get("[data-cy=tag-button]").click();

      cy.get(".p-dialog-content").should("be.visible");
      cy.wait("@getObjectTags").its("state").should("eq", "Complete");
      // Type a tag
      cy.get(".p-chips > .p-inputtext").click().type("TestTag").type("{enter}");
      // Select a tag from the dropdown
      cy.get(".p-fluid > .p-dropdown > .p-dropdown-label").click();
      cy.get('[aria-label="scan_me"]').click();
      // Submit
      cy.get(".p-dialog-footer > :nth-child(2)").should("be.visible");
      cy.get(".p-dialog-footer > :nth-child(2)").click();
      cy.get(".p-dialog-content").should("not.exist");

      cy.wait("@updateAlert").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");

      // Add another tag, make sure that any existing tags are not overwritten
      // Open tag modal
      cy.get("[data-cy=tag-button]").click();

      cy.get(".p-dialog-content").should("be.visible");
      cy.wait("@getObjectTags").its("state").should("eq", "Complete");
      // Type a tag
      cy.get(".p-chips > .p-inputtext").click().type("TestTag").type("{enter}");
      // Select a tag from the dropdown
      cy.get(".p-fluid > .p-dropdown > .p-dropdown-label").click();
      cy.get('[aria-label="scan_me"]').click();
      // Submit
      cy.get(".p-dialog-footer > :nth-child(2)").should("be.visible");
      cy.get(".p-dialog-footer > :nth-child(2)").click();
      cy.get(".p-dialog-content").should("not.exist");

      cy.wait("@updateAlert").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");
    });

    // Add observable
    it("should make a request to add observable to the alert and get updated alert via AddObservablesModal", () => {
      cy.intercept("POST", "/api/observable/").as("createObservables");
      cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
        "getAlert",
      );
      cy.contains("Add Observable(s)").click();

      // Add first observable
      cy.get("[name=observable-type]").click();
      cy.get('[aria-label="ipv4"]').click();
      cy.get("[name=observable-value] input").type("1.2.3.4");

      // Add second observable
      cy.get("#add-observable").click();
      cy.get("[name=observable-type]").eq(1).click();
      cy.get('[aria-label="ipv4"]').click();
      cy.get("[name=observable-value] input").eq(1).type("5.6.7.8");

      // Submit
      cy.contains("Add!").click();

      cy.wait("@createObservables").its("state").should("eq", "Complete");
      cy.wait("@getAlert").its("state").should("eq", "Complete");

      // Check that the observables were added
      cy.contains("1.2.3.4").should("exist");
      cy.contains("5.6.7.8").should("exist");
    });
  });
});
