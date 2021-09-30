import Vuex from "vuex";
import users from "@/store/users";
import axiosInstance from "@/../services/api/axios";
import {UserRead} from "../../../../models/user";
const actions = users.actions;
const mutations = users.mutations;
const getters = users.getters;

const mockUser = {
  uuid: "id1",
  roles: ["analyst"],
  defaultAlertQueue: "default",
};

describe("users Getters", () => {
  it("will return empty list when no users exist", () => {
    const users: UserRead[] | undefined = [];
    const state = { users: users, lastGetAll: 0 };
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["users"]).toStrictEqual([]);
  });
  it("will return list of IDs currently selected", () => {
    const users = [mockUser];
    const state = { users: users, lastGetAll: null };
    const store = new Vuex.Store({ state, getters });

    expect(store.getters["users"]).toStrictEqual(users);
  });
});

describe("users Mutations", () => {
  it("will add a received list of users to the users list", () => {
    const users: UserRead[] | undefined = [];
    const state = { users: users, lastGetAll: 0 };
    const store = new Vuex.Store({ state, getters, mutations });

    store.commit("SET_USERS", [mockUser, mockUser]);
    expect(state.users.length).toBe(2);
  });
  it("will set the lastGetAll timestamp to the current time", () => {
    const users: UserRead[] | undefined = [];
    const state = { users: users, lastGetAll: 0 };
    const store = new Vuex.Store({ state, getters, mutations });

    const before_time = new Date().getTime();
    store.commit("SET_GET_ALL_TIMESTAMP");
    const after_time = new Date().getTime();
    expect(state.lastGetAll).toBeGreaterThanOrEqual(before_time);
    expect(state.lastGetAll).toBeLessThanOrEqual(after_time);
  });
});

describe("users Actions", () => {
  let mockRequest: jest.SpyInstance;

  beforeEach(() => {
    mockRequest = jest.spyOn(axiosInstance, "request");
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("will fetch users from backend and update state variables upon getAllUsers action", async () => {
    const users: UserRead[] | undefined = [];
    const state = { users: users, lastGetAll: 0 };
    const store = new Vuex.Store({ state, getters, mutations, actions });
    const result = {
      status: 200,
      data: [mockUser, mockUser],
    };
    mockRequest.mockImplementation(() => Promise.resolve(result));

    const before_time = new Date().getTime();
    await store.dispatch("getAllUsers");
    const after_time = new Date().getTime();

    expect(mockRequest).toHaveBeenCalled();
    expect(mockRequest.mock.calls.length).toEqual(1);

    expect(state.users[0]).toEqual(mockUser);
    expect(state.users.length).toEqual(2);

    expect(state.lastGetAll).toBeGreaterThanOrEqual(before_time);
    expect(state.lastGetAll).toBeLessThanOrEqual(after_time);
  });

  it("will throw an error if the call to fetch users fails", async () => {
    const users: UserRead[] | undefined = [];
    const state = { users: users, lastGetAll: 0 };
    const store = new Vuex.Store({ state, getters, mutations, actions });
    const result = {
      status: 403,
      statusText: "mockError",
      data: [mockUser, mockUser],
    };
    mockRequest.mockImplementation(() => Promise.resolve(result));

    await expect(store.dispatch("getAllUsers")).rejects.toEqual(
      new Error("fetch failed: 403: mockError")
    );
  });
});
