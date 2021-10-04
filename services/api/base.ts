import { AxiosRequestConfig } from "axios";
import instance from "./axios";
import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";

type Method = "GET" | "DELETE" | "POST" | "PATCH";

export default class BaseApi {
  formatIncomingData(data: Record<string, any>) {
    return camelcaseKeys(data, { deep: true });
  }

  formatOutgoingData(data: Record<string, any>) {
    return snakecaseKeys(data);
  }

  methodDict = {
    POST: "create",
    GET: "fetch",
    PATCH: "update",
    DELETE: "delete",
  };

  async authRequest(
    url: string,
    refresh = false,
    auth?: { username: string; password: string },
  ) {
    const config: AxiosRequestConfig = {
      url: url,
      method: "POST",
    };

    if (refresh && sessionStorage.refreshToken) {
      config["data"] = this.formatOutgoingData({
        refreshToken: sessionStorage.refreshToken,
      });
    } else if (auth) {
      const formData = new FormData();
      formData.append("username", auth.username);
      formData.append("password", auth.password);
      config["data"] = formData;
      config["headers"] = {
        "content-type": "application/x-www-form-urlencoded",
      };
    }

    const response = await instance.request(config).catch((error) => {
      throw error;
    });

    // todo decode, move this to vuex, etc.
    sessionStorage.setItem(
      "accessToken",
      `Bearer ${response.data.access_token}`,
    );
    sessionStorage.setItem("refreshToken", response.data.refresh_token);
  }

  protected async baseRequest(
    url: string,
    method: Method,
    data?: Record<string, any>,
  ) {
    const config: AxiosRequestConfig = {
      url: url,
      method: method,
    };

    if (data) {
      config["data"] = this.formatOutgoingData(data);
    }

    if (sessionStorage.accessToken) {
      config["headers"] = { Authorization: sessionStorage.accessToken };
    }

    const response = await instance.request(config).catch((error) => {
      throw error;
    });

    if (response) {
      if (Array.isArray(response.data)) {
        return response.data.map(this.formatIncomingData);
      }
      return this.formatIncomingData(response.data);
    }
    throw new Error(`${this.methodDict[method]} failed!`);
  }

  async createRequest(url: string, data?: Record<string, any>) {
    return await this.baseRequest(url, "POST", data);
  }

  async readRequest(url: string) {
    return await this.baseRequest(url, "GET");
  }

  async updateRequest(url: string, data?: Record<string, any>) {
    return await this.baseRequest(url, "PATCH", data);
  }
}
