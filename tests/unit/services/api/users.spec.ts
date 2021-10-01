/**
 * @jest-environment node
 */

import user from "../../../../services/api/users";
import myNock from "./nock";

import snakecaseKeys from "snakecase-keys";

const mockCreateUser = {
  username: "Alice",
  password: "password123",
  uuid: "1",
};

describe("/user API calls", () => {
  it("will make a post request when createUser is called", async () => {
    myNock
      .post("/user/", JSON.stringify(snakecaseKeys(mockCreateUser)))
      .reply(200, "Create user successful");

    const res = await user.createUser(mockCreateUser);
    expect(res).toEqual("Create user successful");
  });
  it("will make a get request to /user/{uuid} when getUser is called", async () => {
    // The reply would actually contain userRead data, but we don't need to test that here since nothing is done with
    // the data in users.ts
    myNock.get("/user/1").reply(200, "Read user successful");

    const res = await user.getUser("1");
    expect(res).toEqual("Read user successful");
  });
  it("will make a get request to /user/ when getUsers is called", async () => {
    myNock.get("/user/").reply(200, [mockCreateUser, mockCreateUser]);

    const res = await user.getAllUsers();
    expect(res).toEqual([mockCreateUser, mockCreateUser]);
  });
  it("will make a patch request to /user/{uuid} when updateUser is called", async () => {
    myNock
      .patch("/user/1", JSON.stringify({ disposition: "false_positive" }))
      .reply(200, "Update user successful");

    const res = await user.updateUser({ disposition: "false_positive" }, "1");
    expect(res).toEqual("Update user successful");
  });
  it("will throw an error if a request fails", async () => {
    myNock.get("/user/1").reply(404, "User not found :(");

    await expect(user.getUser("1")).rejects.toEqual(
      new Error("Request failed with status code 404"),
    );
  });
});
