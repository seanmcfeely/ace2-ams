import { GenericEndpoint } from "./base";

class Alerts extends GenericEndpoint {
  getAll() {
    return Promise.reject(Error("Not implemented."));
  }
}

export default new Alerts("/observable/instance");
