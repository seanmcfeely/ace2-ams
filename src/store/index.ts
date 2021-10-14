import { Commit, createStore } from "vuex";

import auth from "@/store/auth";
import alerts from "@/store/alerts";
import modals from "@/store/modals";
import selectedAlerts from "@/store/selectedAlerts";
import users from "@/store/users";

// todo: add selectedAlerts to store
// probably also want to add applied filters.

export interface CommitFunction {
  commit: Commit;
}

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: { auth, alerts, modals, selectedAlerts, users },
});
