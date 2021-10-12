import { AxiosRequestConfig } from "axios";
import instance from "./axios";
import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";
import { UUID } from "models/base";

type Method = "GET" | "DELETE" | "POST" | "PATCH";

export class BaseApi {
  formatIncomingData(data: Record<string, unknown>): Record<string, unknown> {
    return camelcaseKeys(data, { deep: true });
  }

  formatOutgoingData(data: Record<string, unknown>): Record<string, unknown> {
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
  ): Promise<void> {
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
    if (!refresh) {
      sessionStorage.setItem("refreshToken", response.data.refresh_token);
    }
  }

  protected async baseRequest(
    url: string,
    method: Method,
    data?: Record<string, unknown>,
  ): Promise<unknown> {
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

  async createRequest(
    url: string,
    data?: Record<string, unknown>,
  ): Promise<unknown> {
    return await this.baseRequest(url, "POST", data);
  }

  async readRequest(url: string): Promise<unknown> {
    return await this.baseRequest(url, "GET");
  }

  async updateRequest(
    url: string,
    data?: Record<string, unknown>,
  ): Promise<unknown> {
    return await this.baseRequest(url, "PATCH", data);
  }
}

export class GenericEndpoint {
  api = new BaseApi();
  endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  // CREATE
  async create(object: Record<string, unknown>): Promise<unknown> {
    return await this.api
      .createRequest(`${this.endpoint}`, object)
      .catch((err) => {
        throw err;
      });
  }

  // READ
  async getAll(): Promise<unknown> {
    return await this.api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  }

  async getSingle(uuid: UUID): Promise<unknown> {
    return await this.api
      .readRequest(`${this.endpoint}${uuid}`)
      .catch((err) => {
        throw err;
      });
  }

  // UPDATE
  async updateSingle(
    object: Record<string, unknown>,
    uuid: UUID,
  ): Promise<unknown> {
    return await this.api
      .updateRequest(`${this.endpoint}${uuid}`, object)
      .catch((err) => {
        throw err;
      });
  }
}
