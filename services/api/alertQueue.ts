import BaseApi from "./base";
import { UUID, genericObject } from "../../models/base";
import { AlertQueueCreate } from "../../models/alertQueue";

const api = new BaseApi();

export default {
  endpoint: "/alert/queue",

  // CREATE
  async createAlertQueue(alertQueue: AlertQueueCreate): Promise<genericObject> {
    return await api
      .createRequest(`${this.endpoint}`, alertQueue)
      .catch((err) => {
        throw err;
      });
  },

  // READ
  async getAllAlertQueues(): Promise<genericObject> {
    return await api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  },

  async getAlertQueue(uuid: UUID): Promise<genericObject> {
    return await api.readRequest(`${this.endpoint}${uuid}`).catch((err) => {
      throw err;
    });
  },

  // UPDATE
  async updateAlertQueue(
    alertQueue: { value: string },
    uuid: UUID,
  ): Promise<genericObject> {
    return await api
      .updateRequest(`${this.endpoint}${uuid}`, alertQueue)
      .catch((err) => {
        throw err;
      });
  },
};
