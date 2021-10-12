<template>
  <div>
    <TabView>
      <TabPanel key="basic" header="Basic">
        <br />
        <span class="p-float-label p-field">
          <InputText id="description" v-model="value" type="text"></InputText>
          <label for="description">Alert Description</label>
        </span>
        <br />
        <Fieldset legend="Advanced" :toggleable="true" :collapsed="true">
          <Calendar
            id="time24"
            v-model="date8"
            :show-time="true"
            :show-seconds="true"
          />
          <Dropdown
            id="type"
            v-model="type"
            :options="alertTypes"
            option-label="type"
          />
          <InputText id="value" v-model="o_value" type="text"></InputText>
          <Dropdown
            id="queue"
            v-model="queue"
            :options="alertQueues"
            option-label="type"
          />
        </Fieldset>
        <p>Observables</p>
        <div id="observables-list">
          <div
            v-for="(observable, index) in observables"
            :key="observable.index"
          >
            <Calendar
              id="observable-time"
              :v-model="observable.time"
              :show-time="true"
              :show-seconds="true"
            />

            <Dropdown
              id="observable-type"
              v-model="observable.type"
              :options="observableTypes"
              option-label="Type"
            />

            <InputText
              id="observable-value"
              v-model="observable.value"
              type="text"
            ></InputText>

            <Dropdown
              id="observable-directives"
              v-model="observable.directive"
              :options="directives"
              option-label="Directives"
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
  import { mapState, mapGetters, mapActions } from "vuex";

  import Dropdown from "primevue/dropdown";

  import Calendar from "primevue/calendar";
  import InputText from "primevue/inputtext";

  import Button from "primevue/button";
  import Fieldset from "primevue/fieldset";

  import TabPanel from "primevue/tabpanel";
  import TabView from "primevue/tabview";

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
        alertType: null,
        alertDescription: null,
        alertQueue: null,
        observables: [],
      };
    },
    computed: {
      lastObservableIndex() {
        return this.observables.length - 1;
      },
      ...mapGetters({
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
          index: 0,
          time: null,
          type: "file",
          directives: ["sandbox"],
        });
      },
      async loadInitialData() {
        await this.$store.dispatch("alertQueue/getAllAlertQueues");
        await this.$store.dispatch("alertType/getAllAlertTypes");
        await this.$store.dispatch("nodeDirective/getAllNodeDirectives");
        await this.$store.dispatch("observableType/getAllObservableTypes");
      },
      addFormObservable() {
        this.observables.push({
          time: null,
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
