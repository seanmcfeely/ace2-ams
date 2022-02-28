import AnalyzeAlertForm from "@/components/Alerts/AnalyzeAlertForm.vue";
import Button from "primevue/button";
import Calendar from "primevue/calendar";
import Card from "primevue/card";
import Dropdown from "primevue/dropdown";
import Fieldset from "primevue/fieldset";
import FileUpload from "primevue/fileupload";
import InputText from "primevue/inputtext";
import Message from "primevue/message";
import MultiSelect from "primevue/multiselect";
import TabPanel from "primevue/tabpanel";
import TabView from "primevue/tabview";
import { mount, VueWrapper } from "@vue/test-utils";
import PrimeVue from "primevue/config";
import moment from "moment-timezone";
import myNock from "@unit/services/api/nock";
import nock from "nock";
import router from "@/router";
import { userReadFactory } from "../../../../mocks/user";
import { TestingOptions } from "@pinia/testing";

import snakecaseKeys from "snakecase-keys";
import { createCustomPinia } from "@unit/helpers";

function factory(options?: TestingOptions) {
  const wrapper: VueWrapper<any> = mount(AnalyzeAlertForm, {
    global: {
      plugins: [createCustomPinia(options), PrimeVue, router],
    },
  });

  wrapper.vm.authStore.user = userReadFactory({ username: "analyst" });

  return { wrapper };
}

// DATA/CREATION
describe("AnalyzeAlertForm data/creation", () => {
  const { wrapper } = factory();

  it("renders", () => {
    expect(wrapper.exists()).toBe(true);
  });

  it("contains expected components upon creation", () => {
    expect(wrapper.findComponent(Button).exists()).toBe(true);
    expect(wrapper.findComponent(Calendar).exists()).toBe(true);
    expect(wrapper.findComponent(Card).exists()).toBe(true);
    expect(wrapper.findComponent(Dropdown).exists()).toBe(true);
    expect(wrapper.findComponent(Fieldset).exists()).toBe(true);
    expect(wrapper.findComponent(FileUpload).exists()).toBe(true);
    expect(wrapper.findComponent(InputText).exists()).toBe(true);
    expect(wrapper.findComponent(MultiSelect).exists()).toBe(true);
    expect(wrapper.findComponent(TabPanel).exists()).toBe(true);
    expect(wrapper.findComponent(TabView).exists()).toBe(true);
    expect(wrapper.findComponent(Message).exists()).toBe(false); // shouldn't be visible on component load
  });
});

// COMPUTED DATA
describe("AnalyzeAlertForm computed data", () => {
  const { wrapper } = factory();

  beforeEach(async () => {
    wrapper.vm.initData();
  });

  it("adjustedAlertDate", () => {
    let adjustedAlertDate = moment(wrapper.vm.alertDate)
      .tz(moment.tz.guess())
      .format();
    expect(wrapper.vm.adjustedAlertDate).toEqual(adjustedAlertDate);
    wrapper.vm.timezone = "UTC";
    adjustedAlertDate = moment(wrapper.vm.alertDate).tz("UTC").format();
    expect(wrapper.vm.adjustedAlertDate).toEqual(adjustedAlertDate);
  });

  it("alertDescriptionFormatted", () => {
    expect(wrapper.vm.alertDescriptionFormatted).toEqual("Manual Alert");
    wrapper.vm.alertDescriptionAppendString = " new_string";
    expect(wrapper.vm.alertDescriptionFormatted).toEqual(
      "Manual Alert new_string",
    );
  });

  it("observablesListEmpty", () => {
    expect(wrapper.vm.observablesListEmpty).toBe(false);
    wrapper.vm.observables = [];
    expect(wrapper.vm.observablesListEmpty).toBe(true);
  });

  it("lastObservableIndex", () => {
    expect(wrapper.vm.lastObservableIndex).toEqual(0);
    wrapper.vm.observables = ["1", "2", "3"];
    expect(wrapper.vm.lastObservableIndex).toEqual(2);
  });
});

// METHOD MOCKS/STUBS

const readAlertStub = {
  alert: {
    uuid: "alertID",
  },
  analyses: [],
  observables: [],
};

