import alertQueue from "../../services/api/alertQueue";
import { AlertQueueRead } from "../../models/alertQueue";
import { CommitFunction } from "@/store/index";

const store = {
  namespaced: true,

  state: {
    // last time all alert queues were fetched
    lastGetAll: null,
    // all alert queues
    alertQueues: [],
  },
  getters: {
    alertQueues: (state: { alertQueues: AlertQueueRead[] }): AlertQueueRead[] =>
      state.alertQueues,
  },
  mutations: {
    SET_ALERT_QUEUES(
      state: { alertQueues: AlertQueueRead[]; lastGetAll: number | null },
      alertQueues: AlertQueueRead[],
    ): void {
      state.alertQueues = alertQueues;
    },
    SET_GET_ALL_TIMESTAMP(state: {
      alertQueues: AlertQueueRead[];
      lastGetAll: number | null;
    }): void {
      state.lastGetAll = new Date().getTime();
    },
  },

  actions: {
    getAllAlertQueues({ commit }: CommitFunction): Promise<void> {
      return alertQueue
        .getAllAlertQueues()
        .then((alertQueues) => {
          commit("SET_ALERT_QUEUES", alertQueues);
          commit("SET_GET_ALL_TIMESTAMP");
        })
        .catch((error) => {
          throw error;
        });
    },
  },
};

export default store;
