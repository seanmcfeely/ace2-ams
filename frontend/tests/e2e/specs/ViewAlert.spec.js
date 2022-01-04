describe("ViewAlert.vue", () => {
  before(() => {
    cy.log("logging in");
    cy.login();
  });

  after(() => {
    cy.log("logging out");
    cy.logout();
  });

  beforeEach(() => {
    Cypress.Cookies.preserveOnce("access_token", "refresh_token");
    cy.visit("/alert/02f8299b-2a24-400f-9751-7dd9164daf6a");
    cy.url().should("contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a");
  });

  it("View Alert page renders", () => {
    cy.get("#alert-tree").should("be.visible");
  });

  it("Renders the expected number of nodes", () => {
    // Total number of nodes
    cy.get(".pi").should("have.length", 32);

    // Number of expandable nodes
    cy.get(".p-tree-toggler-icon").should("have.length", 14);

    // Number of expanded nodes
    cy.get(".pi-chevron-down").should("have.length", 13);
    // Number of collapsed nodes
    cy.get(".pi-chevron-right").should("have.length", 1);
  });

  it("Renders the expected number of tags", () => {
    cy.get(".p-chip").should("have.length", 4);
  });

  it("should automatically collapse repeated observable analysis", () => {
    // First appearance of 'fqdn: evil.com' observable
    cy.get('[data-cy="fqdn: evil.com"]').first().should("be.visible");

    // First 'fqdn: evil.com' toggle icon
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .first()
      .should("have.class", "pi-chevron-down");

    // First appearance of 'Test Analysis', child analysis of 'evil.com'
    cy.get('[data-cy="Test Analysis"]').should("be.visible");

    // Second appearance of 'fqdn: evil.com' observable
    cy.get('[data-cy="fqdn: evil.com"]').last().should("be.visible");

    // Second 'fqdn: evil.com' toggle icon
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .should("have.class", "pi-chevron-right");

    // Second appearance of child analysis of 'evil.com'
    cy.get('[data-cy="Test Analysis"]').eq(1).should("not.exist");
  });

  it("should toggle observable/analysis expanded status when icon clicked", () => {
    // Second 'fqdn: evil.com' toggle icon
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .should("have.class", "pi-chevron-right");

    // Second appearance of child analysis of 'evil.com'
    cy.get('[data-cy="Test Analysis"]').eq(1).should("not.exist");

    // Click the toggle
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .click();

    // Only that icon should have changed
    // Number of expanded nodes
    cy.get(".pi-chevron-down").should("have.length", 15);
    // Number of collapsed nodes
    cy.get(".pi-chevron-right").should("not.exist");

    // Should now have down/'expanded' toggle icon
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .should("have.class", "pi-chevron-down");

    // Repeated analysis should now be visible
    cy.get('[data-cy="Test Analysis"]').eq(1).should("be.visible");

    // Click the toggle again
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .click();

    // Should have the right/'collapsed' toggle icon again
    cy.get(
      '[data-cy="fqdn: evil.com"] > :nth-child(1) > :nth-child(1) > .p-link > .p-tree-toggler-icon',
    )
      .last()
      .should("have.class", "pi-chevron-right");

    // Child analysis no longer visible
    cy.get('[data-cy="Test Analysis"]').eq(1).should("not.exist");

    // Node counts back to original
    // Number of expanded nodes
    cy.get(".pi-chevron-down").should("have.length", 13);
    // Number of collapsed nodes
    cy.get(".pi-chevron-right").should("have.length", 1);
  });

  it("should route to a 'View Analysis' page when analysis is clicked", () => {
    // Click first 'Test Analysis' node
    cy.get('[data-cy="Test Analysis"]').contains("Test Analysis").click();

    //  Not perfect, but url should now be a child route of the test alert
    cy.url().should("contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/");
  });

  // Alert Action Toolbar tests

  // Disposition
  it.only("should make a request to update and get updated alert when disposition is set", () => {
    cy.intercept("PATCH", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "updateAlert",
    );
    cy.intercept("POST", "/api/node/comment").as("createComment");
    cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "getAlert",
    );

    // Open disposition modal
    cy.get(".p-button-normal").click();
    cy.get(".p-dialog-content").should("be.visible");
    // Select first option
    cy.get('[aria-label="FALSE_POSITIVE"]').click();
    // Add a comment
    cy.get(".p-inputtextarea").click().type("test disposition comment!");
    // Submit
    cy.get(".p-dialog-footer > .p-button").click();
    cy.get(".p-dialog-content").should("not.exist");

    cy.intercept("PATCH", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "updateAlert",
    );

    cy.wait("@updateAlert").its("state").should("eq", "Complete");
    cy.wait("@createComment").its("state").should("eq", "Complete");
    cy.wait("@getAlert").its("state").should("eq", "Complete");
  });

  // Comment
  it("should make a request to add comment and get updated alert when comment is added", () => {
    cy.intercept({
      path: "/api/node/comment/",
      method: "POST",
    }).as("createComment");
    cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "getAlert",
    );

    // Open comment modal
    cy.get(".p-toolbar-group-left > :nth-child(2)").click();
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
    cy.intercept("PATCH", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "updateAlert",
    );
    cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "getAlert",
    );

    // Click button

    cy.get(".p-toolbar-group-left > :nth-child(3)").click();
    cy.wait("@updateAlert").its("state").should("eq", "Complete");
    cy.wait("@getAlert").its("state").should("eq", "Complete");
  });

  // Assign
  it("should make a request to update owner and get updated alert when owner is set", () => {
    cy.intercept("PATCH", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "updateAlert",
    );
    cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "getAlert",
    );
    // Open assign modal
    cy.get(".p-toolbar-group-left > :nth-child(4)").click();
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
  it("should make a request to update tags and get updated alert when owner is set", () => {
    cy.intercept("PATCH", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "updateAlert",
    );
    cy.intercept("GET", "/api/alert/02f8299b-2a24-400f-9751-7dd9164daf6a").as(
      "getAlert",
    );

    // Open tag modal
    cy.get(".p-toolbar-group-left > :nth-child(5)").click();
    cy.get(".p-dialog-content").should("be.visible");
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
});
