import nodeDirective from "../../services/api/nodeDirective";
import { NodeDirectiveRead } from "../../models/nodeDirective";
import { CommitFunction } from "@/store/index";

const store = {
  namespaced: true,

  state: {
    // last time all node directives were fetched
    lastGetAll: null,
    // all node directives
    nodeDirectives: [],
  },
  getters: {
    nodeDirectives: (state: {
      nodeDirectives: NodeDirectiveRead[];
    }): NodeDirectiveRead[] => state.nodeDirectives,
  },
  mutations: {
    SET_NODE_DIRECTIVES(
      state: {
        nodeDirectives: NodeDirectiveRead[];
        lastGetAll: number | null;
      },
      nodeDirectives: NodeDirectiveRead[],
    ): void {
      state.nodeDirectives = nodeDirectives;
    },
    SET_GET_ALL_TIMESTAMP(state: {
      nodeDirectives: NodeDirectiveRead[];
      lastGetAll: number | null;
    }): void {
      state.lastGetAll = new Date().getTime();
    },
  },

  actions: {
    getAllNodeDirectives({ commit }: CommitFunction): Promise<void> {
      return nodeDirective
        .getAllNodeDirectives()
        .then((nodeDirectives) => {
          commit("SET_NODE_DIRECTIVES", nodeDirectives);
          commit("SET_GET_ALL_TIMESTAMP");
        })
        .catch((error) => {
          throw error;
        });
    },
  },
};

export default store;
