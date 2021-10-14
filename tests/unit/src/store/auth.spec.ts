import Cookies from "js-cookie";
import Vuex from "vuex";

import auth from "../../../../src/store/auth";

const getters = auth.getters;

const mockAuthenticatedUntil = "1111111111.111111";

class State {
  authenticated_until = 0;
  isLoggedIn = false;
}

describe("auth Getters", () => {
  it("will return isLoggedIn and authenticated_until state when not logged in", () => {
    // Mock out the response when getting the "authenticated_until" cookie value
    Cookies.get = jest.fn().mockImplementation(() => undefined);

    const state = new State();
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["isLoggedIn"]).toStrictEqual(false);
    expect(store.getters["authenticatedUntil"]).toStrictEqual(0);
  });

  it("will return isLoggedIn and authenticated_until state when logged in", () => {
    // Mock out the response when getting the "authenticated_until" cookie value
    Cookies.get = jest.fn().mockImplementation(() => mockAuthenticatedUntil);

    const state = new State();
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["isLoggedIn"]).toStrictEqual(true);
    expect(store.getters["authenticatedUntil"]).toStrictEqual(
      parseFloat(mockAuthenticatedUntil),
    );
  });
});