const expectedObservableCreate = {
  type: "ipv4",
  value: "1.2.3.4",
};

const observableStub = {
  time: null,
  multiAdd: false,
  type: "ipv4",
  value: "1.2.3.4",
  directives: [],
};

const multiObservableCommaStub = {
  time: null,
  multiAdd: true,
  type: "ipv4",
  value: "0.0.0.0,4.3.2.1",
  directives: [],
};

// NON-ASYNC METHODS
describe("AnalyzeAlertForm non-async methods", () => {
  const { wrapper } = factory({ stubActions: false });

  const multiObservableNewlineStub = {
    time: null,
    multiAdd: true,
    type: "ipv4",
    value: "0.0.0.0\n4.3.2.1",
    directives: [],
  };

  it("initializes data as expected", () => {
    expect(wrapper.vm.addingObservables).toEqual(false);
    expect(wrapper.vm.alertCreateLoading).toEqual(false);
    expect(wrapper.vm.alertDate).toBeInstanceOf(Date);
    expect(wrapper.vm.alertDescription).toEqual("Manual Alert");
    expect(wrapper.vm.alertDescriptionAppendString).toEqual("");
    expect(wrapper.vm.queue).toEqual("external");
    expect(wrapper.vm.alertType).toBe("manual");
    expect(wrapper.vm.errors).toStrictEqual([]);
    expect(wrapper.vm.observables).toStrictEqual([
      {
        time: null,
        type: "file",
        multiAdd: false,
        value: null,
        directives: [],
      },
    ]);
    expect(wrapper.vm.splitButtonOptions[0].label).toStrictEqual(
      "Create multiple alerts",
    );
    expect(wrapper.vm.splitButtonOptions[0].icon).toStrictEqual("pi pi-copy");
    expect(wrapper.vm.showContinueButton).toBe(false);
    expect(wrapper.vm.timezone).toBe(moment.tz.guess());
    expect(wrapper.vm.timezones).toStrictEqual(moment.tz.names());
  });

  it("will correctly switch observable 'multiAdd' property when toggleMultiObservable is called", () => {
    expect(wrapper.vm.observables.length).toEqual(1);
    expect(wrapper.vm.observables[0].multiAdd).toBe(false);
    wrapper.vm.toggleMultiObservable(0);
    expect(wrapper.vm.observables[0].multiAdd).toBe(true);
    wrapper.vm.toggleMultiObservable(0);
    expect(wrapper.vm.observables[0].multiAdd).toBe(false);
  });

  it("will add a default observable to observables when addFormObservable is called", () => {
    expect(wrapper.vm.observables.length).toEqual(1);
    wrapper.vm.addFormObservable();
    expect(wrapper.vm.observables.length).toEqual(2);
  });

  it("will delete a given index from observables when deleteFormObservable is called", () => {
    wrapper.vm.observables = ["1", "2", "3"];
    wrapper.vm.deleteFormObservable(1);
    expect(wrapper.vm.observables.length).toEqual(2);
    expect(wrapper.vm.observables.includes("2")).toBe(false);
  });

  it("will correctly use the moment library to format a given string with a given timezone", () => {
    const testDate = "2021-10-28T00:00:00.000Z";
    const testTimezone = "EST";
    const adjustedTimezone = wrapper.vm.adjustForTimezone(
      testDate,
      testTimezone,
    );
    expect(adjustedTimezone).toEqual("2021-10-27T19:00:00-05:00");
  });

  it("will correctly return whether a given index is the last in the observables list in isLastObservable", () => {
    wrapper.vm.observables = ["1", "2", "3"];
    expect(wrapper.vm.isLastObservable(2)).toEqual(true);
    expect(wrapper.vm.isLastObservable(1)).toEqual(false);
  });

  it("will add a correctly built string to the errors list when addError is called", () => {
    wrapper.vm.addError("test example", new Error("test error"));
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0]).toEqual({
      content: "Could not create test example: Error: test error null",
    });
  });

  it("will remove a given error when handleError is called", () => {
    wrapper.vm.errors = ["1", "2", "3"];
    wrapper.vm.handleError(1);
    expect(wrapper.vm.errors.length).toEqual(2);
    expect(wrapper.vm.errors.includes("2")).toBe(false);
  });

  it("will correctly generate a submission observable from a form observable", () => {
    const testObservableWithTime = {
      ...observableStub,
      time: "2021-10-28T00:00:00.000Z",
    };
    wrapper.vm.timezone = "UTC";
    wrapper.vm.alertStore.openAlert = readAlertStub;

    const submissionObservableWithoutTime =
      wrapper.vm.generateSubmissionObservable(observableStub);
    const submissionObservableWithTime =
      wrapper.vm.generateSubmissionObservable(testObservableWithTime);
    expect(submissionObservableWithoutTime).toEqual(expectedObservableCreate);
    expect(submissionObservableWithTime).toEqual({
      ...expectedObservableCreate,
      time: "2021-10-28T00:00:00Z",
    });
  });

  it("will split a 'multi' form observable into multiple single form observables", () => {
    const splitMultiObservableComma = wrapper.vm.splitMultiObservable(
      multiObservableCommaStub,
    );
    const splitMultiObservableNewline = wrapper.vm.splitMultiObservable(
      multiObservableNewlineStub,
    );
    expect(splitMultiObservableComma.length).toEqual(2);
    expect(splitMultiObservableComma[0].value).toEqual("0.0.0.0");
    expect(splitMultiObservableComma[1].value).toEqual("4.3.2.1");

    expect(splitMultiObservableNewline.length).toEqual(2);
    expect(splitMultiObservableNewline[0].value).toEqual("0.0.0.0");
    expect(splitMultiObservableNewline[1].value).toEqual("4.3.2.1");
  });

  it("will expand the multi observables in observables form list to return a list of all single observables", () => {
    wrapper.vm.observables = [multiObservableCommaStub, observableStub];

    const expandedObservables = wrapper.vm.expandObservablesList();
    expect(expandedObservables.length).toEqual(3);
    expect(expandedObservables[0]).toEqual({
      time: null,
      type: "ipv4",
      value: "0.0.0.0",
    });
    expect(expandedObservables[1]).toEqual({
      time: null,
      type: "ipv4",
      value: "4.3.2.1",
    });
    expect(expandedObservables[2]).toEqual(observableStub);
  });
});

