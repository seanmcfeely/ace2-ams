import alertType from "../../services/api/alertType";
import { AlertTypeRead } from "../../models/alertType";
import { CommitFunction } from "@/store/index";

const store = {
  namespaced: true,

  state: {
    // last time all alert types were fetched
    lastGetAll: null,
    // all alert types
    alertTypes: [],
  },
  getters: {
    alertTypes: (state: { alertTypes: AlertTypeRead[] }): AlertTypeRead[] =>
      state.alertTypes,
  },
  mutations: {
    SET_ALERT_TYPES(
      state: { alertTypes: AlertTypeRead[]; lastGetAll: number | null },
      alertTypes: AlertTypeRead[],
    ): void {
      state.alertTypes = alertTypes;
    },
    SET_GET_ALL_TIMESTAMP(state: {
      alertTypes: AlertTypeRead[];
      lastGetAll: number | null;
    }): void {
      state.lastGetAll = new Date().getTime();
    },
  },

  actions: {
    getAllAlertTypes({ commit }: CommitFunction): Promise<void> {
      return alertType
        .getAllAlertTypes()
        .then((alertTypes) => {
          commit("SET_ALERT_TYPES", alertTypes);
          commit("SET_GET_ALL_TIMESTAMP");
        })
        .catch((error) => {
          throw error;
        });
    },
  },
};

export default store;
