import { describe, it, beforeEach, expect } from "vitest";
import myNock from "@unit/services/api/nock";
import { eventFilterParams } from "@/models/event";
import { parseEventSummary, useEventTableStore } from "@/stores/eventTable";
import { useSelectedEventStore } from "@/stores/selectedEvent";
import { eventReadFactory, eventSummaryFactory } from "@mocks/events";
import { queueableObjectReadFactory } from "@mocks/genericObject";
import { threatReadFactory } from "@mocks/threat";
import { userReadFactory } from "@mocks/user";
import { createCustomPinia } from "@tests/unitHelpers";
import { useFilterStore } from "@/stores/filter";

createCustomPinia();
const store = useEventTableStore();

const mockEventReadA = eventReadFactory({ uuid: "uuid1" });
const mockEventReadASummary = eventSummaryFactory({
  uuid: "uuid1",
  queue: "testObject",
});
const mockEventReadB = eventReadFactory({ uuid: "uuid2" });
const mockEventReadBSummary = eventSummaryFactory({
  uuid: "uuid2",
});

const mockOwner = userReadFactory();
const mockPreventionTool = queueableObjectReadFactory({
  value: "preventionTool",
});
const mockSeverity = queueableObjectReadFactory({ value: "severity" });
const mockStatus = queueableObjectReadFactory({ value: "status" });
const mockThreat = threatReadFactory();
const mockThreatActor = queueableObjectReadFactory({ value: "threatActor" });
const mockType = queueableObjectReadFactory({ value: "type" });
const mockVector = queueableObjectReadFactory({ value: "vector" });
const mockEventReadC = eventReadFactory({
  uuid: "uuid3",
  owner: mockOwner,
  preventionTools: [mockPreventionTool],
  severity: mockSeverity,
  status: mockStatus,
  threatActors: [mockThreatActor],
  threats: [mockThreat],
  type: mockType,
  vectors: [mockVector],
});
const mockEventReadCSummary = eventSummaryFactory({
  uuid: "uuid3",
  owner: "Test Analyst",
  preventionTools: ["preventionTool"],
  severity: "severity",
  status: "status",
  threatActors: ["threatActor"],
  threats: ["threat"],
  type: "type",
  vectors: ["vector"],
  queue: "testObject",
});

const mockParams: eventFilterParams = { limit: 5, offset: 0 };

describe("eventTable helpers", () => {
  it("will correctly parse an event received from the backend using parseEventSummary", () => {
    const resA = parseEventSummary(mockEventReadA);
    const resB = parseEventSummary(mockEventReadC);
    expect(resA).toEqual(mockEventReadASummary);
    expect(resB).toEqual(mockEventReadCSummary);
  });
});

describe("eventTable getters", () => {
  beforeEach(() => {
    store.$reset();
  });

  it("will correctly return  visibleQueriedItemSummaries", () => {
    store.visibleQueriedItems = [
      mockEventReadA,
      mockEventReadB,
      mockEventReadC,
    ];
    expect(store.visibleQueriedItemSummaries).toEqual([
      mockEventReadASummary,
      mockEventReadBSummary,
      mockEventReadCSummary,
    ]);
  });

  it("will correctly return  visibleQueriedItemsUuids", () => {
    store.visibleQueriedItems = [
      mockEventReadA,
      mockEventReadB,
      mockEventReadC,
    ];
    expect(store.visibleQueriedItemsUuids).toEqual(["uuid1", "uuid2", "uuid3"]);
  });

  it("will correctly return  visibleQueriedItemById", () => {
    store.visibleQueriedItems = [
      mockEventReadA,
      mockEventReadB,
      mockEventReadC,
    ];
    expect(store.visibleQueriedItemById("uuid1")).toEqual(mockEventReadA);
  });

  it("will correctly return  visibleQueriedSelectedItems", () => {
    const selectedStore = useSelectedEventStore();
    selectedStore.selected = ["uuid2"];
    store.visibleQueriedItems = [
      mockEventReadA,
      mockEventReadB,
      mockEventReadC,
    ];
    expect(store.visibleQueriedSelectedItems).toEqual([mockEventReadB]);
  });

  it("will correctly return sortFilter", () => {
    expect(store.sortFilter).toEqual("created_time|desc");

    store.sortField = null;
    store.sortOrder = null;
    expect(store.sortFilter).toStrictEqual(null);
  });

  it("will correctly return allFiltersLoaded", () => {
    expect(store.allFiltersLoaded).toStrictEqual(false);
    store.stateFiltersLoaded = true;
    expect(store.allFiltersLoaded).toStrictEqual(false);
    store.stateFiltersLoaded = false;
    store.routeFiltersLoaded = true;
    expect(store.allFiltersLoaded).toStrictEqual(false);
    store.stateFiltersLoaded = true;
    expect(store.allFiltersLoaded).toStrictEqual(true);
  });
});

describe("eventTable actions", () => {
  beforeEach(() => {
    store.$reset();
  });

  it("will request to read page of events with given params on readPage", async () => {
    const mockRequest = myNock.get("/event/?limit=5&offset=0").reply(200, {
      total: 3,
      items: [mockEventReadA, mockEventReadB, mockEventReadC],
    });

    await store.readPage(mockParams);

    expect(mockRequest.isDone()).toEqual(true);
    expect(store.visibleQueriedItems).toEqual([
      JSON.parse(JSON.stringify(mockEventReadA)),
      JSON.parse(JSON.stringify(mockEventReadB)),
      JSON.parse(JSON.stringify(mockEventReadC)),
    ]);
    expect(store.totalItems).toEqual(3);
    expect(store.requestReload).toEqual(false);
  });

  it("will throw an error if request fails on readPage", async () => {
    myNock.get("/event/?limit=5&offset=0").reply(403);

    try {
      await store.readPage(mockParams);
    } catch (e) {
      const error = e as Error;
      expect(error.message).toStrictEqual(
        "Request failed with status code 403",
      );
    }

    expect(store.visibleQueriedItems).toEqual([]);
    expect(store.totalItems).toEqual(0);
    expect(store.requestReload).toEqual(false);
  });
  it("will reset the sort order and sort field to written defaults on resetSort", () => {
    store.sortField = "exampleSort";
    store.sortOrder = "asc";

    store.resetSort();

    expect(store.sortField).toEqual("createdTime");
    expect(store.sortOrder).toEqual("desc");
  });
  it("tests your func for events reading from all pages", async () => {
    const mockRequest = myNock.get("/event/?limit=5&offset=0").reply(200, {
      total: 3,
      items: [mockEventReadA, mockEventReadB, mockEventReadC],
    });

    const result = await store.readAllPages(mockParams);
    
    expect(mockRequest.isDone()).toEqual(true);
    expect(result).toEqual([
      mockEventReadASummary,
      mockEventReadBSummary,
      mockEventReadCSummary,
    ]);
  });
  it("will throw an error if request fails on readAllPages", async () => {
    myNock.get("/event/?limit=5&offset=0").reply(403);

    try {
      await store.readAllPages(mockParams);
    } catch (e) {
      const error = e as Error;
      expect(error.message).toStrictEqual(
        "Request failed with status code 403",
      );
    }
  });
});