// ASYNC METHODS
describe("AnalyzeAlertForm async methods", () => {
  const { wrapper } = factory({ stubActions: false });

  const expectedAlertCreate = {
    alertDescription: "Manual Alert",
    eventTime: moment(wrapper.vm.alertDate).tz(moment.tz.guess()).format(),
    name: "Manual Alert",
    observables: [expectedObservableCreate],
    owner: "analyst",
    queue: "external",
    type: "manual",
  };

  const alertCreateErrorMessage =
    'Could not create alert Manual Alert: Error: Request failed with status code 404 "Create failed"';

  beforeEach(async () => {
    wrapper.vm.initData();
    expectedAlertCreate.eventTime = moment(wrapper.vm.alertDate)
      .tz(moment.tz.guess())
      .format();
  });
  afterEach(async () => {
    nock.cleanAll();
  });

  // submitAlert
  it("will submit an alert to the backend using when submitAlert is called", async () => {
    const alertCreate = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(201, "Create successful");

    await wrapper.vm.submitAlert([{ type: "ipv4", value: "1.2.3.4" }]);
    expect(alertCreate.isDone()).toBe(true);
  });

  it("will add an error to errors when submitAlert is called and the API call fails", async () => {
    const alertCreateFail = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(404, "Create failed");

    await wrapper.vm.submitAlert([expectedObservableCreate]);
    expect(alertCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(alertCreateErrorMessage);
  });

  // submitSingleAlert
  it("will not make an API call if there is an error present", async () => {
    const alertCreate = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys(
            snakecaseKeys({
              ...expectedAlertCreate,
              observables: [
                { type: "ipv4", value: "1.2.3.4" },
                { type: "ipv4", value: "1.2.3.4" },
              ],
            }),
          ),
        ),
      )
      .reply(201, readAlertStub);

    wrapper.vm.errors = ["blah"];
    wrapper.vm.observables = [observableStub, observableStub];

    await wrapper.vm.submitSingleAlert();
    expect(alertCreate.isDone()).toBe(false);
    expect(wrapper.vm.errors.length).toEqual(1);
  });

  it("will attempt to route the new alert page when submitSingleAlert is called and completes successfully", async () => {
    const alertCreate = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys(
            snakecaseKeys({
              ...expectedAlertCreate,
              observables: [
                { type: "ipv4", value: "1.2.3.4" },
                { type: "ipv4", value: "1.2.3.4" },
              ],
            }),
          ),
        ),
      )
      .reply(201, readAlertStub);

    wrapper.vm.observables = [observableStub, observableStub];

    await wrapper.vm.submitSingleAlert();
    expect(alertCreate.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(0);
  });

  it("will add an error to errors when submitSingleAlert is called and the API call fails", async () => {
    const alertCreateFail = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(404, "Create failed");

    wrapper.vm.observables = [observableStub];

    await wrapper.vm.submitSingleAlert();
    expect(alertCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(alertCreateErrorMessage);
  });

  // submitMultiAlerts
  it("will call submitMultipleAlerts when the 'Create multiple alerts' button is clicked", async () => {
    const alertCreateA = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 1.2.3.4",
            alertDescription: "Manual Alert 1.2.3.4",
            observables: [{ type: "ipv4", value: "1.2.3.4" }],
          }),
        ),
      )
      .reply(201, readAlertStub);
    const alertCreateB = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 0.0.0.0",
            alertDescription: "Manual Alert 0.0.0.0",
            observables: [{ type: "ipv4", value: "0.0.0.0" }],
          }),
        ),
      )
      .reply(201, readAlertStub);
    const alertCreateC = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 4.3.2.1",
            alertDescription: "Manual Alert 4.3.2.1",
            observables: [{ type: "ipv4", value: "4.3.2.1" }],
          }),
        ),
      )
      .reply(201, readAlertStub);

    wrapper.vm.observables = [observableStub, multiObservableCommaStub];

    await wrapper.vm.splitButtonOptions[0].command();
    expect(alertCreateA.isDone()).toBe(true);
    expect(alertCreateB.isDone()).toBe(true);
    expect(alertCreateC.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(0);
  });

  it("will make a call to create alert and add an observable for each observable to be added then route to most recent alert created when submitMultipleAlerts completes successfully", async () => {
    const alertCreateA = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 1.2.3.4",
            alertDescription: "Manual Alert 1.2.3.4",
            observables: [{ type: "ipv4", value: "1.2.3.4" }],
          }),
        ),
      )
      .reply(201, readAlertStub);
    const alertCreateB = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 0.0.0.0",
            alertDescription: "Manual Alert 0.0.0.0",
            observables: [{ type: "ipv4", value: "0.0.0.0" }],
          }),
        ),
      )
      .reply(201, readAlertStub);
    const alertCreateC = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 4.3.2.1",
            alertDescription: "Manual Alert 4.3.2.1",
            observables: [{ type: "ipv4", value: "4.3.2.1" }],
          }),
        ),
      )
      .reply(201, readAlertStub);

    wrapper.vm.observables = [observableStub, multiObservableCommaStub];

    await wrapper.vm.submitMultipleAlerts();
    expect(alertCreateA.isDone()).toBe(true);
    expect(alertCreateB.isDone()).toBe(true);
    expect(alertCreateC.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(0);
  });

  it("will return from submitMultipleAlerts early if the first submitAlert call fails", async () => {
    const alertCreate = myNock
      .post(
        "/alert/",
        JSON.stringify(
          snakecaseKeys({
            ...expectedAlertCreate,
            name: "Manual Alert 1.2.3.4",
            alertDescription: "Manual Alert 1.2.3.4",
            observables: [{ type: "ipv4", value: "1.2.3.4" }],
          }),
        ),
      )
      .reply(403, "Create failed");

    wrapper.vm.observables = [observableStub, multiObservableCommaStub];

    await wrapper.vm.submitMultipleAlerts();
    expect(alertCreate.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(
      'Could not create alert Manual Alert 1.2.3.4: Error: Request failed with status code 403 "Create failed"',
    );
  });
});
