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
                  :options="alertTypes"
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
                  :options="alertQueues"
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
                  icon="pi pi-plus"
                  class="p-button-rounded inputfield"
                  @click="addFormObservable"
                />
              </div>
            </div>
            <div
              v-for="(observable, index) in observables"
              :key="observable.index"
              class="p-col-12"
            >
              <div class="formgrid grid">
                <div class="field col-2 px-1">
                  <Calendar
                    id="observable-time"
                    v-model="observables[index].time"
                    placeholder="No time selected"
                    class="inputfield w-full"
                    :show-time="true"
                    :show-seconds="true"
                  />
                </div>
                <div class="field col-2 px-1">
                  <Dropdown
                    id="observable-type"
                    v-model="observables[index].type"
                    class="inputfield w-full"
                    option-label="value"
                    option-value="value"
                    :options="observableTypes"
                  />
                </div>
                <div class="field col-3 px-1">
                  <FileUpload
                    v-if="observables[index].type == 'file'"
                    mode="basic"
                    class="inputfield w-full"
                  ></FileUpload>
                  <InputText
                    v-else
                    id="observable-value"
                    v-model="observables[index].value"
                    placeholder="Enter a value"
                    class="inputfield w-full"
                    type="text"
                  ></InputText>
                </div>
                <div class="field col-3 px-1">
                  <MultiSelect
                    id="observable-directives"
                    v-model="observables[index].directives"
                    placeholder="No directives selected"
                    class="inputfield w-full"
                    :options="directives"
                  />
                </div>
                <div class="field col-1">
                  <Button
                    icon="pi pi-times"
                    class="inputfield"
                    @click="deleteFormObservable(index)"
                  />
                </div>
                <div class="field col-1">
                  <Button
                    v-if="isLastObservable(index)"
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
    <Button
      label="Analyze!"
      :loading="alertCreateLoading"
      :disabled="showContinueButton"
      class="p-button-lg"
      @click="submitAlertAndObservables"
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

<script>
  import { mapActions, mapGetters } from "vuex";

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

  import moment from "moment-timezone";

  import ObservableInstance from "@/services/api/observableInstance";

  export default {
    name: "AnalyzeAlertForm",
    components: {
      Button,
      Calendar,
      Card,
      Dropdown,
      Fieldset,
      FileUpload,
      InputText,
      Message,
      MultiSelect,
      TabPanel,
      TabView,
    },
    data() {
      return {
        addingObservables: false,
        alertCreateLoading: false,
        alertDate: null,
        alertDescription: null,
        alertQueue: null,
        alertType: null,
        errors: [],
        observables: [],
        showContinueButton: false,
        timezone: null,
        timezones: moment.tz.names(),
      };
    },
    computed: {
      adjustedAlertDate() {
        return this.adjustForTimezone(this.alertDate, this.timezone);
      },
      observablesListEmpty() {
        return !this.observables.length;
      },
      lastObservableIndex() {
        return this.observables.length - 1;
      },
      ...mapGetters({
        openAlert: "alerts/openAlert",
        directives: "nodeDirective/allItems",
        alertTypes: "alertType/allItems",
        alertQueues: "alertQueue/allItems",
        observableTypes: "observableType/allItems",
      }),
    },
    created() {
      this.initData();
      this.initExternalData();
    },
    methods: {
      ...mapActions({
        createAlert: "alerts/createAlert",
        getAllAlertQueue: "alertQueue/getAll",
        getAllAlertType: "alertType/getAll",
        getAllNodeDirective: "nodeDirective/getAll",
        getAllObservableType: "observableType/getAll",
      }),
      adjustForTimezone(datetime, timezone) {
        return moment(datetime).tz(timezone).format();
      },
      initData() {
        this.alertDate = new Date();
        this.alertType = "manual";
        this.alertQueue = "default";
        this.errors = [];
        this.timezone = moment.tz.guess();
        this.observables = [
          {
            time: null,
            type: "file",
            value: null,
            directives: [],
          },
        ];
      },
      async initExternalData() {
        await this.getAllAlertQueue();
        await this.getAllAlertType();
        await this.getAllNodeDirective();
        await this.getAllObservableType();
      },
      async submitAlertAndObservables() {
        this.alertCreateLoading = true;
        await this.submitAlert();
        this.alertCreateLoading = false;

        if (this.errors.length) {
          return;
        }

        if (this.observables.length) {
          this.addingObservables = true;
          await this.submitObservables();
          this.addingObservables = false;
        }

        if (this.errors.length) {
          this.showContinueButton = true;
        } else {
          this.routeToNewAlert();
        }
      },
      async submitAlert() {
        const alert = {
          alertDescription: this.alertDescription,
          eventTime: this.adjustedAlertDate,
          name: this.alertDescription,
          queue: this.alertQueue,
          type: this.alertType,
        };
        try {
          await this.createAlert(alert);
        } catch (error) {
          this.addError(`alert ${alert.name}`, error);
        }
      },
      async submitObservables() {
        let observables = [];
        for (const obs_index in this.observables) {
          const observable = {
            alertUuid: this.openAlert.uuid,
            parentAnalysisUuid: this.openAlert.analysis.uuid,
            type: this.observables[obs_index].type,
            value: this.observables[obs_index].value,
          };
          if (this.observables[obs_index].time) {
            observable["time"] = this.adjustForTimezone(
              this.observables[obs_index].time,
              this.timezone,
            );
          }
          observables.push(observable);
        }

        try {
          await ObservableInstance.create(observables, false);
        } catch (error) {
          this.addError(`at least one observable`, error);
        }
      },
      addFormObservable() {
        this.observables.push({
          time: null,
          type: "file",
          value: null,
          directives: [],
        });
      },
      deleteFormObservable(index) {
        this.observables.splice(index, 1);
      },
      isLastObservable(index) {
        return index == this.lastObservableIndex;
      },
      routeToNewAlert() {
        this.$router.push({ path: `/alert/${this.openAlert.uuid}` });
      },
      addError(object, error) {
        let responseError = null;
        if (error.response) {
          responseError = JSON.stringify(error.response.data);
        }
        this.errors.push({
          content: `Could not create ${object}: ${error} ${responseError}`,
        });
      },
      handleError(index) {
        this.errors.splice(index, 1);
      },
    },
  };
</script>
