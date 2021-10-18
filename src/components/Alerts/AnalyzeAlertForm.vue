<template>
  <div>
    <TabView>
      <TabPanel key="basic" header="Basic">
        <br />
        <span class="p-float-label p-field">
          <InputText
            id="description"
            v-model="alertDescription"
            type="text"
          ></InputText>
          <label for="description">Alert Description</label>
        </span>
        <br />
        <Fieldset legend="Advanced" :toggleable="true" :collapsed="true">
          <Calendar
            id="alert-date"
            v-model="alertDate"
            :show-time="true"
            :show-seconds="true"
          />
          <Dropdown id="timezone" v-model="timezone" :options="timezones" />
          <Dropdown
            id="type"
            v-model="alertType"
            :options="alertTypes"
            option-label="value"
            option-value="value"
          />
          <Dropdown
            id="queue"
            v-model="alertQueue"
            :options="alertQueues"
            option-label="value"
            option-value="value"
          />
        </Fieldset>
        <p>Observables</p>
        <div id="observables-list" class="p-grid">
          <div
            v-for="(observable, index) in observables"
            :key="observable.index"
            class="p-col-12"
          >
            <Calendar
              id="observable-time"
              v-model="observables[index].time"
              :show-time="true"
              :show-seconds="true"
            />
            <Dropdown
              id="observable-type"
              v-model="observables[index].type"
              option-label="value"
              option-value="value"
              :options="observableTypes"
            />

            <InputText
              id="observable-value"
              v-model="observables[index].value"
              type="text"
            ></InputText>

            <MultiSelect
              id="observable-directives"
              v-model="observables[index].directives"
              :options="directives"
            />

            <Button
              v-if="observable.index != 0"
              icon="pi pi-times"
              @click="deleteFormObservable(index)"
            />
          </div>
        </div>
        <Button icon="pi pi-plus" @click="addFormObservable" />
        <br />
      </TabPanel>
    </TabView>
    <Button
      label="Analyze!"
      :loading="loadingAlertCreation"
      @click="createAlert()"
    />
  </div>
</template>

<script>
  import { mapGetters } from "vuex";

  import Dropdown from "primevue/dropdown";

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
      Dropdown,
      Button,
      Fieldset,
      InputText,
      TabPanel,
      TabView,
      MultiSelect,
    },
    data() {
      return {
        alertDate: null,
        timezone: null,
        timezones: moment.tz.names(),
        alertType: null,
        alertDescription: null,
        alertQueue: null,
        observables: [],
        loadingAlertCreation: false,
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
        // this.alertDate = moment(new Date().format("M/M/DD/YYYY HH:mm:ss")).utc();
        this.timezone = "UTC";
        this.alertType = "Manual";
        this.alertDescription = "Test Alert!";
        this.alertQueue = "Default";
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
      printObservables() {
        console.log(this.observables);
      },
      async createAlert() {
        const alert = {
          alertDescription: this.alertDescription,
          eventTime: this.alertDate,
          instructions: "NO instructions",
          name: this.alertDescription,
          owner: "analyst",
          queue: this.alertQueue,
          tool: null,
          toolInstance: null,
          type: this.alertType,
        };

        this.loadingAlertCreation = true;
        await this.$store.dispatch("alerts/createAlert", alert);
        await this.addObservables();
        this.$router.push({ path: `/alert/${this.openAlert.uuid}` });
      },
      async addObservables() {
        for (const obs_index in this.observables) {
          const observable = {
            alertUuid: this.openAlert.uuid,
            parentAnalysisUuid: this.openAlert.analysis.uuid,
            type: this.observables[obs_index].type,
            value: this.observables[obs_index].value,
          };
          await ObservableInstance.create(observable);
        }
      },
    },
  };
</script>
