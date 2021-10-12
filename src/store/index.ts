import { Commit, createStore } from "vuex";

import alertQueue from "./alertQueue";
import alerts from "./alerts";
import alertType from "./alertType";
import auth from "./auth";
import modals from "./modals";
import nodeDirectives from "./nodeDirectives";
import observableType from "./observableType";
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
  modules: {
    alertQueue,
    auth,
    alerts,
    alertType,
    modals,
    nodeDirectives,
    observableType,
    selectedAlerts,
    users,
  },
});
