import Cookies from "js-cookie";

import auth from "@/services/api/auth";
import myNock from "@unit/services/api/nock";

const mockLoginData = {
  username: "user",
  password: "pass",
};

const mockAuthenticatedUntil = "1111111111.111111";

describe("/auth API calls", () => {
  it("will make a post request to /auth when authenticate is called and get the authenticated_until cookie upon success", async () => {
    // Mock out the response when getting the "authenticated_until" cookie value
    Cookies.get = jest.fn().mockImplementation(() => mockAuthenticatedUntil);

    myNock.post("/auth").reply(200);
    await auth.authenticate(mockLoginData);
    expect(Cookies.get("authenticated_until")).toEqual(mockAuthenticatedUntil);
  });

  it("will make a post request to /auth/refresh when refresh is called and get the authenticated_until cookie upon success", async () => {
    // Mock out the response when getting the "authenticated_until" cookie value
    Cookies.get = jest.fn().mockImplementation(() => mockAuthenticatedUntil);

    myNock.post("/auth/refresh").reply(200);
    await auth.refresh();
    expect(Cookies.get("authenticated_until")).toEqual(mockAuthenticatedUntil);
  });

  it("will throw an error if auth attempt fails", async () => {
    myNock.post("/auth").reply(401, "Login failed :(");

    await expect(auth.authenticate(mockLoginData)).rejects.toEqual(
      new Error("Request failed with status code 401"),
    );
  });

  it("will throw an error if an authenticate or authRefresh request fails", async () => {
    myNock.post("/auth").reply(403, "Bad request :(");
    myNock.post("/auth/refresh").reply(403, "Bad request :(");

    await expect(auth.authenticate(mockLoginData)).rejects.toEqual(
      new Error("Request failed with status code 403"),
    );
    await expect(auth.refresh()).rejects.toEqual(
      new Error("Request failed with status code 403"),
    );
  });
});
