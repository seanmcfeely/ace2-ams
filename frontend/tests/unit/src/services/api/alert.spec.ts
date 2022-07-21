import { describe, it, expect } from "vitest";
import { alertCreate, alertFilterParams, alertUpdate } from "@/models/alert";
import { Alert } from "@/services/api/alert";
import myNock from "@unit/services/api/nock";

const MOCK_ALERT_CREATE: alertCreate = {
  alert: true,
  name: "Test",
  queue: "Default",
  type: "test",
  observables: [],
  historyUsername: "analyst",
};

const MOCK_ALERT_UPDATE: alertUpdate = {
  uuid: "uuid",
  historyUsername: "analyst",
};
const MOCK_PARAMS: alertFilterParams = {
  limit: 10,
  offset: 10,
  name: { included: ["Test Name"], notIncluded: [] },
  disposition: {
    included: [
      {
        rank: 0,
        description: null,
        uuid: "1",
        value: "FALSE_POSITIVE",
      },
    ],
    notIncluded: [],
  },
  observableTypes: {
    included: [
      [
        { value: "testA", description: null, uuid: "1" },
        { value: "testB", description: null, uuid: "2" },
      ],
    ],
    notIncluded: [],
  },
  tags: { included: [["tagA", "tagB"]], notIncluded: [] },
  threats: {
    included: [
      [
        {
          value: "threatA",
          description: null,
          queues: [],
          types: [],
          uuid: "1",
        },
        {
          value: "threatB",
          description: null,
          queues: [],
          types: [],
          uuid: "2",
        },
      ],
    ],
    notIncluded: [],
  },
  observable: {
    included: [
      {
        category: { value: "test", description: null, uuid: "1" },
        value: "example",
      },
    ],
    notIncluded: [],
  },
};

describe("Alert calls", () => {
  const api = Alert;

  it("will make a post to the /alert endpoint with alertCreate data when 'create' is called", async () => {
    myNock
      .post("/alert/")
      .reply(200, "Create successful", {
        "content-location": "/newItem",
      })
      .get("/newItem")
      .reply(200, "Read successful");
    const res = await api.createAndRead(MOCK_ALERT_CREATE);
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/{uuid} endpoint when 'read' is called with a given UUID", async () => {
    myNock.get("/alert/uuid").reply(200, "Read successful");
    const res = await api.read("uuid");
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/{uuid}/history endpoint when 'readHistory' is called with a given UUID", async () => {
    myNock.get("/alert/uuid/history").reply(200, "Read successful");
    const res = await api.readHistory("uuid");
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/ endpoint when 'readPage' is called with no params, if none given", async () => {
    myNock.get("/alert/").reply(200, "Read successful");
    const res = await api.readPage();
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/ endpoint when 'readPage' is called with properly formatted params", async () => {
    myNock
      .get(
        "/alert/?limit=10&offset=10&name=Test+Name&disposition=FALSE_POSITIVE&observable_types=testA,testB&tags=tagA,tagB&threats=threatA,threatB&observable=test%7Cexample",
      )
      .reply(200, "Read successful");
    const res = await api.readPage(MOCK_PARAMS);
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/ endpoint when 'readAllPages' is called with properly formatted params", async () => {
    myNock
      .get(
        "/alert/?limit=10&offset=0&name=Test+Name&disposition=FALSE_POSITIVE&observable_types=testA%2CtestB&tags=tagA%2CtagB&threats=threatA%2CthreatB&observable=test%7Cexample",
      )
      .reply(200, { items: [], total: 0 });
    const res = await api.readAllPages(MOCK_PARAMS);
    expect(res).toEqual([]);
  });

  it("will make a patch request to the /alert/ endpoint when 'update' is called with an array of update data", async () => {
    myNock.patch("/alert/").reply(200, "Update successful");
    const res = await api.update([MOCK_ALERT_UPDATE]);
    expect(res).toEqual("Update successful");
  });

  it("will make a post request to the /alert/observables endpoint when 'readHistory' is called with a given UUID", async () => {
    const uuids = ["uuid1", "uuid2"];
    myNock
      .post("/alert/observables", JSON.stringify(uuids))
      .reply(200, "Read successful");
    const res = await api.readObservables(uuids);
    expect(res).toEqual("Read successful");
  });

  it("will make a get request to the /alert/{uuid}/summary/url_domain endpoint when 'readUrlDomainSummary' is called with a given UUID", async () => {
    myNock.get("/alert/uuid/summary/url_domain").reply(200, "Read successful");
    const res = await api.readUrlDomainSummary("uuid");
    expect(res).toEqual("Read successful");
  });
});
