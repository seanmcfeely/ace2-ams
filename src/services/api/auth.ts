import { AxiosRequestConfig } from "axios";

import instance from "./axios";

export default {
  // AUTH
  async authenticate(loginData: {
    username: string;
    password: string;
  }): Promise<void> {
    const config: AxiosRequestConfig = {
      url: "/auth",
      method: "POST",
      withCredentials: true,
    };

    const formData = new FormData();
    formData.append("username", loginData.username);
    formData.append("password", loginData.password);
    config["data"] = formData;
    config["headers"] = {
      "content-type": "application/x-www-form-urlencoded",
    };

    await instance.request(config).catch((error) => {
      throw error;
    });
  },

  // REFRESH AUTH
  async refresh(): Promise<void> {
    const config: AxiosRequestConfig = {
      url: "/auth/refresh",
      method: "POST",
      withCredentials: true,
    };

    await instance.request(config).catch((error) => {
      throw error;
    });
  },
};
