import { AxiosRequestConfig } from "axios";

import instance from "@/services/api/axios";

export const authUrl = "/auth";
export const logoutUrl = "/auth/logout";
export const refreshUrl = "/auth/refresh";
export const validateUrl = "/auth/validate";

export default {
  // AUTH
  async authenticate(loginData: {
    username: string;
    password: string;
  }): Promise<void> {
    const config: AxiosRequestConfig = {
      url: authUrl,
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
      sessionStorage.removeItem("authenticated");
      throw error;
    });

    sessionStorage.setItem("authenticated", "yes");
  },

  // REFRESH AUTH
  async refresh(): Promise<void> {
    const config: AxiosRequestConfig = {
      url: refreshUrl,
      method: "GET",
      withCredentials: true,
    };

    await instance.request(config).catch((error) => {
      console.debug("need to authenticate");
      sessionStorage.removeItem("authenticated");
      throw error;
    });

    console.debug("authenticated");
    sessionStorage.setItem("authenticated", "yes");
  },

  // VALIDATE
  async validate(): Promise<void> {
    const config: AxiosRequestConfig = {
      url: validateUrl,
      method: "GET",
      withCredentials: true,
    };

    await instance.request(config).catch((error) => {
      throw error;
    });
  },

  // LOGOUT
  async logout(): Promise<void> {
    const config: AxiosRequestConfig = {
      url: logoutUrl,
      method: "GET",
      withCredentials: true,
    };

    await instance.request(config).catch((error) => {
      throw error;
    });

    sessionStorage.removeItem("authenticated");
  },
};
