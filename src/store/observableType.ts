import observableType from "../../services/api/observableType";
import { ObservableTypeRead } from "../../models/observableType";
import { CommitFunction } from "@/store/index";

const store = {
  namespaced: true,

  state: {
    // last time all observable types were fetched
    lastGetAll: null,
    // all observable types
    observableTypes: [],
  },
  getters: {
    observableTypes: (state: {
      observableTypes: ObservableTypeRead[];
    }): ObservableTypeRead[] => state.observableTypes,
  },
  mutations: {
    SET_OBSERVABLE_TYPES(
      state: {
        observableTypes: ObservableTypeRead[];
        lastGetAll: number | null;
      },
      observableTypes: ObservableTypeRead[],
    ): void {
      state.observableTypes = observableTypes;
    },
    SET_GET_ALL_TIMESTAMP(state: {
      observableTypes: ObservableTypeRead[];
      lastGetAll: number | null;
    }): void {
      state.lastGetAll = new Date().getTime();
    },
  },

  actions: {
    getAllObservableTypes({ commit }: CommitFunction): Promise<void> {
      return observableType
        .getAllObservableTypes()
        .then((observableTypes) => {
          commit("SET_OBSERVABLE_TYPES", observableTypes);
          commit("SET_GET_ALL_TIMESTAMP");
        })
        .catch((error) => {
          throw error;
        });
    },
  },
};

export default store;
