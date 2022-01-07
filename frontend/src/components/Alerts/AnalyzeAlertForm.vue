<template>
  <TabView>
    <TabPanel key="basic" header="Basic">
      <Card>
        <template #title>Alert Details </template>
        <template #content>
          <div class="formgrid grid">
            <div class="field col-4">
              <InputText
                id="description"
                v-model="alertDescription"
                placeholder="Alert Description"
                class="inputfield w-full"
                type="text"
              ></InputText>
            </div>
          </div>

          <br />

          <Fieldset legend="Advanced" :toggleable="true" :collapsed="true">
            <div class="formgrid grid">
              <div class="field col-4">
                <label for="alert-date">Alert Datetime</label>
                <Calendar
                  id="alert-date"
                  v-model="alertDate"
                  class="inputfield w-full"
                  :show-time="true"
                  :show-seconds="true"
                />
              </div>
            </div>
            <div class="formgrid grid">
              <div class="field col-4">
                <label for="timezone">Timezone</label>
                <Dropdown
                  id="timezone"
                  v-model="timezone"
                  class="inputfield w-full"
                  :options="timezones"
                />
              </div>
            </div>
            <div class="formgrid grid">
              <div class="field col-4">
                <label for="type">Alert Type</label>
                <Dropdown
                  id="type"
                  v-model="alertType"
                  class="inputfield w-full"
                  :options="alertTypeStore.items"
                  option-label="value"
                  option-value="value"
                />
              </div>
            </div>
            <div class="formgrid grid">
              <div class="field col-4">
                <label for="queue">Queue</label>
                <Dropdown
                  id="queue"
                  v-model="alertQueue"
                  class="inputfield w-full"
                  :options="alertQueueStore.items"
                  option-label="value"
                  option-value="value"
                />
              </div>
            </div>
          </Fieldset>
        </template>
      </Card>

      <br />

      <Card>
        <template #title>Observables </template>
        <template #content>
          <div id="observables-list">
            <div class="formgrid grid">
              <div class="field col-2 px-1">
                <label for="observable-time">Time</label>
              </div>
              <div class="field col-2 px-1">
                <label for="observable-type">Type</label>
              </div>
              <div class="field col-3 px-1">
                <label for="observable-value">Value</label>
              </div>
              <div class="field col-3 px-1">
                <label for="observable-directives">Directives</label>
              </div>
              <div class="field col-1">
                <Button
                  v-if="observablesListEmpty"
                  id="add-observable-empty"
                  icon="pi pi-plus"
                  class="p-button-rounded inputfield"
                  @click="addFormObservable"
                />
              </div>
            </div>
            <div
              v-for="(observable, index) in observables"
              :key="observable.index"
              name="observable-input"
              class="p-col-12"
            >
              <div class="formgrid grid">
                <div class="field col-2 px-1">
                  <Calendar
                    v-model="observables[index].time"
                    name="observable-time"
                    placeholder="No time selected"
                    class="inputfield w-full"
                    :show-time="true"
                    :show-seconds="true"
                  />
                </div>
                <div class="field col-2 px-1">
                  <Dropdown
                    v-model="observables[index].type"
                    name="observable-type"
                    class="inputfield w-full"
                    option-label="value"
                    option-value="value"
                    :options="observableTypeStore.items"
                  />
                </div>
                <div class="field col-3 px-1" name="observable-value">
                  <FileUpload
                    v-if="observables[index].type == 'file'"
                    mode="basic"
                    class="inputfield w-full"
                  ></FileUpload>
                  <div v-else class="p-inputgroup">
                    <InputText
                      v-if="!observables[index].multiAdd"
                      v-model="observables[index].value"
                      placeholder="Enter a value"
                      class="inputfield w-full"
                      type="text"
                    ></InputText>
                    <Textarea
                      v-else
                      v-model="observables[index].value"
                      placeholder="Enter a comma or newline-delimited list of values"
                      class="inputfield w-full"
                    ></Textarea>
                    <Button
                      icon="pi pi-list"
                      @click="toggleMultiObservable(index)"
                    />
                  </div>
                </div>
                <div class="field col-3 px-1">
                  <MultiSelect
                    v-model="observables[index].directives"
                    name="observable-directives"
                    placeholder="No directives selected"
                    class="inputfield w-full"
                    :options="nodeDirectiveStore.items"
                  />
                </div>
                <div class="field col-1">
                  <Button
                    name="delete-observable"
                    icon="pi pi-times"
                    class="inputfield"
                    @click="deleteFormObservable(index)"
                  />
                </div>
                <div class="field col-1">
                  <Button
                    v-if="isLastObservable(index)"
                    id="add-observable"
                    label="Add"
                    icon="pi pi-plus"
                    class="p-button-rounded inputfield"
                    @click="addFormObservable"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <br />
    </TabPanel>
  </TabView>
  <div class="pl-3">
    <SplitButton
      label="Analyze!"
      :loading="alertCreateLoading"
      :disabled="showContinueButton"
      :model="splitButtonOptions"
      class="p-button-lg"
      @click="submitSingleAlert"
    />
  </div>
  <Message v-if="addingObservables" severity="info"
    >Alert created, now adding Observables...</Message
  >
  <Message v-if="showContinueButton" severity="info"
    >Oh dear, it looks like some observables couldn't be created... The errors
    below might help explain what went wrong. You can try adding the observables
    again on the next page!</Message
  >
  <Message
    v-for="(error, index) of errors"
    :key="error.content"
    severity="error"
    @close="handleError(index)"
    >{{ error.content }}</Message
  >
  <div class="pl-3">
    <Button
      v-if="showContinueButton"
      label="On with it then..."
      class="p-button-lg"
      @click="routeToNewAlert"
    />
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from "vue";
  import { useRouter } from "vue-router";

  import Button from "primevue/button";
  import Calendar from "primevue/calendar";
  import Card from "primevue/card";
  import Dropdown from "primevue/dropdown";
  import Fieldset from "primevue/fieldset";
  import FileUpload from "primevue/fileupload";
  import InputText from "primevue/inputtext";
  import Message from "primevue/message";
  import MultiSelect from "primevue/multiselect";
  import SplitButton from "primevue/splitbutton";
  import TabPanel from "primevue/tabpanel";
  import TabView from "primevue/tabview";
  import Textarea from "primevue/textarea";

  import moment from "moment-timezone";

  import { useAlertStore } from "@/stores/alert";
  import { useAlertQueueStore } from "@/stores/alertQueue";
  import { useAlertTypeStore } from "@/stores/alertType";
  import { useNodeDirectiveStore } from "@/stores/nodeDirective";
  import { useObservableTypeStore } from "@/stores/observableType";

  const router = useRouter();

  const alertStore = useAlertStore();
  const alertQueueStore = useAlertQueueStore();
  const alertTypeStore = useAlertTypeStore();
  const nodeDirectiveStore = useNodeDirectiveStore();
  const observableTypeStore = useObservableTypeStore();

  const addingObservables = ref(false);
  const alertCreateLoading = ref(false);
  const alertDate = ref(Date());
  const alertDescription = ref("Manual Alert");
  const alertDescriptionAppendString = ref("");
  const alertQueue = ref("default");
  const alertType = ref("manual");
  const errors = ref([]);
  const splitButtonOptions = ref([
    {
      label: "Create multiple alerts",
      icon: "pi pi-copy",
      command: async () => {
        await submitMultipleAlerts();
      },
    },
  ]);
  const observables = ref([]);
  const showContinueButton = ref(false);
  const timezone = ref(moment.tz.guess());
  const timezones = moment.tz.names();

  const adjustedAlertDate = computed(() => {
    return adjustForTimezone(alertDate.value, timezone.value);
  });

  const alertDescriptionFormatted = computed(() => {
    return `${alertDescription.value}${alertDescriptionAppendString.value}`;
  });

  const observablesListEmpty = computed(() => {
    return !observables.value.length;
  });

  const lastObservableIndex = computed(() => {
    return observables.value.length - 1;
  });

  onMounted(async () => {
    initData();
    await initExternalData();
  });

  const addError = (object, error) => {
    let responseError = null;
    if (error.response) {
      responseError = JSON.stringify(error.response.data);
    }
    errors.value.push({
      content: `Could not create ${object}: ${error} ${responseError}`,
    });
  };

  const addFormObservable = () => {
    observables.value.push({
      time: null,
      type: "file",
      multiAdd: false,
      value: null,
      directives: [],
    });
  };

  const adjustForTimezone = (datetime, timezone) => {
    return moment(datetime).tz(timezone).format();
  };

  const deleteFormObservable = (index) => {
    observables.value.splice(index, 1);
  };

  // Generate a list of all observables (single observables plus expanded multi-observables)
  const expandObservablesList = () => {
    let _observables = [];
    for (const obs_index in observables.value) {
      let current_observable = observables.value[obs_index];
      if (current_observable.multiAdd) {
        const splitObservables = splitMultiObservable(current_observable);
        _observables = [..._observables, ...splitObservables];
      } else {
        _observables.push(current_observable);
      }
    }
    return _observables;
  };

  // Given an observable object, return a formatted observable instance 'create' object
  const generateSubmissionObservable = (observable) => {
    const submissionObservable = {
      type: observable.type,
      value: observable.value,
    };
    if (observable.time) {
      submissionObservable["time"] = adjustForTimezone(
        observable.time,
        timezone.value,
      );
    }
    return submissionObservable;
  };

  const handleError = (index) => {
    errors.value.splice(index, 1);
  };

  const initData = () => {
    alertDate.value = new Date();
    alertDescription.value = "Manual Alert";
    alertDescriptionAppendString.value = "";
    alertType.value = "manual";
    alertQueue.value = "default";
    errors.value = [];
    timezone.value = moment.tz.guess();
    observables.value = [];
    addFormObservable();
  };

  const initExternalData = async () => {
    await alertQueueStore.readAll();
    await alertTypeStore.readAll();
    await nodeDirectiveStore.readAll();
    await observableTypeStore.readAll();
  };

  const isLastObservable = (index) => {
    return index == lastObservableIndex.value;
  };

  const routeToNewAlert = () => {
    router.push({ path: `/alert/${alertStore.openAlert.uuid}` });
  };

  // Given a multi-observable object, expand into a list of single observable objects for each sub-value
  const splitMultiObservable = (multiObservable) => {
    // Determine split character -- can be newline or comma
    let splitValues = [];
    var containsNewline = /\r?\n/.exec(multiObservable.value);
    if (containsNewline) {
      splitValues = multiObservable.value.split(/\r?\n/);
    } else {
      splitValues = multiObservable.value.split(",");
    }
    // Split and return new list
    const splitObservables = [];
    for (const index in splitValues) {
      const subObservable = {
        type: multiObservable.type,
        value: splitValues[index],
        time: multiObservable.time,
      };
      splitObservables.push(subObservable);
    }
    return splitObservables;
  };

  // Submit alert create object to API to create an alert
  const submitAlert = async (observables) => {
    const alert = {
      alertDescription: alertDescriptionFormatted.value,
      eventTime: adjustedAlertDate.value,
      name: alertDescriptionFormatted.value,
      observables: observables,
      queue: alertQueue.value,
      type: alertType.value,
    };
    try {
      await alertStore.create(alert);
    } catch (error) {
      addError(`alert ${alert.name}`, error);
    }
  };

  // create a single alert that contains all observables currently in the form
  const submitSingleAlert = async () => {
    if (!errors.value.length && observables.value.length) {
      addingObservables.value = true;
      let _observables = expandObservablesList();

      alertCreateLoading.value = true;
      await submitAlert(_observables.map(generateSubmissionObservable));
      alertCreateLoading.value = false;
      addingObservables.value = false;

      if (errors.value.length) {
        showContinueButton.value = true;
      } else {
        routeToNewAlert();
      }
    }
  };

  // create a single alert for each observable currently in the form
  const submitMultipleAlerts = async () => {
    alertCreateLoading.value = true;

    const _observables = expandObservablesList();
    for (const obs_index in _observables) {
      const current_observable = _observables[obs_index];

      // Update the alert name with observable value to easily from manage alerts page
      alertDescriptionAppendString.value = ` ${current_observable.value}`;

      await submitAlert([generateSubmissionObservable(current_observable)]);

      if (errors.value.length) {
        // If first alert can't be created, bail trying a bunch of times
        return;
      }
    }

    alertCreateLoading.value = false;
    // Routes you to latest alert
    routeToNewAlert();
  };

  const toggleMultiObservable = (index) => {
    observables.value[index].multiAdd = !observables.value[index].multiAdd;
  };
</script>