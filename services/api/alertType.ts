import BaseApi from "./base";
import { UUID } from "../../models/base";
import { AlertTypeCreate } from "../../models/alertType";

const api = new BaseApi();

export default {
  endpoint: "/alert/type",

  // CREATE
  async createAlertType(alertType: AlertTypeCreate) {
    return await api
      .createRequest(`${this.endpoint}`, alertType)
      .catch((err) => {
        throw err;
      });
  },

  // READ
  async getAllAlertTypes() {
    return await api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  },

  async getAlertType(uuid: UUID) {
    return await api.readRequest(`${this.endpoint}${uuid}`).catch((err) => {
      throw err;
    });
  },

  // UPDATE
  async updateAlertType(alertType: { value: string }, uuid: UUID) {
    return await api
      .updateRequest(`${this.endpoint}${uuid}`, alertType)
      .catch((err) => {
        throw err;
      });
  },
};
