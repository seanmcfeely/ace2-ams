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
                  <InputText
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
                    class="inputfield w-full"
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
      class="p-button-lg"
      @click="createAlert()"
    />
  </div>
  <Message v-if="error" severity="error" @close="handleError">{{
    error
  }}</Message>
</template>

<script>
  import { mapGetters } from "vuex";

  import Card from "primevue/card";
  import Dropdown from "primevue/dropdown";

  import Message from "primevue/message";

  import MultiSelect from "primevue/multiselect";

  import Calendar from "primevue/calendar";
  import InputText from "primevue/inputtext";

  import Button from "primevue/button";
  import Fieldset from "primevue/fieldset";

  import TabPanel from "primevue/tabpanel";
  import TabView from "primevue/tabview";

  import moment from "moment-timezone";

  import ObservableInstance from "@/services/api/observableInstance";

  export default {
    name: "AnalyzeAlertForm",
    components: {
      Calendar,
      Card,
      Dropdown,
      Button,
      Fieldset,
      InputText,
      TabPanel,
      TabView,
      Message,
      MultiSelect,
    },
    data() {
      return {
        alertCreateLoading: false,
        alertDate: null,
        alertDescription: null,
        alertType: null,
        alertQueue: null,
        error: null,
        observables: [],
        timezone: null,
        timezones: moment.tz.names(),
      };
    },
    computed: {
      lastObservableIndex() {
        return this.observables.length - 1;
      },
      ...mapGetters({
        openAlert: "alerts/openAlert",
        directives: "nodeDirectives/nodeDirectives",
        alertTypes: "alertType/alertTypes",
        alertQueues: "alertQueue/alertQueues",
        observableTypes: "observableType/observableTypes",
      }),
    },
    created() {
      this.init();
      this.loadInitialData();
    },
    methods: {
      init() {
        this.observables.push({
          time: null,
          type: "ipv4",
          value: null,
          directives: [],
        });
        this.alertDate = new Date();
        this.timezone = moment.tz.guess();
        this.alertType = "manual";
        this.alertQueue = "default";
      },
      async loadInitialData() {
        await this.$store.dispatch("alertQueue/getAllAlertQueues");
        await this.$store.dispatch("alertType/getAllAlertTypes");
        await this.$store.dispatch("nodeDirectives/getAllNodeDirectives");
        await this.$store.dispatch("observableType/getAllObservableTypes");
      },
      addFormObservable() {
        this.observables.push({
          time: null,
          type: "ipv4",
          value: null,
          directives: [],
        });
      },
      deleteFormObservable(index) {
        this.observables.splice(index, 1);
      },
      handleError() {
        this.error = null;
      },
      isLastObservable(index) {
        return index == this.lastObservableIndex;
      },
      async createAlert() {
        const alert = {
          alertDescription: this.alertDescription,
          eventTime: this.alertDate,
          name: this.alertDescription,
          queue: this.alertQueue,
          type: this.alertType,
        };

        this.alertCreateLoading = true;
        try {
          await this.$store.dispatch("alerts/createAlert", alert);
          await this.addObservables();
          this.$router.push({ path: `/alert/${this.openAlert.uuid}` });
        } catch (error) {
          this.error = `Could not create alert: ${error} ${JSON.stringify(
            error.response.data.detail,
          )}`;
          this.alertCreateLoading = false;
        }
      },
      async addObservables() {
        for (const obs_index in this.observables) {
          const observable = {
            alertUuid: this.openAlert.uuid,
            parentAnalysisUuid: this.openAlert.analysis.uuid,
            type: this.observables[obs_index].type,
            value: this.observables[obs_index].value,
          };
          await ObservableInstance.create(observable, false);
        }
      },
    },
  };
</script>
