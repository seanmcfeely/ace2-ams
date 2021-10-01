import { Commit, createStore } from "vuex";

import alerts from "./alerts";
import modals from "./modals";
import selectedAlerts from "./selectedAlerts";
import users from "./users";

// todo: add selectedAlerts to store
// probably also want to add applied filters.

export interface CommitFunction {
  commit: Commit;
}

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: { alerts, modals, selectedAlerts, users },
});
