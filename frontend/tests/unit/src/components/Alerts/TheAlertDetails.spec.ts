import TheAlertDetails from "@/components/Alerts/TheAlertDetails.vue";
import { shallowMount, VueWrapper } from "@vue/test-utils";
import PrimeVue from "primevue/config";
import { createTestingPinia, TestingOptions } from "@pinia/testing";
import * as helpers from "@/etc/helpers";

import { createRouterMock, injectRouterMock } from "vue-router-mock";

function factory(piniaOptions: TestingOptions = {}) {
  const router = createRouterMock();
  injectRouterMock(router);

  const wrapper: VueWrapper<any> = shallowMount(TheAlertDetails, {
    global: {
      plugins: [createTestingPinia(piniaOptions), PrimeVue],
    },
  });

  return { wrapper };
}

describe("TheAlertDetails", () => {
  it("renders", () => {
    const { wrapper } = factory();
    expect(wrapper.exists()).toBe(true);
  });

  it("correctly calls copyToClipboard with current location on copyLink", () => {
    const spy = jest
      .spyOn(helpers, "copyToClipboard")
      .mockImplementationOnce(() => null);
    const { wrapper } = factory({ stubActions: false });

    wrapper.vm.copyLink();
    expect(spy).toHaveBeenCalled();
  });
});
