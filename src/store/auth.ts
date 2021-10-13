import Cookies from "js-cookie";

class State {
  authenticated_until = 0;
  isLoggedIn = false;
}

const store = {
  namespaced: true,

  state: new State(),

  getters: {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    isLoggedIn: (_: State): boolean => !!Cookies.get("authenticated_until"),

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    authenticatedUntil: (_: State): number => {
      const authenticated_until = Cookies.get("authenticated_until");

      if (typeof authenticated_until === "string") {
        return parseFloat(authenticated_until);
      }

      return 0;
    },
  },
};

export default store;
