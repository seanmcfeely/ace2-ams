/**
 * @jest-environment node
 */

import myNock from "@unit/services/api/nock";
import { useEventStore } from "@/stores/event";
import { createTestingPinia } from "@pinia/testing";
import { eventFactory } from "../../../mocks/events";

createTestingPinia();

const store = useEventStore();

const mockEvent = eventFactory({ uuid: "uuid1" });

describe("event Actions", () => {
  beforeEach(() => {
    store.$reset();
  });

  it("will fetch event data given an event ID", async () => {
    const mockRequest = myNock.get("/event/uuid1").reply(200, mockEvent);
    await store.read("uuid1");

    expect(mockRequest.isDone()).toEqual(true);

    // The openEvent is not parsed at all when received, so any dates will be in string format
    expect(store.openEvent).toEqual(JSON.parse(JSON.stringify(mockEvent)));
  });

  it("will make a request to update an event given the UUID and update data upon the updateEvent action", async () => {
    const mockRequest = myNock.patch("/event/").reply(200);
    await store.update([{ uuid: "uuid1", name: "test" }]);

    expect(mockRequest.isDone()).toEqual(true);
    // None of these should be changed
    expect(store.openEvent).toBeNull();
  });
});
