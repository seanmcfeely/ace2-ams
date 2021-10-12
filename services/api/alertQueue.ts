import BaseApi from "./base";
import { UUID } from "../../models/base";
import { AlertQueueCreate } from "../../models/alertQueue";

const api = new BaseApi();

export default {
  endpoint: "/alert/queue",

  // CREATE
  async createAlertQueue(alertQueue: AlertQueueCreate) {
    return await api
      .createRequest(`${this.endpoint}`, alertQueue)
      .catch((err) => {
        throw err;
      });
  },

  // READ
  async getAllAlertQueues() {
    return await api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  },

  async getAlertQueue(uuid: UUID) {
    return await api.readRequest(`${this.endpoint}${uuid}`).catch((err) => {
      throw err;
    });
  },

  // UPDATE
  async updateAlertQueue(alertQueue: { value: string }, uuid: UUID) {
    return await api
      .updateRequest(`${this.endpoint}${uuid}`, alertQueue)
      .catch((err) => {
        throw err;
      });
  },
};
