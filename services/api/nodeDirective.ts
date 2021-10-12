import BaseApi from "./base";
import { UUID } from "../../models/base";
import { NodeDirectiveCreate } from "../../models/nodeDirective";

const api = new BaseApi();

export default {
  endpoint: "/node/directive",

  // CREATE
  async createNodeDirective(nodeDirective: NodeDirectiveCreate) {
    return await api
      .createRequest(`${this.endpoint}`, nodeDirective)
      .catch((err) => {
        throw err;
      });
  },

  // READ
  async getAllNodeDirectives() {
    return await api.readRequest(`${this.endpoint}`).catch((err) => {
      throw err;
    });
  },

  async getNodeDirective(uuid: UUID) {
    return await api.readRequest(`${this.endpoint}${uuid}`).catch((err) => {
      throw err;
    });
  },

  // UPDATE
  async updateNodeDirective(nodeDirective: { value: string }, uuid: UUID) {
    return await api
      .updateRequest(`${this.endpoint}${uuid}`, nodeDirective)
      .catch((err) => {
        throw err;
      });
  },
};
