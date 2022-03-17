import { visitUrl } from "./helpers";

describe("ViewEvent.vue", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");

    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "small_template.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });

  it("View Event page renders", () => {
    cy.get('[data-cy="event-details-menu"]').should("be.visible");
    cy.get('[aria-haspopup="true"]').eq(0).should("have.text", "Actions");
    cy.get('[aria-haspopup="true"]').eq(1).should("have.text", "Information");
    cy.get('[aria-haspopup="true"]').eq(2).should("have.text", "Analysis");
    cy.get('[data-cy="event-details-card"]').should("be.visible");
    cy.get('[data-cy="event-details-header"]').should("be.visible");
    cy.get('[data-cy="event-title"]').should("have.text", "Test Event");
    cy.get('[data-cy="event-details-link"]').should("be.visible");
    cy.get('[data-cy="event-details-content"]').should("be.visible");
    cy.get("#event-section-title").should("contain.text", "Event Summary");
  });

  it("Switches the component / details section when selected from dropdown", () => {
    // Click on the Analysis dropdown
    cy.get('[aria-haspopup="true"]').eq(2).click();
    // Select first available analysis type
    cy.get("span").contains("a_type0 Analysis").click();
    // Check that basic analysis showed up
    cy.get('[data-cy="event-details-content"]')
      .contains("Basic Analysis")
      .should("be.visible");
    cy.get('[data-cy="event-details-content"]')
      .contains("a_type0 Analysis")
      .should("be.visible");
    // Switch back to the event summary section and check content
    cy.get('[aria-haspopup="true"]').eq(1).click();
    cy.get("span").contains("Event Summary").click();
    cy.get("#event-section-title").should("contain.text", "Event Summary");
  });
});

