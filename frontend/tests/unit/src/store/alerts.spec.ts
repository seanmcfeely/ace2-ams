/**
 * @jest-environment node
 */

import Vuex from "vuex";
import alerts from "@/store/alerts";
import { parseAlertSummary } from "@/store/alerts";
import myNock from "@unit/services/api/nock";
import snakecaseKeys from "snakecase-keys";

const actions = alerts.actions;
const getters = alerts.getters;
const mutations = alerts.mutations;

const mockAlertCreate = {
  queue: "default",
  type: "MockType",
  uuid: "uuid1",
  version: "VersionId1",
  eventTime: new Date(0),
  name: "mockAlert",
};

const mockAlert = {
  comments: [],
  description: "A test alert",
  disposition: "",
  dispositionTime: Date(),
  dispositionUser: "",
  eventTime: Date(),
  insertTime: Date(),
  name: "Test Alert",
  observables: [],
  owner: "Analyst",
  queue: "Default",
  tags: [],
  tool: "GUI",
  type: "Manual",
  uuid: "uuid1",
};

const mockAPIAlert = {
  comments: [{ value: "A comment", description: "comment", uuid: "uuid1" }],
  description: "A test alert",
  disposition: { value: "False Positive", description: "fp", uuid: "uuid1" },
  dispositionTime: new Date(0),
  dispositionUser: { value: "Analyst", description: "user", uuid: "uuid1" },
  eventTime: new Date(0),
  insertTime: new Date(0),
  name: "Test Alert",
  analysis: { discoveredObservableUuids: ["obsUuid1"] },
  owner: { value: "Analyst", description: "user", uuid: "uuid1" },
  queue: { value: "Default", description: "queue", uuid: "uuid1" },
  tags: [{ value: "a tag", description: "tag", uuid: "uuid1" }],
  tool: { value: "GUI", description: "tool", uuid: "uuid1" },
  type: { value: "Manual", description: "type", uuid: "uuid1" },
  uuid: "uuid1",
};

describe("alerts utilities", () => {
  it("will use default values when parsing an API alert object that has missing properties", () => {
    expect(parseAlertSummary({ uuid: "uuid1" })).toStrictEqual({
      comments: [],
      description: "",
      disposition: "OPEN",
      dispositionTime: null,
      dispositionUser: "None",
      eventTime: null,
      insertTime: null,
      name: "Unnamed",
      observables: [],
      owner: "None",
      queue: "None",
      tags: [],
      tool: "None",
      type: "",
      uuid: "uuid1",
    });
  });
  it("will use the available values when parsing an API alert object with all optional properties", () => {
    expect(parseAlertSummary(mockAPIAlert)).toStrictEqual({
      comments: [{ value: "A comment", description: "comment", uuid: "uuid1" }],
      description: "A test alert",
      disposition: "False Positive",
      dispositionTime: new Date(0),
      dispositionUser: "Analyst",
      eventTime: new Date(0),
      insertTime: new Date(0),
      name: "Test Alert",
      observables: ["obsUuid1"],
      owner: "Analyst",
      queue: "Default",
      tags: [{ value: "a tag", description: "tag", uuid: "uuid1" }],
      tool: "GUI",
      type: { value: "Manual", description: "type", uuid: "uuid1" },
      uuid: "uuid1",
    });
  });
});

describe("alerts Mutations", () => {
  it("will set the openAlert state value to a given alert object", () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations });

    store.commit("SET_OPEN_ALERT", mockAlert);
    expect(state.openAlert).toEqual(mockAlert);
  });
  it("will add a list of queried alerts to the queriedAlerts list", () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations });

    store.commit("SET_QUERIED_ALERTS", [mockAlert, mockAlert]);
    expect(state.queriedAlerts.length).toBe(2);
  });
});

describe("alerts Actions", () => {
  it("will request to create an alert with a given AlertCreate object, and set the openAlert to result on success", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(mockAlertCreate)))
      .reply(200, mockAlert);

    await store.dispatch("createAlert", mockAlertCreate);

    expect(mockRequest.isDone()).toEqual(true);
    expect(state.openAlert).toEqual(mockAlert);
  });

  it("will fetch alert data given an alert ID", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock.get("/alert/uuid1").reply(200, mockAlert);
    await store.dispatch("getSingle", "uuid1");

    expect(mockRequest.isDone()).toEqual(true);

    expect(state.openAlert).toEqual(mockAlert);
  });

  it("will fetch all alerts when getAll is called and no filter options are set", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock
      .get("/alert/")
      .reply(200, { items: [{ uuid: "uuid1" }, { uuid: "uuid2" }] });
    await store.dispatch("getAll");

    expect(mockRequest.isDone()).toEqual(true);

    expect(state.openAlert).toBeNull();
    expect(state.queriedAlerts).toHaveLength(2);
  });

  it("will make a request to update an alert given the UUID and update data upon the updateAlert action", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock.patch("/alert/uuid1").reply(200);
    await store.dispatch("updateAlert", {
      oldAlertUUID: "uuid1",
      updateData: { disposition: "test" },
    });

    expect(mockRequest.isDone()).toEqual(true);
    // None of these should be changed
    expect(state.openAlert).toBeNull();
    expect(state.queriedAlerts).toEqual([]);
  });

  it("will make multiple reqs to update multiple alerts given a list of UUIDS and update data upon the updateAlerts action", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock
      .patch(/\/alert\/uuid\d/)
      .twice()
      .reply(200);
    await store.dispatch("updateAlerts", {
      oldAlertUUIDs: ["uuid1", "uuid2"],
      updateData: { disposition: "test" },
    });

    expect(mockRequest.isDone()).toEqual(true);
    // None of these should be changed
    expect(state.openAlert).toBeNull();
    expect(state.queriedAlerts).toEqual([]);
  });

  it("will throw an error when a request fails in any action", async () => {
    const state = {
      openAlert: null,
      queriedAlerts: [],
    };
    const store = new Vuex.Store({ state, mutations, actions });
    const mockRequest = myNock
      .persist()
      .post(/\/alert\/*/)
      .reply(403, "Bad request :(")
      .get(/\/alert\/*/)
      .reply(403, "Bad request :(")
      .patch(/\/alert\/*/)
      .reply(403, "Bad request :(");

    await expect(store.dispatch("createAlert")).rejects.toEqual(
      new Error("Request failed with status code 403"),
    );
    await expect(store.dispatch("getSingle")).rejects.toEqual(
      new Error("Request failed with status code 403"),
    );
    await expect(
      store.dispatch("updateAlert", {
        oldAlertUUID: "uuid1",
        updateData: { disposition: "test" },
      }),
    ).rejects.toEqual(new Error("Request failed with status code 403"));
    await expect(
      store.dispatch("updateAlerts", {
        oldAlertUUIDs: ["uuid1"],
        updateData: { disposition: "test" },
      }),
    ).rejects.toEqual(new Error("Request failed with status code 403"));

    mockRequest.persist(false); // cleanup persisted nock request
  });
});
