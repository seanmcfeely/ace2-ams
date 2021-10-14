import Vuex from "vuex";
import auth from "@/store/auth";
import myNock from "../services/api/nock";
const actions = auth.actions;
const mutations = auth.mutations;
const getters = auth.getters;

describe("auth Getters", () => {
  it("will return loggedIn state boolean when false", () => {
    const loggedIn = false;
    const state = { loggedIn: loggedIn };
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["loggedIn"]).toStrictEqual(false);
  });
  it("will return loggedIn state boolean when true", () => {
    const loggedIn = true;
    const state = { loggedIn: loggedIn };
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["loggedIn"]).toStrictEqual(true);
  });
});

describe("auth Mutations", () => {
  it("will set loggedIn to the given boolean", () => {
    const loggedIn = false;
    const state = { loggedIn: loggedIn };
    const store = new Vuex.Store({ state, getters, mutations });

    expect(store.getters["loggedIn"]).toStrictEqual(false);
    store.commit("SET_LOGGEDIN", true);
    expect(store.getters["loggedIn"]).toStrictEqual(true);
    store.commit("SET_LOGGEDIN", false);
    expect(store.getters["loggedIn"]).toStrictEqual(false);
  });
});

describe("auth Actions", () => {
  const authHeaders = {
    "access-control-allow-headers": "Authorization",
  };
  beforeEach(() => {
    myNock.options("/auth").reply(200, "options", authHeaders);
  });

  it("will set loggedIn to true upon successful login action", async () => {
    const loggedIn = false;
    const state = { loggedIn: loggedIn };
    const store = new Vuex.Store({ state, getters, mutations, actions });
    const mockRequest = myNock.post("/auth").reply(
      200,
      {
        access_token: "abcd1234",
        refresh_token: "1234abcd",
        token_type: "bearer",
      },
      authHeaders,
    );

    expect(state.loggedIn).toEqual(false);
    await store.dispatch("login");
    expect(mockRequest.isDone()).toEqual(true);
    expect(state.loggedIn).toEqual(true);
  });

  it("will throw an error and set loggedIn to false if the login action fails", async () => {
    const loggedIn = false;
    const state = { loggedIn: loggedIn };
    const store = new Vuex.Store({ state, getters, mutations, actions });
    myNock.post("/auth").reply(401, "Login failed :(", authHeaders);

    await expect(store.dispatch("login")).rejects.toEqual(
      new Error("Request failed with status code 401"),
    );
  });
});
