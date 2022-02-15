import {
  observableCreate,
  observableRead,
  observableUpdate,
} from "@/models/observable";
import { UUID } from "@/models/base";
import { BaseApi } from "./base";
import { observableHistoryReadPage } from "@/models/history";

const api = new BaseApi();
const endpoint = "/observable/instance/";

export const ObservableInstance = {
  create: (data: observableCreate, getAfterCreate = false): Promise<void> =>
    api.create(endpoint, data, getAfterCreate),

  read: (uuid: UUID): Promise<observableRead> => api.read(`${endpoint}${uuid}`),

  readHistory: async (uuid: UUID): Promise<observableHistoryReadPage> =>
    await api.read(`${endpoint}${uuid}/history`),

  update: (uuid: UUID, data: observableUpdate): Promise<void> =>
    api.update(`${endpoint}${uuid}`, data),
};
