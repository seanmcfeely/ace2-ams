import { createStore } from "vuex";
import { CommitFunction } from "@/store";
import auth from "@/store/auth";
import alerts from "@/store/alerts";
import users from "@/store/users";
import modals from "@/store/modals";
import selectedAlerts from "@/store/selectedAlerts";

const authState = auth.state;
const authGetters = auth.getters;

const alertsState = alerts.state;
const alertsMutations = alerts.mutations;

const usersState = users.state;
const usersGetters = users.getters;
const usersMutations = users.mutations;

export class testVars {
  public static errorCondition = false;
}

const alertsStore = {
  namespaced: true,
  state: alertsState,
  mutations: alertsMutations,
  actions: {
    updateAlert() {
      let promise = Promise.resolve<string | Error>("success");

      if (testVars.errorCondition) {
        promise = Promise.reject<string | Error>(new Error("Call failed"));
      }
      return promise.catch((error) => {
        throw error;
      });
    },
    updateAlerts() {
      let promise = Promise.resolve<string | Error>("success");

      if (testVars.errorCondition) {
        promise = Promise.reject<string | Error>(new Error("Call failed"));
      }
      return promise.catch((error) => {
        throw error;
      });
    },
  },
};

const usersStore = {
  namespaced: true,

  state: usersState,
  getters: usersGetters,
  mutations: usersMutations,

  actions: {
    getAllUsers({ commit }: CommitFunction) {
      let promise = Promise.resolve<Array<string> | Error>(["Alice", "Bob"]);

      if (testVars.errorCondition) {
        promise = Promise.reject<Array<string> | Error>(
          new Error("Call failed"),
        );
      }
      return promise
        .then((users) => {
          commit("SET_USERS", users);
          commit("SET_GET_ALL_TIMESTAMP");
        })
        .catch((error) => {
          throw error;
        });
    },
  },
};

const authStore = {
  namespaced: true,

  state: authState,
  getters: authGetters,

  actions: {
    login({ commit }: CommitFunction) {
      let promise = Promise.resolve<undefined | Error>(undefined);

      if (testVars.errorCondition) {
        promise = Promise.reject<undefined | Error>(new Error("Call failed"));
      }
      return promise
        .then(() => {
          commit("SET_LOGGEDIN", true);
        })
        .catch((error) => {
          commit("SET_LOGGEDIN", false);
          throw error;
        });
    },
  },
};

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: {
    modals: modals,
    users: usersStore,
    selectedAlerts: selectedAlerts,
    alerts: alertsStore,
    auth: authStore,
  },
});
