import ManageAlerts from "@/pages/Alerts/ManageAlerts.vue";
import TheAlertActionToolbar from "@/components/Alerts/TheAlertActionToolbar.vue";
import TheFilterToolbar from "@/components/Filters/TheFilterToolbar.vue";
import TheAlertsTable from "@/components/Alerts/TheAlertsTable.vue";
import DateRangePicker from "@/components/UserInterface/DateRangePicker.vue";
import { mount, VueWrapper } from "@vue/test-utils";
import { createTestingPinia, TestingOptions } from "@pinia/testing";
import Tooltip from "primevue/tooltip";
import { createRouterMock, injectRouterMock } from "vue-router-mock";
import { useFilterStore } from "@/stores/filter";
import { useModalStore } from "@/stores/modal";
import * as helpers from "@/etc/helpers";

function factory(
  initialLocation = "/manage_alerts",
  piniaOptions?: TestingOptions,
) {
  const router = createRouterMock({
    initialLocation: initialLocation,
  });
  injectRouterMock(router);

  const wrapper = mount(ManageAlerts, {
    global: {
      plugins: [createTestingPinia(piniaOptions)],
      directives: { tooltip: Tooltip },
      stubs: ["TheAlertsTable", "TagModal", "FilterChipContainer"],
    },
  });

  const filterStore = useFilterStore();
  const modalStore = useModalStore();

  return { wrapper, filterStore, modalStore, router };
}

describe("ManageAlerts.vue", () => {
  it("renders", () => {
    const { wrapper } = factory();
    expect(wrapper.exists()).toBe(true);
  });

  it("contains expected components", () => {
    const { wrapper } = factory();

    expect(wrapper.findComponent(TheAlertActionToolbar).exists()).toBe(true);
    expect(wrapper.findComponent(TheFilterToolbar).exists()).toBe(true);
    expect(wrapper.findComponent(TheAlertsTable).exists()).toBe(true);
  });

  it("executes loadRouteQuery route changes", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory("/manage_alerts", {
      stubActions: false,
    });

    await wrapper.vm.$nextTick();
    expect(filterStore.alerts).toEqual({});

    // push new route with query
    router.push("/manage_alerts?tags=tagA,tagB");
    await wrapper.vm.$nextTick();
    expect(filterStore.alerts).toEqual({
      tags: ["tagA", "tagB"],
    });

    // should route you back to /manage_alerts when done
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("provides the correct data to be injected", () => {
    const { wrapper } = factory();

    // All of the data provided by the ManageAlerts component is injected into the DateRangePicker child component
    // We can therefore find it and check its data for all the injected data

    const datepicker = wrapper.findComponent(
      DateRangePicker,
    ) as VueWrapper<any>;
    expect(datepicker.vm.filterType).toEqual("alerts");
    expect(datepicker.vm.rangeFilterOptions).toEqual([
      "Event Time",
      "Insert Time",
      "Disposition Time",
    ]);
    expect(datepicker.vm.rangeFilters).toEqual({
      "Event Time": { start: "eventTimeAfter", end: "eventTimeBefore" },
      "Insert Time": { start: "insertTimeAfter", end: "insertTimeBefore" },
      "Disposition Time": {
        start: "dispositionedAfter",
        end: "dispositionedBefore",
      },
    });
  });

  it("will attempt to load common stores if url parameters are provided", async () => {
    const spy = jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    factory("/manage_alerts?fake_filter=blah");
    expect(spy).toHaveBeenCalled();
  });

  it("will not add any filters that cannot be found", () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    factory("/manage_alerts?fake_filter=blah");
    const filterStore = useFilterStore();

    expect(Object.keys(filterStore.alerts).length).toBeFalsy();
  });

  it("will correctly parse and add any multiselect filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?observableTypes=ipv4,file,fake",
      {
        initialState: {
          observableTypeStore: {
            items: [{ value: "ipv4" }, { value: "file" }],
          },
        },
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      observableTypes: [{ value: "ipv4" }, { value: "file" }],
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("will correctly parse and add any chips filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?tags=tagA,tagB",
      {
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      tags: ["tagA", "tagB"],
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("will correctly parse and add any select filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?owner=analystB",
      {
        initialState: {
          userStore: {
            items: [{ username: "analystA" }, { username: "analystB" }],
          },
        },
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      owner: { username: "analystB" },
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("will correctly parse and add any date filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?eventTimeBefore=Sat+Jan+08+2022+11%3A31%3A51+GMT-0500+%28Eastern+Standard+Time%29",
      {
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      eventTimeBefore: new Date("2022-01-08T16:31:51.000Z"),
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("will skip any date filters that fail to parse", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?eventTimeBefore=Bad+Date",
      {
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({});
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });

  it("will correctly parse and add any input text filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?name=test+name",
      {
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      name: "test name",
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });
  it("will correctly parse and add any catetgorized value filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?observable=ipv4%7C1.2.3.4",
      {
        initialState: {
          observableTypeStore: {
            items: [{ value: "ipv4" }, { value: "file" }],
          },
        },
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      observable: { category: { value: "ipv4" }, value: "1.2.3.4" },
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });
  it("will correctly parse and add any combined filters", async () => {
    jest
      .spyOn(helpers, "populateCommonStores")
      .mockImplementationOnce(() => Promise.resolve());
    const { wrapper, filterStore, router } = factory(
      "/manage_alerts?observable=ipv4%7C1.2.3.4&eventTimeBefore=Sat+Jan+08+2022+11%3A31%3A51+GMT-0500+%28Eastern+Standard+Time%29&name=test+name&observableTypes=ipv4,file,fake&fake=blah&owner=analystB&tags=tagA,tagB",
      {
        initialState: {
          observableTypeStore: {
            items: [{ value: "ipv4" }, { value: "file" }],
          },
          userStore: {
            items: [{ username: "analystA" }, { username: "analystB" }],
          },
        },
        stubActions: false,
      },
    );

    await wrapper.vm.$nextTick();

    expect(filterStore.alerts).toEqual({
      tags: ["tagA", "tagB"],
      owner: { username: "analystB" },
      observableTypes: [{ value: "ipv4" }, { value: "file" }],
      eventTimeBefore: new Date("2022-01-08T16:31:51.000Z"),
      name: "test name",
      observable: { category: { value: "ipv4" }, value: "1.2.3.4" },
    });
    expect(router.currentRoute.value.fullPath).toEqual("/manage_alerts");
  });
});
