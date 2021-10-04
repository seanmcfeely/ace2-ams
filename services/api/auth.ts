import BaseApi from "./base";

const api = new BaseApi();

export default {
  endpoint: "/auth",

  // AUTH
  async authenticate(loginData: {
    username: string;
    password: string;
  }): Promise<void> {
    return await api
      .authRequest(this.endpoint, false, loginData)
      .catch((err) => {
        throw err;
      });
  },

  // REFRESH AUTH
  async refeshAuth(): Promise<void> {
    return await api.authRequest("/refresh", true).catch((err) => {
      throw err;
    });
  },
};
