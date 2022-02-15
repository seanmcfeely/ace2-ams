import AlertTableExpansion from "@/components/Alerts/AlertTableExpansion.vue";
import { flushPromises, mount, VueWrapper } from "@vue/test-utils";
import { TestingOptions } from "@pinia/testing";
import { useFilterStore } from "@/stores/filter";
import myNock from "@unit/services/api/nock";
import nock from "nock";
import { createCustomPinia } from "@unit/helpers";

function factory(
  options: TestingOptions = {},
  observables: unknown = [
    { type: { value: "type_A" }, value: "value_A", tags: [] },
    { type: { value: "type_A" }, value: "value_C", tags: [] },
    { type: { value: "type_B" }, value: "value_A", tags: [] },
    { type: { value: "type_B" }, value: "value_B", tags: [] },
    { type: { value: "type_C" }, value: "value_C", tags: [] },
  ],
) {
  const wrapper: VueWrapper<any> = mount(AlertTableExpansion, {
    global: {
      plugins: [createCustomPinia(options)],
      provide: { nodeType: "alerts" },
    },
    props: {
      observables: observables,
      uuid: "05975cf2-fd3d-4485-a03f-7cbc1e7efbbc",
    },
  });

  const filterStore = useFilterStore();

  return { wrapper, filterStore };
}

describe("AlertTableExpansion", () => {
  it("renders", () => {
  myNock
    .post("/node/tree/observable", '["05975cf2-fd3d-4485-a03f-7cbc1e7efbbc"]')
    .reply(200, [
      { type: { value: "type_B" }, value: "value_B", tags: [] },
      { type: { value: "type_C" }, value: "value_C", tags: [] },
      { type: { value: "type_B" }, value: "value_A", tags: [] },
      { type: { value: "type_A" }, value: "value_A", tags: [] },
      { type: { value: "type_A" }, value: "value_C", tags: [] },
    ])
    .persist();

  afterAll(async () => {
    await flushPromises();
    nock.cleanAll();
  });

  it("correctly computes isLoading as true when observables prop is null", () => {
    const { wrapper } = factory({}, null);
    expect(wrapper.vm.isLoading).toBeTruthy();
  });
  it("correctly fetches, sets, and sorts observables on getObservables", async () => {
    const { wrapper } = factory();

    await wrapper.vm.getObservables("05975cf2-fd3d-4485-a03f-7cbc1e7efbbc");

    expect(wrapper.vm.observables).toEqual([
      { type: { value: "type_A" }, value: "value_A", tags: [] },
      { type: { value: "type_A" }, value: "value_C", tags: [] },
      { type: { value: "type_B" }, value: "value_A", tags: [] },

  it("correctly computes isLoading as true when observables prop is not null", () => {
    const { wrapper } = factory();
    expect(wrapper.vm.isLoading).toBeFalsy();
  });

  it("correctly formats a given observable object into string", () => {
    const { wrapper } = factory();
    const result = wrapper.vm.formatObservable({
      type: { value: "type_B" },
      value: "value_B",
      tags: [],
    });
    expect(result).toEqual("type_B : value_B");
  });

  it("correctly sets an observable filter on filterByObservable", () => {
    const { wrapper, filterStore } = factory({ stubActions: false });
    wrapper.vm.filterByObservable({
      type: { value: "type_B" },
      value: "value_B",
      tags: [],
    });
    expect(filterStore.alerts).toEqual({
      observable: { category: { value: "type_B" }, value: "value_B" },
    });
  });
});
