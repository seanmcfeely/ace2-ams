import BaseApi from "./base";
import { UUID, genericObject } from "../../models/base";
import { ObservableTypeCreate } from "../../models/observableType";

const api = new BaseApi();

export default {
  endpoint: "/observable/type",

  // CREATE
  async createObservableType(
    observableType: ObservableTypeCreate,
  ): Promise<genericObject> {
    return await api
      .createRequest(`${this.endpoint}`, observableType)
      .catch((err) => {
        throw err;
      });
  },

  // READ
  async getAllObservableTypes(): Promise<genericObject> {
    return await api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  },

  async getObservableType(uuid: UUID): Promise<genericObject> {
    return await api.readRequest(`${this.endpoint}${uuid}`).catch((err) => {
      throw err;
    });
  },

  // UPDATE
  async updateObservableType(
    observableType: { value: string },
    uuid: UUID,
  ): Promise<genericObject> {
    return await api
      .updateRequest(`${this.endpoint}${uuid}`, observableType)
      .catch((err) => {
        throw err;
      });
  },
};
