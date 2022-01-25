import ManageEvents from "@/pages/Events/ManageEvents.vue";
import TheFilterToolbar from "@/components/Filters/TheFilterToolbar.vue";
import TheEventsTable from "@/components/Events/TheEventsTable.vue";
import TheNodeActionToolbarVue from "@/components/Node/TheNodeActionToolbar.vue";
import DateRangePicker from "@/components/UserInterface/DateRangePicker.vue";
import { mount, VueWrapper } from "@vue/test-utils";
import { createTestingPinia, TestingOptions } from "@pinia/testing";
import Tooltip from "primevue/tooltip";
import { createRouterMock, injectRouterMock } from "vue-router-mock";
import { useFilterStore } from "@/stores/filter";
import { useModalStore } from "@/stores/modal";
import * as helpers from "@/etc/helpers";

function factory(
  initialLocation = "/manage_events",
  piniaOptions?: TestingOptions,
) {
  const router = createRouterMock({
    initialLocation: initialLocation,
  });
  injectRouterMock(router);

  const wrapper = mount(ManageEvents, {
    global: {
      plugins: [createTestingPinia(piniaOptions)],
      directives: { tooltip: Tooltip },
      stubs: ["TheEventsTable", "TagModal", "FilterChipContainer"],
    },
  });

  const filterStore = useFilterStore();
  const modalStore = useModalStore();

  return { wrapper, filterStore, modalStore, router };
}

describe("ManageEvents.vue", () => {
  it("renders", () => {
    const { wrapper } = factory();
    expect(wrapper.exists()).toBe(true);
  });

  it("contains expected components", () => {
    const { wrapper } = factory();

    expect(wrapper.findComponent(TheNodeActionToolbarVue).exists()).toBe(true);
    expect(wrapper.findComponent(TheFilterToolbar).exists()).toBe(true);
    expect(wrapper.findComponent(TheEventsTable).exists()).toBe(true);
  });

  it("will not add any filters that cannot be found", () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    factory("/manage_events?fake_filter=blah");
    const filterStore = useFilterStore();

    expect(Object.keys(filterStore.alerts).length).toBeFalsy();
  });

  it("will parse given filters, set them in the filterStore, and reload on loadRouteQuery", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_events?tags=tagA,tagB",
      {
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();
    expect(filterStore.events).toEqual({
      tags: ["tagA", "tagB"],
    });

    // should route you back to /manage_events when done
    expect(router.currentRoute.value.fullPath).toEqual("/manage_events");
  });

  it("executes loadRouteQuery when route changes", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory("/manage_events", {
      stubActions: false,
    });

    await wrapper.vm.$nextTick();
    expect(filterStore.events).toEqual({});

    // push new route with query
    router.push("/manage_events?tags=tagA,tagB");
    await wrapper.vm.$nextTick();
    expect(filterStore.events).toEqual({
      tags: ["tagA", "tagB"],
    });

    // should route you back to /manage_events when done
    expect(router.currentRoute.value.fullPath).toEqual("/manage_events");
  });

  it("will attempt to load common stores if url parameters are provided", async () => {
    const spy = jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    factory("/manage_events?fake_filter=blah");
    expect(spy).toHaveBeenCalled();
  });
});
