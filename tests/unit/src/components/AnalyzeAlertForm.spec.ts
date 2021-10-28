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
import { mount } from "@vue/test-utils";
import store from "../../../../src/store/index";
import PrimeVue from "primevue/config";
import moment from "moment-timezone";
import myNock from "@unit/services/api/nock";
import nock from "nock";
import router from "@/router";

import snakecaseKeys from "snakecase-keys";

describe("AnalyzeAlertForm.vue", () => {
  const wrapper = mount(AnalyzeAlertForm, {
    global: {
      plugins: [store, PrimeVue, router],
    },
  });

  const expectedAlertCreate = {
    alertDescription: "Manual Alert",
    eventTime: moment(wrapper.vm.alertDate).tz(moment.tz.guess()).format(),
    name: "Manual Alert",
    queue: "default",
    type: "manual",
  };

  const readAlertStub = {
    uuid: "alertID",
    analysis: {
      uuid: "analysisID",
    },
  };

  const expectedObservableCreate = {
    alertUuid: "alertID",
    parentAnalysisUuid: "analysisID",
    type: "ipv4",
    value: "1.2.3.4",
  };

  const expectedObservableCreateList = [
    expectedObservableCreate,
    expectedObservableCreate,
  ];

  const mockObservable = {
    time: null,
    multiAdd: false,
    type: "ipv4",
    value: "1.2.3.4",
    directives: [],
  };

  const mockMultiObservableComma = {
    time: null,
    multiAdd: true,
    type: "ipv4",
    value: "0.0.0.0,4.3.2.1",
    directives: [],
  };

  const mockMultiObservableNewline = {
    time: null,
    multiAdd: true,
    type: "ipv4",
    value: "0.0.0.0\n4.3.2.1",
    directives: [],
  };

  const alertCreateErrorMessage =
    'Could not create alert Manual Alert: Error: Request failed with status code 404 "Create failed"';
  const observableCreateErrorMessage =
    'Could not create at least one observable: Error: Request failed with status code 404 "Create failed"';

  beforeEach(async () => {
    myNock.persist().get("/alert/queue/").reply(200, ["default"]);
    myNock.persist().get("/alert/type/").reply(200, ["manual"]);
    myNock.persist().get("/node/directive/").reply(200, []);
    myNock.persist().get("/observable/type/").reply(200, ["file", "ipv4"]);
    wrapper.vm.initData();
    await wrapper.vm.initExternalData();
    expectedAlertCreate.eventTime = moment(wrapper.vm.alertDate)
      .tz(moment.tz.guess())
      .format();
  });
  afterEach(async () => {
    nock.cleanAll();
  });

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

  it("initializes data as expected", () => {
    expect(wrapper.vm.addingObservables).toEqual(false);
    expect(wrapper.vm.alertCreateLoading).toEqual(false);
    expect(wrapper.vm.alertDate).toBeInstanceOf(Date);
    expect(wrapper.vm.alertDescription).toEqual("Manual Alert");
    expect(wrapper.vm.alertDescriptionAppendString).toEqual("");
    expect(wrapper.vm.alertQueue).toEqual("default");
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
    expect(wrapper.vm.splitButtonOptions).toStrictEqual([
      {
        label: "Create multiple alerts",
        icon: "pi pi-copy",
        command: wrapper.vm.submitMultipleAlerts,
      },
    ]);
    expect(wrapper.vm.showContinueButton).toBe(false);
    expect(wrapper.vm.timezone).toBe(moment.tz.guess());
    expect(wrapper.vm.timezones).toStrictEqual(moment.tz.names());
  });
  it("will populate dropdowns using mapped vuex actions (which perform API calls) when initExternalData is called", async () => {
    expect(wrapper.vm.alertQueues).toStrictEqual(["default"]);
    expect(wrapper.vm.alertTypes).toStrictEqual(["manual"]);
    expect(wrapper.vm.observableTypes).toStrictEqual(["file", "ipv4"]);
    expect(wrapper.vm.directives).toStrictEqual([]);
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
    wrapper.setData({
      observables: ["1", "2", "3"],
    });
    wrapper.vm.deleteFormObservable(1);
    expect(wrapper.vm.observables.length).toEqual(2);
    expect(wrapper.vm.observables.includes("2")).toBe(false);
  });
  it("will correctly compute adjustedAlertDate", () => {
    let adjustedAlertDate = moment(wrapper.vm.alertDate)
      .tz(moment.tz.guess())
      .format();
    expect(wrapper.vm.adjustedAlertDate).toEqual(adjustedAlertDate);
    wrapper.setData({
      timezone: "UTC",
    });
    adjustedAlertDate = moment(wrapper.vm.alertDate).tz("UTC").format();
    expect(wrapper.vm.adjustedAlertDate).toEqual(adjustedAlertDate);
  });
  it("will correctly compute alertDescriptionFormatted", () => {
    expect(wrapper.vm.alertDescriptionFormatted).toEqual("Manual Alert");
    wrapper.setData({
      alertDescriptionAppendString: " new_string",
    });
    expect(wrapper.vm.alertDescriptionFormatted).toEqual(
      "Manual Alert new_string",
    );
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
  it("will correctly compute observablesListEmpty", () => {
    expect(wrapper.vm.observablesListEmpty).toBe(false);
    wrapper.setData({
      observables: [],
    });
    expect(wrapper.vm.observablesListEmpty).toBe(true);
  });
  it("will correctly compute lastObservableIndex", () => {
    expect(wrapper.vm.lastObservableIndex).toEqual(0);
    wrapper.setData({
      observables: ["1", "2", "3"],
    });
    expect(wrapper.vm.lastObservableIndex).toEqual(2);
  });
  it("will correctly return whether a given index is the last in the observables list in isLastObservable", () => {
    wrapper.setData({
      observables: ["1", "2", "3"],
    });
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
    wrapper.setData({
      errors: ["1", "2", "3"],
    });
    wrapper.vm.handleError(1);
    expect(wrapper.vm.errors.length).toEqual(2);
    expect(wrapper.vm.errors.includes("2")).toBe(false);
  });
  it("will correctly generate a submission observable from a form observable", () => {
    const testObservableWithTime = {
      ...mockObservable,
      time: "2021-10-28T00:00:00.000Z",
    };
    wrapper.setData({
      timezone: "UTC",
      openAlert: readAlertStub,
    });
    const submissionObservableWithoutTime =
      wrapper.vm.generateSubmissionObservable(mockObservable);
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
      mockMultiObservableComma,
    );
    const splitMultiObservableNewline = wrapper.vm.splitMultiObservable(
      mockMultiObservableNewline,
    );
    expect(splitMultiObservableComma.length).toEqual(2);
    expect(splitMultiObservableComma[0].value).toEqual("0.0.0.0");
    expect(splitMultiObservableComma[1].value).toEqual("4.3.2.1");

    expect(splitMultiObservableNewline.length).toEqual(2);
    expect(splitMultiObservableNewline[0].value).toEqual("0.0.0.0");
    expect(splitMultiObservableNewline[1].value).toEqual("4.3.2.1");
  });
  it("will expand the multi observables in observables form list to return a list of all single observables", () => {
    wrapper.setData({
      observables: [mockMultiObservableComma, mockObservable],
    });
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
    expect(expandedObservables[2]).toEqual(mockObservable);
  });
  it("will submit an alert to the backend using when submitAlert is called", async () => {
    const alertCreate = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(201, "Create successful");

    await wrapper.vm.submitAlert();
    expect(alertCreate.isDone()).toBe(true);
  });
  it("will add an error to errors when submitAlert is called and the API call fails", async () => {
    const alertCreateFail = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(404, "Create failed");

    await wrapper.vm.submitAlert();
    expect(alertCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(alertCreateErrorMessage);
  });
  it("will submit observables to the backend using when submitObservables is called", async () => {
    const observableCreate = myNock
      .post(
        "/observable/instance/",
        JSON.stringify(snakecaseKeys(expectedObservableCreateList)),
      )
      .reply(201, "Create successful");
    store.commit("alerts/SET_OPEN_ALERT", readAlertStub);

    await wrapper.vm.submitObservables([
      expectedObservableCreate,
      expectedObservableCreate,
    ]);
    expect(observableCreate.isDone()).toBe(true);
  });
  it("will add an error to errors when submitObservables is called and the API call fails", async () => {
    const observableCreateFail = myNock
      .post(
        "/observable/instance/",
        JSON.stringify(snakecaseKeys(expectedObservableCreateList)),
      )
      .reply(404, "Create failed");
    store.commit("alerts/SET_OPEN_ALERT", readAlertStub);

    await wrapper.vm.submitObservables([
      expectedObservableCreate,
      expectedObservableCreate,
    ]);
    expect(observableCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(observableCreateErrorMessage);
  });
  it("will attempt to route the new alert page when submitSingleAlert is called and completes successfully", async () => {
    const alertCreate = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(201, readAlertStub);

    const observableCreate = myNock
      .post(
        "/observable/instance/",
        JSON.stringify(snakecaseKeys(expectedObservableCreateList)),
      )
      .reply(201, "Create successful");

    wrapper.setData({
      observables: [mockObservable, mockObservable],
    });

    await wrapper.vm.submitSingleAlert();
    expect(alertCreate.isDone()).toBe(true);
    expect(observableCreate.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(0);
  });
  it("will display an error and not attempt to submit observables if submitSingleAlert is called and fails at submitAlert", async () => {
    const alertCreateFail = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(404, "Create failed");

    await wrapper.vm.submitSingleAlert();
    expect(alertCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(alertCreateErrorMessage);
  });
  it("will display error(s), the warning message, and continue button if submitSingleAlert is called and failures occur in submitObservables", async () => {
    const alertCreate = myNock
      .post("/alert/", JSON.stringify(snakecaseKeys(expectedAlertCreate)))
      .reply(201, readAlertStub);

    const observableCreateFail = myNock
      .post(
        "/observable/instance/",
        JSON.stringify(snakecaseKeys(expectedObservableCreateList)),
      )
      .reply(404, "Create failed");
    store.commit("alerts/SET_OPEN_ALERT", readAlertStub);

    wrapper.setData({
      observables: [mockObservable, mockObservable],
    });

    await wrapper.vm.submitSingleAlert();
    expect(alertCreate.isDone()).toBe(true);
    expect(observableCreateFail.isDone()).toBe(true);
    expect(wrapper.vm.errors.length).toEqual(1);
    expect(wrapper.vm.errors[0].content).toEqual(observableCreateErrorMessage);
  });
});
