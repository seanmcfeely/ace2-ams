import TheLogin from "@/pages/User/TheLogin.vue";
import store from "./mockStore";
import { shallowMount } from "@vue/test-utils";

describe("TheLogin.vue", () => {
  const wrapper = shallowMount(TheLogin, {
    global: {
      plugins: [store],
    },
  });
  it("renders", () => {
    expect(wrapper.exists()).toBe(true);
  });
});
