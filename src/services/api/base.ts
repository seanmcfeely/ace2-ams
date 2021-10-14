import { AxiosRequestConfig } from "axios";
import instance from "./axios";
import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";

type Method = "GET" | "DELETE" | "POST" | "PATCH";

export default class BaseApi {
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

  protected async baseRequest(
    url: string,
    method: Method,
    data?: Record<string, unknown>,
  ): Promise<unknown> {
    const config: AxiosRequestConfig = {
      url: url,
      method: method,
      withCredentials: true,
    };

    if (data) {
      config["data"] = this.formatOutgoingData(data);
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
