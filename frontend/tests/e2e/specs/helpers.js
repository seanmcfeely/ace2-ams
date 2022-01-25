const pg = require("pg");

const connectionString = process.env.DATABASE_TEST_URL;

const client = new pg.Client({
  connectionString,
});
client.connect();

export function addUser(options) {
  client.query("SELECT NOW()", (err, res) => {
    console.log(err, res);
    client.end();
  });
}

export function visitUrl(options) {
  // Persist the cookies for the duration of the test
  Cypress.Cookies.preserveOnce("access_token", "refresh_token");

  // Intercept the auth refresh call
  cy.intercept("GET", "/api/auth/refresh").as("authRefresh");

  // Intercept all of the populateCommonStores API calls
  cy.intercept("GET", "/api/alert/disposition/?offset=0").as(
    "alertDisposition",
  );
  cy.intercept("GET", "/api/alert/queue/?offset=0").as("alertQueue");
  cy.intercept("GET", "/api/alert/tool/?offset=0").as("alertTool");
  cy.intercept("GET", "/api/alert/tool/instance/?offset=0").as(
    "alertToolInstance",
  );
  cy.intercept("GET", "/api/alert/type/?offset=0").as("alertType");
  cy.intercept("GET", "/api/event/prevention_tool/?offset=0").as(
    "eventPreventionTool",
  );
  cy.intercept("GET", "/api/event/queue/?offset=0").as("eventQueue");
  cy.intercept("GET", "/api/event/risk_level/?offset=0").as("eventRiskLevel");
  cy.intercept("GET", "/api/event/status/?offset=0").as("eventStatus");
  cy.intercept("GET", "/api/event/type/?offset=0").as("eventType");
  cy.intercept("GET", "/api/event/vector/?offset=0").as("eventVector");
  cy.intercept("GET", "/api/node/directive/?offset=0").as("nodeDirective");
  cy.intercept("GET", "/api/observable/type/?offset=0").as("observableType");
  cy.intercept("GET", "/api/user/?offset=0").as("user");

  // Visit the intended URL
  cy.visit(options.url);

  // Wait for all of the intercepted calls to complete
  const intercepts = [
    "@authRefresh",
    "@alertDisposition",
    "@alertQueue",
    "@alertTool",
    "@alertToolInstance",
    "@alertType",
    "@eventPreventionTool",
    "@eventQueue",
    "@eventRiskLevel",
    "@eventStatus",
    "@eventType",
    "@eventVector",
    "@nodeDirective",
    "@observableType",
    "@user",
  ];

  // Also wait for any extra intercepts that were passed in
  if (options.extraIntercepts) {
    intercepts.push.apply(intercepts, options.extraIntercepts);
  }

  cy.wait(intercepts).then((interceptions) => {
    for (let i = 0; i < interceptions.length; i++) {
      cy.wrap(interceptions[i]).its("state").should("eq", "Complete");
    }
  });
}
