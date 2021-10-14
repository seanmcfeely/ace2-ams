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
          <Dropdown id="type" v-model="alertType" :options="alertTypes" />
          <Dropdown id="queue" v-model="alertQueue" :options="alertQueues" />
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
              :v-model="observables[index].time"
              :show-time="true"
              :show-seconds="true"
            />
            <Dropdown
              id="observable-type"
              v-model="observables[index].type"
              :options="observableTypes"
            />

            <InputText
              id="observable-value"
              v-model="observables[index].value"
              type="text"
            ></InputText>

            <Dropdown
              id="observable-directives"
              v-model="observables[index].directive"
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
    <Button label="Analyze!" @click="save" />
  </div>
</template>

<script>
  import { mapGetters } from "vuex";

  import Dropdown from "primevue/dropdown";

  import FileUpload from "primevue/fileupload";

  import Calendar from "primevue/calendar";
  import InputText from "primevue/inputtext";

  import Button from "primevue/button";
  import Fieldset from "primevue/fieldset";

  import TabPanel from "primevue/tabpanel";
  import TabView from "primevue/tabview";

  import moment from "moment-timezone";

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
        directives: ["sandbox"],
        alertTypes: ["manual"],
        alertQueues: ["default"],
        observableTypes: ["file", "ipv4"],
      };
    },
    computed: {
      lastObservableIndex() {
        return this.observables.length - 1;
      },
      ...mapGetters({
        // directives: "nodeDirectives/nodeDirectives",
        // alertTypes: "alertType/alertTypes",
        // alertQueues: "alertQueue/alertQueues",
        // observableTypes: "observableType/observableTypes",
      }),
    },
    created() {
      this.init();
      this.loadInitialData();
    },
    methods: {
      init() {
        this.observables.push({
          index: 0,
          time: new Date(),
          type: "file",
          directives: ["sandbox"],
        });
        this.observables.push({
          index: 1,
          time: new Date(),
          type: "ipv4",
          directives: [],
        });
        this.alertDate = new Date().toUTCString();
        this.timezone = "UTC";
        this.alertType = "Manual";
        this.alertDescription = "Test Alert!";
        this.alertQueue = "Default";
      },
      async loadInitialData() {
        await this.$store.dispatch("alertQueue/getAllAlertQueues");
        await this.$store.dispatch("alertType/getAllAlertTypes");
        await this.$store.dispatch("nodeDirective/getAllNodeDirectives");
        await this.$store.dispatch("observableType/getAllObservableTypes");
      },
      addFormObservable() {
        this.observables.push({
          time: new Date(),
          type: "file",
          directives: ["sandbox"],
        });
      },
      deleteFormObservable(index) {
        this.observables.splice(index, 1);
      },
    },
  };
</script>
