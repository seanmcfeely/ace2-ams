import { mount } from "@cypress/vue";
import PrimeVue from "primevue/config";
import router from "@/router/index";

import TheLogin from "@/pages/User/TheLogin.vue";
import authApi from "@/services/api/auth";
import { createCustomCypressPinia } from "@tests/cypressHelpers";

const factory = () => {
  mount(TheLogin, {
    global: {
      plugins: [PrimeVue, createCustomCypressPinia(), router],
    },
  });
};

describe("TheLogin", () => {
  it("renders", () => {
    factory();
  });
  it("doesn't display error if login successful", () => {
    const stub = cy.stub(authApi, "authenticate").resolves();
    factory();
    cy.get("#username").type("user");
    cy.get("#password").type("pass");
    cy.contains("Log In").click();
    cy.contains("Invalid username or password").should("not.exist");
    cy.wrap(stub).should("be.called");
  });
  it("displays an error message if login fails", () => {
    const stub = cy
      .stub(authApi, "authenticate")
      .rejects(new Error("401 auth failed"));
    factory();
    cy.get("#username").type("user");
    cy.get("#password").type("pass");
    cy.contains("Log In").click();
    cy.contains("Invalid username or password").should("be.visible");
    cy.wrap(stub).should("be.called");
  });
});
