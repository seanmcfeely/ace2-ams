/**
 * @jest-environment node
 */

import BaseApi from "../../../../src/services/api/base";
import myNock from "./nock";

describe("BaseAPI calls", () => {
  const api = new BaseApi();

  it("make a post request when createRequest is called", async () => {
    myNock.post("/create").reply(200, "Create successful");
    const res = await api.createRequest("/create");
    expect(res).toEqual("Create successful");
  });
  it("make a get request when readRequest called", async () => {
    myNock.get("/read").reply(200, "Read successful");
    const res = await api.readRequest("/read");
    expect(res).toEqual("Read successful");
  });
  it("make a patch request when updateRequest called", async () => {
    myNock.patch("/update").reply(200, "Update successful");
    const res = await api.updateRequest("/update");
    expect(res).toEqual("Update successful");
  });
  it("will format outgoing data into snake_case keys", async () => {
    myNock
      .post("/create", { first_key: "A", second_key: 2 })
      .reply(200, "Update successful");
    const res = await api.createRequest("/create", {
      firstKey: "A",
      secondKey: 2,
    });
    expect(res).toEqual("Update successful");
  });
  it("will format incoming data into camelCase keys", async () => {
    myNock.post("/create").reply(200, { first_key: "A", second_key: 2 });
    const res = await api.createRequest("/create");
    expect(res).toEqual({
      firstKey: "A",
      secondKey: 2,
    });
  });
  it("will format incoming objects in a list format into camelCase keys", async () => {
    myNock.post("/create").reply(200, [
      { first_key: "A", second_key: 2 },
      { third_key: "B", fourth_key: 3 },
    ]);
    const res = await api.createRequest("/create");
    expect(res).toEqual([
      {
        firstKey: "A",
        secondKey: 2,
      },
      {
        thirdKey: "B",
        fourthKey: 3,
      },
    ]);
  });
  it("will throw an error if a request fails", async () => {
    myNock.patch("/update").replyWithError("Request failed :(");
    await expect(api.updateRequest("/update")).rejects.toEqual(
      new Error("Request failed :("),
    );
  });
  it("will throw an error if a request completes, but without a successful response code", async () => {
    myNock.patch("/update").reply(404, "Not found :(");
    await expect(api.updateRequest("/update")).rejects.toEqual(
      new Error("Request failed with status code 404"),
    );
  });
});