describe("ViewEvent.vue actions", () => {
  beforeEach(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");

    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "small_template.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });

  // Have to  manually leave event page
  // BC when database resets it will try to get the old event with old uuid
  // And will cause an error
  afterEach(() => {
    visitUrl({
      url: "/manage_alerts",
    });
  });

  it("Correctly adds comment via comment modal and reloads page", () => {
    cy.intercept("POST", "/api/node/comment/").as("addComment");

    // Click on the Actions dropdown
    cy.get('[aria-haspopup="true"]').eq(0).click();
    cy.get("span").contains("Comment").click();
    // Add test data and submit
    cy.get(".p-inputtextarea").click().type("Test comment");
    cy.get(".p-dialog-footer > Button").last().click();
    cy.wait("@addComment").its("state").should("eq", "Complete");
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });
  it("Correctly takes ownership via take ownership item and reloads page", () => {
    cy.intercept("PATCH", "/api/event/").as("updateEvent");

    // Click on the Actions dropdown
    cy.get('[aria-haspopup="true"]').eq(0).click();
    cy.get("span").contains("Take Ownership").click();
    cy.wait("@updateEvent").its("state").should("eq", "Complete");
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });
  it("Correctly assigns owner via assign modal and reloads page", () => {
    cy.intercept("PATCH", "/api/event/").as("updateEvent");

    // Click on the Actions dropdown
    cy.get('[aria-haspopup="true"]').eq(0).click();
    cy.get("span").contains("Assign").click();
    cy.get(".p-dropdown-trigger").click();
    cy.get('[aria-label="Analyst Alice"]').click();
    cy.get(".p-dialog-footer > Button").last().click();
    cy.wait("@updateEvent").its("state").should("eq", "Complete");
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });
  it("Correctly adds tags via add tags modal and reloads page", () => {
    cy.intercept("PATCH", "/api/event/").as("updateEvent");
    cy.intercept("POST", "/api/node/tag/").as("addTag");

    // Click on the Actions dropdown
    cy.get('[aria-haspopup="true"]').eq(0).click();
    cy.get("span").contains("Add Tags").click();
    cy.get(".p-chips > .p-inputtext").click().type("TestTag").type("{enter}");
    cy.get(".p-dialog-footer > Button").last().click();
    cy.wait("@addTag").its("state").should("eq", "Complete");
    cy.wait("@updateEvent").its("state").should("eq", "Complete");
    cy.wait("@getEvent").its("state").should("eq", "Complete");
    cy.get(".p-tag").should("be.visible");
    cy.get(".p-tag > .tag").should("have.text", "TestTag");
  });
  it("Correctly edits event via edit event modal and reloads page", () => {
    cy.intercept("PATCH", "/api/event/").as("updateEvent");
    cy.intercept("GET", "/api/event/prevention_tool/?offset=0").as(
      "eventPreventionTool",
    );
    cy.intercept("GET", "/api/event/remediation/?offset=0").as(
      "eventRemediation",
    );
    cy.intercept("GET", "/api/event/risk_level/?offset=0").as("eventRiskLevel");
    cy.intercept("GET", "/api/event/status/?offset=0").as("eventStatus");
    cy.intercept("GET", "/api/event/type/?offset=0").as("eventType");
    cy.intercept("GET", "/api/event/vector/?offset=0").as("eventVector");
    cy.intercept("GET", "/api/node/threat_actor/?offset=0").as(
      "nodeThreatActor",
    );
    cy.intercept("GET", "/api/node/threat/?offset=0").as("nodeThreat");
    cy.intercept("GET", "/api/node/threat/type/?offset=0").as("nodeThreatType");
    cy.intercept("GET", "/api/user/?offset=0").as("user");
    cy.intercept("GET", "/api/event/*").as("event");

    // Wait for all of the intercepted calls to complete
    const intercepts = [
      "@eventPreventionTool",
      "@eventRemediation",
      "@eventRiskLevel",
      "@eventStatus",
      "@eventType",
      "@eventVector",
      "@nodeThreatActor",
      "@nodeThreat",
      "@nodeThreatType",
      "@user",
    ];

    // Click on the Actions dropdown
    cy.get('[aria-haspopup="true"]').eq(0).click();
    cy.get("span").contains("Edit Event").click();

    cy.wait(intercepts).then((interceptions) => {
      for (let i = 0; i < interceptions.length; i++) {
        cy.wrap(interceptions[i]).its("state").should("eq", "Complete");
      }
    });
    cy.get('[data-cy="event-name-field"] [data-cy="property-input-value"]')
      .click()
      .clear()
      .type("New Name");
    cy.get('[data-cy="save-edit-event-button"]').click();
    cy.wait("@updateEvent").its("state").should("eq", "Complete");
    cy.wait("@getEvent").its("state").should("eq", "Complete");
    cy.get('[data-cy="event-title"]').should("have.text", "New Name");
  });
});

describe("Event Summary Details", () => {
  let now;
  let nowString;

  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");

    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");

    now = new Date();
    nowString = now.toLocaleString("en-US", { timeZone: "UTC" }).slice(0, -9);
    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "small_template.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");
  });

  it("renders main elements correctly", () => {
    cy.get("#event-summary-timeline").should("be.visible");
    cy.get("#event-summary-table").should("be.visible");
    cy.get("#event-section-title").should("contain.text", "Event Summary");
  });
  it("renders timeline correctly", () => {
    cy.get("#event-summary-timeline").should("be.visible");
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(0)
      .should("have.text", "Event");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(0)
      .should("contains.text", nowString);
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(1)
      .should("have.text", "Alert");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(1)
      .should("contains.text", nowString);
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(2)
      .should("have.text", "Ownership");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(2)
      .should("have.text", "TBD");
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(3)
      .should("have.text", "Disposition");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(3)
      .should("have.text", "TBD");
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(4)
      .should("have.text", "Contain");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(4)
      .should("have.text", "TBD");
    cy.get('[data-cy="event-summary-timeline-label"]')
      .eq(5)
      .should("have.text", "Remediation");
    cy.get('[data-cy="event-summary-timeline-datetime"]')
      .eq(5)
      .should("have.text", "TBD");
  });
  it("renders table correctly", () => {
    cy.get("#event-summary-table").should("be.visible");
    cy.get('[data-cy="table-column-select"]').should("be.visible");
    cy.get(".p-multiselect-label").should(
      "contain.text",
      "Created, Name, Threats, Risk Level, Status, Owner",
    );
    cy.get('[data-cy="reset-table-button"]').should("be.visible");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(0)
      .should("have.text", "Created");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(0)
      .should("contain.text", nowString);
    cy.get(".p-column-header-content > .p-column-title")
      .eq(1)
      .should("have.text", "Name");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(1)
      .should("have.text", "Test Event");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(2)
      .should("have.text", "Threats");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(2)
      .should("contain.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(3)
      .should("have.text", "Risk Level");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(3)
      .should("have.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(4)
      .should("have.text", "Status");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(4)
      .should("have.text", "OPEN");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(5)
      .should("have.text", "Owner");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(5)
      .should("have.text", "None");
  });
  it("allows user to change and reset columns in details table", () => {
    // Open columns selector and select a new column
    cy.get(".p-multiselect-label").click();
    cy.get('[aria-label="Threat Actors"]').click();
    cy.get(".p-menubar").click(); // Click away from column selector
    cy.get(".p-multiselect-label").should(
      "contain.text",
      "Created, Name, Threat Actors, Threats, Risk Level, Status, Owner",
    );
    cy.get(".p-column-header-content > .p-column-title")
      .eq(0)
      .should("have.text", "Created");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(0)
      .should("contain.text", nowString);
    cy.get(".p-column-header-content > .p-column-title")
      .eq(1)
      .should("have.text", "Name");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(1)
      .should("have.text", "Test Event");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(2)
      .should("have.text", "Threat Actors");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(2)
      .should("contain.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(3)
      .should("have.text", "Threats");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(3)
      .should("contain.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(4)
      .should("have.text", "Risk Level");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(4)
      .should("have.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(5)
      .should("have.text", "Status");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(5)
      .should("have.text", "OPEN");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(6)
      .should("have.text", "Owner");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(6)
      .should("have.text", "None");

    // Reset the columns and check they're back to the default
    cy.get('[data-cy="reset-table-button"]').click();
    cy.get(".p-column-header-content > .p-column-title")
      .eq(0)
      .should("have.text", "Created");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(0)
      .should("contain.text", nowString);
    cy.get(".p-column-header-content > .p-column-title")
      .eq(1)
      .should("have.text", "Name");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(1)
      .should("have.text", "Test Event");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(2)
      .should("have.text", "Threats");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(2)
      .should("contain.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(3)
      .should("have.text", "Risk Level");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(3)
      .should("have.text", "None");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(4)
      .should("have.text", "Status");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(4)
      .should("have.text", "OPEN");
    cy.get(".p-column-header-content > .p-column-title")
      .eq(5)
      .should("have.text", "Owner");
    cy.get(".p-datatable-tbody > tr >  > :nth-child(2)")
      .eq(5)
      .should("have.text", "None");
  });
});

describe("Alert Summary Details", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");

    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "small_template.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to alert summary view
    cy.get('[aria-haspopup="true"]').eq(1).click();
    // Select first available analysis type
    cy.get("span").contains("Alert Summary").click();
  });

  it("renders section correctly", () => {
    // Check title
    cy.get("#event-section-title").should("contain.text", "Alert Summary");
    // EventAlertsTable should be there
    cy.get('[data-cy="event-alerts-table"]').should("be.visible");
    // Check that correct alert is there (and there is only one)
    cy.get('[data-cy="alertName"] > a').should("have.text", "Manual Alert 0");
  });

  // Other event alerts table tests are covered in EventTable E2E tests
});

describe("URL Summary Details", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");
    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");
    cy.intercept("POST", "/api/node/tree/observable").as("getObservables");

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "smallWithUrls.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to alert summary view
    cy.get('[aria-haspopup="true"]').eq(1).click();
    // Select first available analysis type
    cy.get("span").contains("URL Summary").click();

    cy.wait("@getObservables").its("state").should("eq", "Complete");
  });

  it("renders section correctly", () => {
    // Check title
    cy.get("#event-section-title").should("contain.text", "URL Summary");
    // url list should be there
    cy.get('[data-cy="url-observable-listbox"]').should("be.visible");
    // Check that url observables are there in correct order
    cy.get(".p-listbox-item").should("have.length", 3);
    cy.get(".p-listbox-item").eq(0).should("have.text", "http://amazon.com/");
    cy.get(".p-listbox-item")
      .eq(1)
      .should("have.text", "http://evil.com/malware.exe");
    cy.get(".p-listbox-item")
      .eq(2)
      .should("have.text", "http://notEvil.com/safe.exe");
  });
  it("selects and highlights last clicked url observable", () => {
    // None highlighted to start
    cy.get(".p-listbox-item").eq(0).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(1).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(2).should("not.have.class", "p-highlight");

    // Click the first
    cy.get(".p-listbox-item").eq(0).click();
    cy.get(".p-listbox-item").eq(0).should("have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(1).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(2).should("not.have.class", "p-highlight");

    // Click the second
    cy.get(".p-listbox-item").eq(1).click();
    cy.get(".p-listbox-item").eq(0).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(1).should("have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(2).should("not.have.class", "p-highlight");

    // Click the third
    cy.get(".p-listbox-item").eq(2).click();
    cy.get(".p-listbox-item").eq(0).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(1).should("not.have.class", "p-highlight");
    cy.get(".p-listbox-item").eq(2).should("have.class", "p-highlight");
  });
});

