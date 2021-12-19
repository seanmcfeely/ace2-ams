describe("ViewAnalysis.vue", () => {
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

    // Go to a test analysis page
    cy.visit("/alert/02f8299b-2a24-400f-9751-7dd9164daf6a");
    cy.get('[data-cy="Test Analysis"]').contains("Test Analysis").click();
    cy.url().should("contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/");
  });

  it("View Analysis page renders", () => {
    cy.get("#view-analysis").should("be.visible");
  });

  it("Will display breadcrumbs back to alert and home", () => {
    // There should be 3 breadcrumbs
    cy.get(".p-menuitem-link").should("have.length", 3);

    // There should be a home breadcrumb
    cy.get(".p-breadcrumb-home > .p-menuitem-link").should("be.visible");

    // There should be a breadcrumb to the parent alert
    cy.get(".p-menuitem-link").contains('"Small Alert"').should("be.visible");

    // There should be a breadcrumb representing the current analysis
    cy.get(".p-menuitem-link").contains('"Test Analysis"').should("be.visible");
  });

  it("Will route to home (Manage Alerts) when home breadcrumb is clicked", () => {
    cy.get(".p-breadcrumb-home > .p-menuitem-link").click()
    cy.url().should("contain", "/manage_alerts");
  });

  it("Will route to parent alert when alert breadcrumb is clicked", () => {
    cy.get(".p-menuitem-link").contains('"Small Alert"').click()
    cy.url().should("not.contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/");
    cy.url().should("contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a");
  });
  it("should not route anywhere when analysis breadcrumb is clicked", () => {
    cy.get(".p-menuitem-link").contains('"Test Analysis"').click()
    cy.url().should("contain", "/alert/02f8299b-2a24-400f-9751-7dd9164daf6a/");
  });
});
