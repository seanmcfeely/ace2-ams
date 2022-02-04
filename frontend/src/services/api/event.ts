import { formatNodeFiltersForAPI } from "@/etc/helpers";
import {
  eventCreate,
  eventFilterParams,
  eventRead,
  eventReadPage,
  eventUpdate,
} from "@/models/event";
import { UUID } from "@/models/base";
import { BaseApi } from "./base";
import { eventFilters } from "@/etc/constants";

const api = new BaseApi();
const endpoint = "/event/";

export const Event = {
  create: (data: eventCreate, getAfterCreate = false): Promise<void> => {
    return api.create(endpoint, data, getAfterCreate);
  },

  read: (uuid: UUID): Promise<eventRead> => {
    return api.read(`${endpoint}${uuid}`);
  },

  readPage: (params?: eventFilterParams): Promise<eventReadPage> => {
    let formattedParams = {} as eventFilterParams;
    if (params) {
      formattedParams = formatNodeFiltersForAPI(eventFilters, params);
    }

    return api.read(endpoint, formattedParams);
  },

  readAllPages: (params: eventFilterParams): Promise<eventRead[]> => {
    const formattedParams = formatNodeFiltersForAPI(eventFilters, params);
    return api.readAll(endpoint, formattedParams);
  },

  update: (data: eventUpdate[]): Promise<void> => {
    return api.update(endpoint, data);
  },
};
