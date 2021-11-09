import { AxiosRequestConfig } from "axios";
import instance from "./axios";
import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";
import { anyGetAll, anyGetSingle, getAllParams } from "@/models/api";
import { UUID } from "@/models/base";

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

  protected async baseRequest(
    url: string,
    method: Method,
    options?: {
      data?: Record<string, any>;
      params?: getAllParams;
    },
    getAfterCreate = true,
  ): Promise<any> {
    const config: AxiosRequestConfig = {
      url: url,
      method: method,
      withCredentials: true,
    };

    if (options) {
      if (options.data) {
        config["data"] = this.formatOutgoingData(options.data);
      }

      if (options.params) {
        config["params"] = this.formatOutgoingData(options.params);
      }
    }

    const response = await instance.request(config).catch((error) => {
      throw error;
    });

    if (response) {
      if ("content-location" in response.headers && getAfterCreate) {
        return await this.readRequest(response.headers["content-location"]);
      }

      if (Array.isArray(response.data)) {
        return response.data.map(this.formatIncomingData);
      }
      return this.formatIncomingData(response.data);
    }
    throw new Error(`${this.methodDict[method]} failed!`);
  }

  async createRequest(
    url: string,
    data?: Record<string, any>,
    getAfterCreate = true,
  ): Promise<unknown> {
    return await this.baseRequest(url, "POST", { data: data }, getAfterCreate);
  }

  async readRequest(
    url: string,
    params?: getAllParams,
  ): Promise<anyGetSingle & anyGetAll> {
    return await this.baseRequest(url, "GET", { params: params });
  }

  async updateRequest(
    url: string,
    data?: Record<string, any>,
  ): Promise<unknown> {
    return await this.baseRequest(url, "PATCH", { data: data });
  }
}

export class GenericEndpoint {
  api = new BaseApi();
  endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  // CREATE
  async create(
    object: Record<string, unknown>,
    getAfterCreate = true,
  ): Promise<unknown> {
    return await this.api
      .createRequest(`${this.endpoint}`, object, getAfterCreate)
      .catch((err) => {
        throw err;
      });
  }

  // READ
  async getAll(params?: getAllParams): Promise<anyGetAll> {
    return await this.api
      .readRequest(`${this.endpoint}`, params)
      .catch((err) => {
        throw err;
      });
  }

  async getSingle(uuid: UUID): Promise<anyGetSingle> {
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
