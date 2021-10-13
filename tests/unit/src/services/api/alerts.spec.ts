/**
 * @jest-environment node
 */

import alert from "../../../../../src/services/api/alerts";
import myNock from "./nock";

import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";

const mockCreateAlert = {
  directives: [],
  tags: [],
  threats: [],
  version: "v1",
  uuid: "1",
  eventTime: new Date(0),
  instructions: "None",
  name: "Test Alert",
  queue: "default",
  type: "test",
};

describe("/alert API calls", () => {
  it("will make a post request when createAlert is called", async () => {
    myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(mockCreateAlert)))
      .reply(200, "Create alert successful");

    const res = await alert.createAlert(mockCreateAlert);
    expect(res).toEqual("Create alert successful");
  });
  it("will make a get request to /alert/{uuid} when getAlert is called", async () => {
    // The reply would actually contain alertRead data, but we don't need to test that here since nothing is done with
    // the data in alerts.ts
    myNock.get("/alert/1").reply(200, "Read alert successful");

    const res = await alert.getAlert("1");
    expect(res).toEqual("Read alert successful");
  });
  it("will make a patch request to /alert/{uuid} when updateAlert is called", async () => {
    myNock
      .patch("/alert/1", JSON.stringify({ disposition: "false_positive" }))
      .reply(200, "Update alert successful");

    const res = await alert.updateAlert({ disposition: "false_positive" }, "1");
    expect(res).toEqual("Update alert successful");
  });
  it("will throw an error if a request fails", async () => {
    myNock.get("/alert/1").reply(404, "Alert not found :(");

    await expect(alert.getAlert("1")).rejects.toEqual(
      new Error("Request failed with status code 404"),
    );
  });
});