describe("Observable Summary Details - Affect State", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");
    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");
    cy.intercept("GET", "/api/event/*/summary/observable").as(
      "getObservableSummary",
    );

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "smallWithUrls.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to alert summary view
    cy.get('[aria-haspopup="true"]').eq(1).click();
    // Select first available analysis type
    cy.get("span").contains("Observable Summary").click();

    cy.wait("@getObservableSummary").its("state").should("eq", "Complete");
  });

  it("correctly updates observables for detection status when 'Save Detection Status' button clicked", () => {
    cy.intercept("PATCH", "/api/observable/*").as("updateObservable");
    // Select the first two observables and de-select the third (already checked)
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(0).click();
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(1).click();
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(2).click();

    // Click the save button
    cy.get("#save-detection-status-button").click();

    // 3 calls for each of the changed observables
    cy.wait("@updateObservable").its("state").should("eq", "Complete");
    cy.wait("@updateObservable").its("state").should("eq", "Complete");
    cy.wait("@updateObservable").its("state").should("eq", "Complete");

    // CAll to update the table
    cy.wait("@getObservableSummary").its("state").should("eq", "Complete");

    // Check classes
    cy.get("tr").eq(0).should("not.have.class", "p-highlight");
    cy.get("tr").eq(1).should("not.have.class", "p-highlight");
    cy.get("tr").eq(2).should("have.class", "p-highlight");
    cy.get("tr").eq(3).should("have.class", "p-highlight");
    cy.get("tr").eq(4).should("not.have.class", "p-highlight");
    cy.get("tr").eq(5).should("not.have.class", "p-highlight");
    cy.get("tr").eq(6).should("not.have.class", "p-highlight");
    cy.get("tr").eq(7).should("not.have.class", "p-highlight");
    cy.get("tr").eq(8).should("not.have.class", "p-highlight");

    cy.get("tr").eq(0).should("not.have.class", "low-hits");
    cy.get("tr").eq(1).should("not.have.class", "low-hits");
    cy.get("tr").eq(2).should("not.have.class", "low-hits");
    cy.get("tr").eq(3).should("not.have.class", "low-hits");
    cy.get("tr").eq(4).should("not.have.class", "low-hits");
    cy.get("tr").eq(5).should("not.have.class", "low-hits");
    cy.get("tr").eq(6).should("not.have.class", "low-hits");
    cy.get("tr").eq(7).should("have.class", "low-hits");
    cy.get("tr").eq(8).should("not.have.class", "low-hits");

    // Check checkboxes
    cy.get(".p-datatable-thead .p-checkbox .p-checkbox-box").should(
      "not.be.visible",
    ); // header checkbox should not be visible
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(0)
      .should("have.attr", "aria-checked", "true");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(1)
      .should("have.attr", "aria-checked", "true");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(2)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(3)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(4)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(5)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(6)
      .should("have.attr", "aria-checked", "false");
  });
});
describe("Observable Summary Details - Don't Affect State", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");
    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");
    cy.intercept("GET", "/api/event/*/summary/observable").as(
      "getObservableSummary",
    );

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "smallWithUrls.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to alert summary view
    cy.get('[aria-haspopup="true"]').eq(1).click();
    // Select first available analysis type
    cy.get("span").contains("Observable Summary").click();

    cy.wait("@getObservableSummary").its("state").should("eq", "Complete");
  });

  it("renders section correctly", () => {
    // Check title
    cy.get("#event-section-title").should("contain.text", "Observable Summary");

    // Check table
    cy.get('[data-cy="observables-table"]').should("be.visible");
    cy.get(".p-column-title").should("have.length", 5);
    cy.get(".p-column-title").eq(0).should("have.text", "For Detection");
    cy.get(".p-column-title").eq(1).should("have.text", "FAQueue Hits");
    cy.get(".p-column-title").eq(2).should("have.text", "Type");
    cy.get(".p-column-title").eq(3).should("have.text", "Value");
    cy.get(".p-column-title").eq(4).should("have.text", "Tags");
    cy.get(".p-paginator").should("be.visible");

    // Check all buttons / filters are visible
    cy.get("#save-detection-status-button").should("be.visible");
    cy.get("#select-low-hits-button").should("be.visible");
    cy.get("#reset-selected-observables-button").should("be.visible");
    cy.get("#toggle-max-hits-button").should("be.visible");
    cy.get('[data-cy="observable-type-filter-multiselect"]').should(
      "be.visible",
    );
    cy.get(
      '[data-cy="observable-type-filter-multiselect"] .p-multiselect-label',
    ).should("have.text", "Any");
    cy.get('[data-cy="observable-value-filter-input"]').should("be.visible");
    cy.get('[data-cy="observable-value-filter-input"]').should(
      "have.attr",
      "placeholder",
      "Search by value",
    );

    // Check table content

    // Check there are the right number of rows and they are styled correctly
    cy.get("tr").should("have.length", 9); //  1 header row + 1 filter/button row + 7 observable rows
    cy.get("tr").eq(0).should("not.have.class", "p-highlight");
    cy.get("tr").eq(1).should("not.have.class", "p-highlight");
    cy.get("tr").eq(2).should("not.have.class", "p-highlight");
    cy.get("tr").eq(3).should("not.have.class", "p-highlight");
    cy.get("tr").eq(4).should("have.class", "p-highlight");
    cy.get("tr").eq(5).should("not.have.class", "p-highlight");
    cy.get("tr").eq(6).should("not.have.class", "p-highlight");
    cy.get("tr").eq(7).should("not.have.class", "p-highlight");
    cy.get("tr").eq(8).should("not.have.class", "p-highlight");

    cy.get("tr").eq(0).should("not.have.class", "low-hits");
    cy.get("tr").eq(1).should("not.have.class", "low-hits");
    cy.get("tr").eq(2).should("not.have.class", "low-hits");
    cy.get("tr").eq(3).should("not.have.class", "low-hits");
    cy.get("tr").eq(4).should("not.have.class", "low-hits");
    cy.get("tr").eq(5).should("not.have.class", "low-hits");
    cy.get("tr").eq(6).should("not.have.class", "low-hits");
    cy.get("tr").eq(7).should("have.class", "low-hits");
    cy.get("tr").eq(8).should("not.have.class", "low-hits");

    // Check checkboxes
    cy.get(".p-datatable-thead .p-checkbox .p-checkbox-box").should(
      "not.be.visible",
    ); // header checkbox should not be visible
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(0)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(1)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(2)
      .should("have.attr", "aria-checked", "true"); // This observable is enabled and should be pre-checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(3)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(4)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(5)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(6)
      .should("have.attr", "aria-checked", "false");

    // Check FAQueue Hits column
    cy.get('[data-cy="faqueue-hits-count"]').should("have.length", 7);
    cy.get('[data-cy="faqueue-external-link"]').should("have.length", 7);
    cy.get('[data-cy="faqueue-hits-count"]').eq(0).should("have.text", 5);
    cy.get('[data-cy="faqueue-hits-count"]').eq(1).should("have.text", 100);
    cy.get('[data-cy="faqueue-hits-count"]').eq(2).should("have.text", 10);
    cy.get('[data-cy="faqueue-hits-count"]').eq(3).should("have.text", 1000);
    cy.get('[data-cy="faqueue-hits-count"]').eq(4).should("have.text", 20);
    cy.get('[data-cy="faqueue-hits-count"]').eq(5).should("have.text", 0);
    cy.get('[data-cy="faqueue-hits-count"]').eq(6).should("have.text", 5);

    // Check Type column
    cy.get(".p-datatable-tbody > > :nth-child(3)").should("have.length", 7);
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(0)
      .should("have.text", "email_address");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(1)
      .should("have.text", "email_subject");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(2)
      .should("have.text", "fqdn");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(3)
      .should("have.text", "ipv4");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(4)
      .should("have.text", "uri_path");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(5)
      .should("have.text", "url");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .eq(6)
      .should("have.text", "url");

    // Check Value column
    cy.get(".p-datatable-tbody > > :nth-child(4)").should("have.length", 7);
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(0)
      .should("have.text", "badguy@evil.com");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(1)
      .should("have.text", "Hello");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(2)
      .should("have.text", "evil.com");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(3)
      .should("have.text", "127.0.0.1");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(4)
      .should("have.text", "/malware.exe");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(5)
      .should("have.text", "http://amazon.com/");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .eq(6)
      .should("have.text", "http://evil.com/malware.exe");

    // Check Tags column
    cy.get(".p-datatable-tbody > > :nth-child(5)").should("have.length", 7);
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(0)
      .should("have.text", "from_address");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(1)
      .should("have.text", "");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(2)
      .should("have.text", "");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(3)
      .should("have.text", "c2contacted_host");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(4)
      .should("have.text", "");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(5)
      .should("have.text", "");
    cy.get(".p-datatable-tbody > > :nth-child(5)")
      .eq(6)
      .should("have.text", "");

    // Check that the tags themselves are formatted as tags
    cy.get(".p-tag").should("have.length", 3);
    cy.get(".p-tag").eq(0).should("have.text", "from_address");
    cy.get(".p-tag").eq(1).should("have.text", "c2");
    cy.get(".p-tag").eq(2).should("have.text", "contacted_host");
  });
  it("correctly selects observables with low hits when 'Select low hits' button clicked ", () => {
    cy.get("#select-low-hits-button").click();

    // Check classes
    cy.get("tr").eq(0).should("not.have.class", "p-highlight");
    cy.get("tr").eq(1).should("not.have.class", "p-highlight");
    cy.get("tr").eq(2).should("not.have.class", "p-highlight");
    cy.get("tr").eq(3).should("not.have.class", "p-highlight");
    cy.get("tr").eq(4).should("have.class", "p-highlight"); // This row will stay selected/highlighted
    cy.get("tr").eq(5).should("not.have.class", "p-highlight");
    cy.get("tr").eq(6).should("not.have.class", "p-highlight");
    cy.get("tr").eq(7).should("have.class", "p-highlight"); // Will have the highlighted class now that it is selected
    cy.get("tr").eq(8).should("not.have.class", "p-highlight");

    cy.get("tr").eq(0).should("not.have.class", "low-hits");
    cy.get("tr").eq(1).should("not.have.class", "low-hits");
    cy.get("tr").eq(2).should("not.have.class", "low-hits");
    cy.get("tr").eq(3).should("not.have.class", "low-hits");
    cy.get("tr").eq(4).should("not.have.class", "low-hits");
    cy.get("tr").eq(5).should("not.have.class", "low-hits");
    cy.get("tr").eq(6).should("not.have.class", "low-hits");
    cy.get("tr").eq(7).should("have.class", "low-hits");
    cy.get("tr").eq(8).should("not.have.class", "low-hits");

    // Check checkboxes
    cy.get(".p-datatable-thead .p-checkbox .p-checkbox-box").should(
      "not.be.visible",
    ); // header checkbox should not be visible
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(0)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(1)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(2)
      .should("have.attr", "aria-checked", "true"); // This observable is enabled and will stay checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(3)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(4)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(5)
      .should("have.attr", "aria-checked", "true"); // This observable will now be checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(6)
      .should("have.attr", "aria-checked", "false");

    // Reset newly selected checkbox
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(5).click();
  });

  it("correctly resets selected observables when 'Reset' button clicked", () => {
    // Click a couple of other rows
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(1).click();
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box").eq(5).click();

    // Check classes
    cy.get("tr").eq(0).should("not.have.class", "p-highlight");
    cy.get("tr").eq(1).should("not.have.class", "p-highlight");
    cy.get("tr").eq(2).should("not.have.class", "p-highlight");
    cy.get("tr").eq(3).should("have.class", "p-highlight");
    cy.get("tr").eq(4).should("have.class", "p-highlight"); // This row will stay selected/highlighted
    cy.get("tr").eq(5).should("not.have.class", "p-highlight");
    cy.get("tr").eq(6).should("not.have.class", "p-highlight");
    cy.get("tr").eq(7).should("have.class", "p-highlight"); // Will have the highlighted class now that it is selected
    cy.get("tr").eq(8).should("not.have.class", "p-highlight");

    cy.get("tr").eq(0).should("not.have.class", "low-hits");
    cy.get("tr").eq(1).should("not.have.class", "low-hits");
    cy.get("tr").eq(2).should("not.have.class", "low-hits");
    cy.get("tr").eq(3).should("not.have.class", "low-hits");
    cy.get("tr").eq(4).should("not.have.class", "low-hits");
    cy.get("tr").eq(5).should("not.have.class", "low-hits");
    cy.get("tr").eq(6).should("not.have.class", "low-hits");
    cy.get("tr").eq(7).should("have.class", "low-hits");
    cy.get("tr").eq(8).should("not.have.class", "low-hits");

    // Check checkboxes
    cy.get(".p-datatable-thead .p-checkbox .p-checkbox-box").should(
      "not.be.visible",
    ); // header checkbox should not be visible
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(0)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(1)
      .should("have.attr", "aria-checked", "true");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(2)
      .should("have.attr", "aria-checked", "true"); // This observable is enabled and will stay checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(3)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(4)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(5)
      .should("have.attr", "aria-checked", "true"); // This observable will now be checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(6)
      .should("have.attr", "aria-checked", "false");

    cy.get("#reset-selected-observables-button").click();

    // Check again, should be back to default
    cy.get("tr").eq(0).should("not.have.class", "p-highlight");
    cy.get("tr").eq(1).should("not.have.class", "p-highlight");
    cy.get("tr").eq(2).should("not.have.class", "p-highlight");
    cy.get("tr").eq(3).should("not.have.class", "p-highlight");
    cy.get("tr").eq(4).should("have.class", "p-highlight");
    cy.get("tr").eq(5).should("not.have.class", "p-highlight");
    cy.get("tr").eq(6).should("not.have.class", "p-highlight");
    cy.get("tr").eq(7).should("not.have.class", "p-highlight");
    cy.get("tr").eq(8).should("not.have.class", "p-highlight");

    cy.get("tr").eq(0).should("not.have.class", "low-hits");
    cy.get("tr").eq(1).should("not.have.class", "low-hits");
    cy.get("tr").eq(2).should("not.have.class", "low-hits");
    cy.get("tr").eq(3).should("not.have.class", "low-hits");
    cy.get("tr").eq(4).should("not.have.class", "low-hits");
    cy.get("tr").eq(5).should("not.have.class", "low-hits");
    cy.get("tr").eq(6).should("not.have.class", "low-hits");
    cy.get("tr").eq(7).should("have.class", "low-hits");
    cy.get("tr").eq(8).should("not.have.class", "low-hits");

    // Check checkboxes
    cy.get(".p-datatable-thead .p-checkbox .p-checkbox-box").should(
      "not.be.visible",
    ); // header checkbox should not be visible
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(0)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(1)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(2)
      .should("have.attr", "aria-checked", "true"); // This observable is enabled and should be pre-checked
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(3)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(4)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(5)
      .should("have.attr", "aria-checked", "false");
    cy.get(".p-selection-column > .p-checkbox > .p-checkbox-box")
      .eq(6)
      .should("have.attr", "aria-checked", "false");
  });
  it("correctly hides and shows rows with high FAQueue Hits when toggle button clicked", () => {
    cy.get("#toggle-max-hits-button").should("have.text", "Hide Max Hits");
    cy.get("#toggle-max-hits-button > .pi").should(
      "have.class",
      "pi-eye-slash",
    );
    cy.get("#toggle-max-hits-button").click();
    // Should only be 8 rows now, 1 will have been hidden
    cy.get("tr").should("have.length", 8);
    cy.get("#toggle-max-hits-button").should("have.text", "Show Max Hits");
    cy.get("#toggle-max-hits-button > .pi").should("have.class", "pi-eye");
    cy.get('[data-cy="faqueue-hits-count"]')
      .contains("1000")
      .should("not.exist");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .contains("ipv4")
      .should("not.exist");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .contains("127.0.0.1")
      .should("not.exist");
    cy.get("#toggle-max-hits-button").click();
    cy.get("tr").should("have.length", 9);
    cy.get("#toggle-max-hits-button").should("have.text", "Hide Max Hits");
    cy.get("#toggle-max-hits-button > .pi").should(
      "have.class",
      "pi-eye-slash",
    );
    cy.get('[data-cy="faqueue-hits-count"]')
      .contains("1000")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .contains("ipv4")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .contains("127.0.0.1")
      .should("be.visible");
  });
  it("correctly filters by observable type when selected", () => {
    cy.get('[data-cy="observable-type-filter-multiselect"]').click();
    cy.get('[aria-label="email_address"]').click();
    // Should only be 3 rows now, 2 headers and 1 email_address observable
    cy.get("tr").should("have.length", 3);
    cy.get('[data-cy="faqueue-hits-count"]').contains("5").should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .contains("email_address")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .contains("badguy@evil.com")
      .should("be.visible");
    // Click to add another observable type filter and remove the old, this one will have no results
    cy.get('[aria-label="email_address"]').click();
    cy.get('[aria-label="file"]').click();
    cy.get("tr").should("have.length", 3);
    cy.get("td").contains("No observables found.").should("be.visible");
    // Click the remove filter button, all rows should be visible again
    cy.get(".p-column-filter-clear-button").eq(2).click();
    cy.get("tr").should("have.length", 9);
  });
  it("correctly filters by observable value when typing", () => {
    cy.get('[data-cy="observable-value-filter-input"]').click().type("He");
    // Should only be 3 rows now, 2 headers and 3 "H" observable
    cy.get("tr").should("have.length", 3);
    cy.get('[data-cy="faqueue-hits-count"]')
      .contains("100")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .contains("email_subject")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .contains("Hello")
      .should("be.visible");
    // Click the remove filter button, all rows should be visible again
    cy.get(".p-column-filter-clear-button").eq(3).click();
    cy.get("tr").should("have.length", 9);
  });
  it("correctly sorts by observable value when typing", () => {
    cy.get('[data-cy="observable-value-filter-input"]').click().type("He");
    // Should only be 3 rows now, 2 headers and 3 "H" observable
    cy.get("tr").should("have.length", 3);
    cy.get('[data-cy="faqueue-hits-count"]')
      .contains("100")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(3)")
      .contains("email_subject")
      .should("be.visible");
    cy.get(".p-datatable-tbody > > :nth-child(4)")
      .contains("Hello")
      .should("be.visible");
    // Click the remove filter button, all rows should be visible again
    cy.get(".p-column-filter-clear-button").eq(3).click();
    cy.get("tr").should("have.length", 9);
  });
});

