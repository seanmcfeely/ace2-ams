import { userCreate, userRead, userReadPage, userUpdate } from "@/models/user";
import { pageOptionParams, UUID } from "@/models/base";
import { BaseApi } from "./base";

const api = new BaseApi();
const endpoint = "/user/";

export const User = {
  create: (data: userCreate, getAfterCreate = false): Promise<void> =>
    api.create(endpoint, data, getAfterCreate),

  read: (uuid: UUID): Promise<userRead> => api.read(`${endpoint}${uuid}`),

  readAll: (): Promise<userRead[]> => api.readAll(endpoint),

  readPage: (params?: pageOptionParams): Promise<userReadPage> =>
    api.read(`${endpoint}`, params),

  update: (uuid: UUID, data: userUpdate): Promise<void> =>
    api.update(`${endpoint}${uuid}`, data),
};
