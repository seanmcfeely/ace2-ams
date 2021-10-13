import auth from "../../../../../src/services/api/auth";
import myNock from "./nock";

const mockLoginData = {
  username: "user",
  password: "pass",
};

const mockAuthResponseData = {
  access_token: "abcd1234",
  refresh_token: "1234abcd",
  token_type: "bearer",
};

const mockRefreshResponseData = {
  access_token: "new_token!",
};

const authHeaders = {
  "access-control-allow-headers": "Authorization",
};

// TODO: Fix/update auth tests
// describe("/auth API calls", () => {
//   beforeEach(() => {
//     myNock.options("/refresh").reply(200, "options", authHeaders);
//     myNock.options("/auth").reply(200, "options", authHeaders);
//   });

//   it("will make a post request to /auth when authenticate is called and set session variables upon success", async () => {
//     myNock.post("/auth").reply(200, mockAuthResponseData, authHeaders);
//     await auth.authenticate(mockLoginData);
//     expect(sessionStorage.accessToken).toEqual("Bearer abcd1234");
//     expect(sessionStorage.refreshToken).toEqual("1234abcd");
//   });
//   it("will make a post request to /refresh when refreshAuth is called", async () => {
//     myNock.post("/refresh").reply(200, mockRefreshResponseData, authHeaders);
//     await auth.refeshAuth();
//     expect(sessionStorage.accessToken).toEqual("Bearer new_token!");
//     expect(sessionStorage.refreshToken).toEqual("1234abcd");
//   });
//   it("will throw an error if auth attempt fails", async () => {
//     myNock.post("/auth").reply(401, "Login failed :(", authHeaders);

//     await expect(auth.authenticate(mockLoginData)).rejects.toEqual(
//       new Error("Request failed with status code 401"),
//     );
//   });
//   it("will throw an error if an authenticate or authRefresh request fails", async () => {
//     myNock.post("/auth").reply(403, "Bad request :(", authHeaders);
//     myNock.post("/refresh").reply(403, "Bad request :(", authHeaders);

//     await expect(auth.authenticate(mockLoginData)).rejects.toEqual(
//       new Error("Request failed with status code 403"),
//     );
//     await expect(auth.refeshAuth()).rejects.toEqual(
//       new Error("Request failed with status code 403"),
//     );
//   });
// });