describe("User Summary Details", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");
    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");
    cy.intercept("GET", "/api/event/*/summary/user").as("getUserSummary");

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "smallWithUsers.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to user analysis view
    cy.get('[aria-haspopup="true"]').eq(2).click();
    cy.get("span").contains("User Analysis").click();

    cy.wait("@getUserSummary").its("state").should("eq", "Complete");
  });

  it("renders section correctly", () => {
    // Check title
    cy.get("#event-section-title").should("contain.text", "User Analysis");
    // url list should be there
    cy.get('[data-cy="user-analysis-table"]').should("be.visible");
    // Should be 3 rows, one header and two users
    cy.get("tr").should("have.length", 3);
    // Check headers
    cy.get(".p-column-title").eq(0).should("have.text", "User ID");
    cy.get(".p-column-title").eq(1).should("have.text", "Email");
    cy.get(".p-column-title").eq(2).should("have.text", "Company");
    cy.get(".p-column-title").eq(3).should("have.text", "Division");
    cy.get(".p-column-title").eq(4).should("have.text", "Department");
    cy.get(".p-column-title").eq(5).should("have.text", "Title");
    cy.get(".p-column-title").eq(6).should("have.text", "Manager Email");
    // Check values of first row
    // If this row looks good, we can reliably say any other rows will load correctly
    // AKA don't need to check second row
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(0)
      .should("have.text", "12345");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(1)
      .should("have.text", "goodguy@company.com");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(2)
      .should("have.text", "Company Inc.");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(3)
      .should("have.text", "R&D");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(4)
      .should("have.text", "Widgets");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(5)
      .should("have.text", "Director");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(6)
      .should("have.text", "ceo@company.com");
  });
});

