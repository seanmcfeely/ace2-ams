import auth from "../../services/api/auth";
import { CommitFunction } from "@/store/index";

const store = {
  namespaced: true,

  state: {
    // state of login
    loggedIn: false
  },
  getters: {
    loggedIn: (state: { loggedIn: boolean }) => state.loggedIn,
  },
  mutations: {
    SET_LOGGEDIN(
      state: { loggedIn: boolean },
      loggedIn: boolean,
    ) {
      state.loggedIn = loggedIn;
    },
  },
  actions: {
    async login({ commit }: CommitFunction, payload: {username: string, password: string}) {
        await auth
        .authenticate(payload)
        .then(() => {commit("SET_LOGGEDIN", true);})
        .catch ((error) => {
          commit("SET_LOGGEDIN", false);
          throw error;
        }) 
    },
  },
};

export default store;
