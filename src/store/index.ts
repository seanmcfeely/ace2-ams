import { Commit, createStore } from "vuex";

import alertQueue from "./alertQueue";
import alertType from "./alertType";
import nodeDirectives from "./nodeDirectives";
import observableType from "@/services/api/observableType";
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