describe("URL Domain Summary Details", () => {
  before(() => {
    cy.resetDatabase();
    cy.login();

    // Intercept the API call that loads the event data
    cy.intercept("GET", "/api/event/*").as("getEvent");
    cy.intercept(
      "GET",
      "/api/event/?sort=created_time%7Cdesc&limit=10&offset=0",
    ).as("getEventsDefaultRows");
    cy.intercept("GET", "/api/event/*/summary/url_domain").as(
      "getUrlDomainSummary",
    );

    // Add the test event to the database
    cy.request({
      method: "POST",
      url: "/api/test/add_event",
      body: {
        alert_template: "smallWithUrls.json",
        alert_count: 1,
        name: "Test Event",
      },
    });

    visitUrl({
      url: "/manage_events",
      extraIntercepts: ["@getEventsDefaultRows"],
    });
    cy.get('[data-cy="eventName"] > a').click();
    cy.wait("@getEvent").its("state").should("eq", "Complete");

    // Switch to user analysis view
    cy.get('[aria-haspopup="true"]').eq(1).click();
    cy.get("span").contains("URL Domain Summary").click();

    cy.wait("@getUrlDomainSummary").its("state").should("eq", "Complete");
  });

  it("renders section correctly", () => {
    // Check title
    cy.get("#event-section-title").should("contain.text", "URL Domain Summary");
    // pie chart should be there
    cy.get('[data-cy="url-domain-pie-chart"]').should("be.visible");
    // table should be there
    cy.get('[data-cy="url-domain-summary-table"]');
    // Should be 4 rows, one header and three domains
    cy.get("tr").should("have.length", 4);
    // Check headers
    cy.get(".p-column-title").eq(0).should("have.text", "Domain");
    cy.get(".p-column-title").eq(1).should("have.text", "Count");
    // Check values of first row
    // If this row looks good, we can reliably say any other rows will load correctly
    // AKA don't need to check second row
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(0)
      .should("have.text", "amazon.com");
    cy.get(".p-datatable-tbody > :nth-child(1) > td")
      .eq(1)
      .should("have.text", "1");
  });
});
