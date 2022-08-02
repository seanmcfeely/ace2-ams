import { mount } from "@cypress/vue";
import PrimeVue from "primevue/config";
import router from "@/router";
import authApi from "@/services/api/auth";
import { useAuthStore } from "@/stores/auth";

import App from "@/App.vue";
import { createCustomCypressPinia } from "@tests/cypressHelpers";
import { userReadFactory } from "@mocks/user";
import Tooltip from "primevue/tooltip";
import ToastService from "primevue/toastservice";

const factory = (isAuthenticated = false) => {
  const user = isAuthenticated ? userReadFactory() : null;
  mount(App, {
    global: {
      directives: { tooltip: Tooltip },
      plugins: [
        PrimeVue,
        createCustomCypressPinia({
          initialState: {
            authStore: {
              user: user,
            },
          },
        }),
        router,
        ToastService,
      ],
    },
  });
};

describe("App", () => {
  it("does not reroute if login is validated", () => {
    const stub = cy.stub(authApi, "validate").resolves();
    factory(true);
    cy.wait(61000);
    cy.wrap(stub).should("be.called");
    cy.url().should("not.contain", "/login");
  });
  it("reroutes to /login if login is not validated", () => {
    const _validate = async () => {
      const authStore = useAuthStore();
      authStore.$reset();
      throw new Error("401 auth failed");
    };
    const stub = cy.stub(authApi, "validate").callsFake(_validate);
    cy.wait(61000);
    factory();
    cy.wrap(stub).should("be.called");
    cy.url().should("contain", "/login");
  });
});
