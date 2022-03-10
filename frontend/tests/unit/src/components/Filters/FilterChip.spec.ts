import FilterChip from "@/components/Filters/FilterChip.vue";
import { shallowMount, VueWrapper } from "@vue/test-utils";
import { TestingOptions } from "@pinia/testing";
import { useFilterStore } from "@/stores/filter";
import { useModalStore } from "@/stores/modal";
import { alertFilters } from "@/etc/configuration/test/alerts";
import { inputTypes } from "@/etc/constants/base";
import { createCustomPinia } from "@unit/helpers";
import { testConfiguration } from "@/etc/configuration/test/index";
import { userReadFactory } from "../../../../mocks/user";
import { genericObjectReadFactory } from "../../../../mocks/genericObject";

describe("FilterChip.vue", () => {
  function factory(
    options?: TestingOptions,
    props: { filterName: string; filterValue: any } = {
      filterName: "name",
      filterValue: "test",
    },
    nodeType = "alerts",
  ) {
    const wrapper: VueWrapper<any> = shallowMount(FilterChip, {
      props: props,
      global: {
        plugins: [
          createCustomPinia({
            ...options,
            initialState: {
              authStore: {
                user: userReadFactory({
                  defaultAlertQueue: genericObjectReadFactory({
                    value: "external",
                  }),
                  defaultEventQueue: genericObjectReadFactory({
                    value: "external",
                  }),
                }),
              },
              currentUserSettingsStore: {
                queues: {
                  alerts: genericObjectReadFactory({ value: "external" }),
                  events: genericObjectReadFactory({ value: "external" }),
                },
              },
            },
          }),
        ],
        provide: {
          nodeType: nodeType,
          config: testConfiguration,
        },
      },
    });

    const filterStore = useFilterStore();
    const modalStore = useModalStore();

    return { wrapper, filterStore, modalStore };
  }

  it("renders", () => {
    const { wrapper } = factory();

    expect(wrapper.exists()).toBe(true);
  });
  it("correctly receives injected data", () => {
    const { wrapper } = factory();

    expect(wrapper.vm.props.filterName).toEqual("name");
    expect(wrapper.vm.props.filterValue).toEqual("test");
  });
  it("correctly receives props", () => {
    const { wrapper } = factory();
    expect(wrapper.vm.nodeType).toEqual("alerts");
  });
  it("correctly sets queue when nodeType is 'alerts'", () => {
    const { wrapper } = factory();
    expect(wrapper.vm.queue).toEqual("external");
    wrapper.vm.currentUserSettingsStore.queues.alerts =
      genericObjectReadFactory({
        value: "internal",
      });
    expect(wrapper.vm.queue).toEqual("internal");
  });
  it("correctly sets queue when nodeType is unknown", () => {
    const { wrapper } = factory(undefined, undefined, "unknown");
    expect(wrapper.vm.queue).toBeNull();
    wrapper.vm.currentUserSettingsStore.queues.alerts =
      genericObjectReadFactory({
        value: "internal",
      });
    expect(wrapper.vm.queue).toBeNull();
  });
  it("correctly sets filterNameObject given a valid filterName", () => {
    const { wrapper } = factory();

    expect(wrapper.vm.filterNameObject).toEqual({
      name: "name",
      label: "Name",
      type: inputTypes.INPUT_TEXT,
    });
  });
  it("correctly sets filterNameObject given an unknown filter", () => {
    const { wrapper } = factory(undefined, {
      filterName: "unknown",
      filterValue: "test",
    });

    expect(wrapper.vm.filterNameObject).toBeUndefined();
  });
  it("correctly computes filterLabel", () => {
    const { wrapper } = factory();

    expect(wrapper.vm.filterLabel).toEqual("Name");
  });
  it("correctly computes filterLabel when filterNameObject undefined", () => {
    const { wrapper } = factory(undefined, undefined, "unknown");
    expect(wrapper.vm.filterLabel).toEqual("");
  });
  it("unsets the current filter on unsetFilter", () => {
    const { wrapper, filterStore } = factory({ stubActions: false });
    filterStore.alerts = {
      name: "test",
      testFilter2: { value: "test2" },
    };

    expect(wrapper.vm.unsetFilter());
    expect(filterStore.alerts).toEqual({
      testFilter2: { value: "test2" },
    });
  });
  it("correctly formats a given filterValue", () => {
    const { wrapper } = factory();
    expect(wrapper.vm.formatValue("test")).toEqual("test");
  });
  it("correctly formats a given filterValue when filterNameObject is undefined", () => {
    const { wrapper } = factory(undefined, undefined, "unknown");
    expect(wrapper.vm.formatValue("test")).toEqual("test");
  });
  it("correctly formats a given filterValue when filterNameObject when stringRepr is available", () => {
    const { wrapper } = factory(undefined, {
      filterName: "tags",
      filterValue: ["testA", "testB"],
    });
    expect(wrapper.vm.formatValue(["testA", "testB"])).toEqual("testA,testB");
  });
  it("correctly formats a given filterValue when filterNameObject when optionProperty is available and filterValue is an object", () => {
    const { wrapper } = factory(undefined, {
      filterName: "owner",
      filterValue: { username: "analyst", displayName: "Analyst Name" },
    });
    expect(
      wrapper.vm.formatValue({
        username: "analyst",
        displayName: "Analyst Name",
      }),
    ).toEqual("Analyst Name");
  });
  it("correctly formats a given filterValue when filterNameObject when optionProperty is available and filterValue is not an object", () => {
    const { wrapper } = factory(undefined, {
      filterName: "owner",
      filterValue: "invalidFilterValue",
    });
    expect(wrapper.vm.formatValue("invalidFilterValue")).toEqual(
      "invalidFilterValue",
    );
  });
  it("correctly sets filterModel on mount", () => {
    const { wrapper } = factory();
    expect(wrapper.vm.filterModel).toEqual({
      propertyType: "name",
      propertyValue: "test",
    });
  });
  it("correctly resets filterModel on resetFilterModel", () => {
    const { wrapper } = factory();
    wrapper.vm.filterModel = undefined;
    wrapper.vm.resetFilterModel();
    expect(wrapper.vm.filterModel).toEqual({
      propertyType: "name",
      propertyValue: "test",
    });
  });
  it("updates the filterStore with set filterModel on updateFilter", () => {
    const { wrapper, filterStore } = factory({ stubActions: false });
    wrapper.vm.updateFilter();
    expect(filterStore.alerts).toEqual({ name: "test" });
  });
});