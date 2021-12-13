/* eslint-disable vue/attribute-hyphenation */
<!-- TheAlertsTable.vue -->
<!-- The table where all currently filtered alerts are displayed, selected to take action, or link to an individual alert page -->

<template>
  <DataTable
    ref="dt"
    v-model:expandedRows="expandedRows"
    v-model:filters="alertTableFilter"
    v-model:selection="selectedRows"
    :value="visibleQueriedAlertSummaries"
    :global-filter-fields="selectedColumns.field"
    :resizable-columns="true"
    :sort-order="-1"
    :loading="isLoading"
    column-resize-mode="expand"
    data-key="uuid"
    removable-sort
    responsive-layout="scroll"
    :sort-field="sortField"
    @sort="sort"
    @rowSelect="alertSelect($event.data.uuid)"
    @rowUnselect="alertUnselect($event.data.uuid)"
    @rowSelect-all="alertSelectAll(visibleQueriedAlertsUuids)"
    @rowUnselect-all="alertUnselectAll()"
  >
    <!--        ALERT TABLE TOOLBAR-->
    <template #header>
      <Toolbar style="border: none">
        <template #left>
          <MultiSelect
            :model-value="selectedColumns"
            :options="columns"
            option-label="header"
            placeholder="Select Columns"
            @update:modelValue="onColumnToggle"
          />
        </template>
        <template #right>
          <span class="p-input-icon-left p-m-1">
            <i class="pi pi-search" />
            <InputText
              v-model="alertTableFilter['global'].value"
              placeholder="Search in table"
            />
          </span>
          <!--            CLEAR TABLE FILTERS -->
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-m-1"
            @click="reset()"
          />
          <!--            EXPORT TABLE -->
          <Button
            class="p-button-rounded p-m-1"
            icon="pi pi-download"
            @click="exportCSV($event)"
          />
        </template>
      </Toolbar>
    </template>

    <!-- DROPDOWN COLUMN-->
    <Column id="alert-expand" :expander="true" header-style="width: 3rem" />

    <!-- CHECKBOX COLUMN -->
    <!-- It's annoying, but the PrimeVue DataTable selectionMode attribute works when camelCase -->
    <Column
      id="alert-select"
      header-style="width: 3em"
      selectionMode="multiple"
    />

    <!-- DATA COLUMN -->
    <Column
      v-for="(col, index) of selectedColumns"
      :key="col.field + '_' + index"
      :field="col.field"
      :header="col.header"
      :sortable="true"
    >
      <!-- DATA COLUMN BODY-->
      <template #body="{ data }">
        <!-- NAME COLUMN - INCL. TAGS AND TODO: ALERT ICONS-->
        <div v-if="col.field === 'name'">
          <span class="p-m-1">
            <router-link :to="getAlertLink(data.uuid)">{{
              data.name
            }}</router-link></span
          >
          <br />
          <span>
            <Tag v-for="tag in data.tags" :key="tag" class="p-mr-2" rounded>{{
              tag
            }}</Tag>
          </span>
        </div>
        <span v-else-if="col.field.includes('Time')">
          {{ formatDateTime(data[col.field]) }}</span
        >
        <span v-else> {{ data[col.field] }}</span>
      </template>
    </Column>

    <!--      ALERT ROW DROPDOWN -->
    <template #expansion="slotProps">
      <h5>Observables:</h5>
      <ul>
        <li v-for="obs of slotProps.data.observables" :key="obs.value">
          {{ obs }}
        </li>
      </ul>
    </template>
  </DataTable>
  <Paginator
    :rows="numRows"
    :rows-per-page-options="[5, 10, 50, 100]"
    :total-records="totalAlerts"
    template="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
    current-page-report-template="Showing {first} to {last} of {totalRecords}"
    @page="
      onPage($event);
      alertUnselectAll();
    "
  ></Paginator>
</template>

<script>
  import { mapState, mapActions } from "pinia";

  import { camelToSnakeCase } from "@/etc/helpers";
  import { useAlertTableStore } from "@/stores/alertTable";
  import { useFilterStore } from "@/stores/filter";
  import { useSelectedAlertStore } from "@/stores/selectedAlert";

  import Button from "primevue/button";
  import Column from "primevue/column";
  import DataTable from "primevue/datatable";
  import { FilterMatchMode } from "primevue/api";
  import InputText from "primevue/inputtext";
  import MultiSelect from "primevue/multiselect";
  import Tag from "primevue/tag";
  import Toolbar from "primevue/toolbar";
  import Paginator from "primevue/paginator";

  export default {
    name: "TheAlertsTable",
    components: {
      Button,
      Column,
      DataTable,
      InputText,
      MultiSelect,
      Tag,
      Toolbar,
      Paginator,
    },

    data() {
      return {
        alertTableFilter: null,

        columns: [
          { field: "dispositionTime", header: "Dispositioned Time" },
          { field: "insertTime", header: "Insert Time" },
          { field: "eventTime", header: "Event Time" },
          { field: "name", header: "Name" },
          { field: "owner", header: "Owner" },
          { field: "disposition", header: "Disposition" },
          { field: "dispositionUser", header: "Dispositioned By" },
          { field: "queue", header: "Queue" },
          { field: "type", header: "Type" },
        ],

        defaultColumns: ["eventTime", "name", "owner", "disposition"],

        expandedRows: [],
        error: null,
        isLoading: false,
        selectedColumns: null,
        selectedRows: null,
        sortField: "eventTime",
        sortOrder: "desc",
        numRows: 10,
        page: 0,
      };
    },

    computed: {
      ...mapState(useFilterStore, {
        filters: "alerts",
      }),

      ...mapState(useAlertTableStore, {
        totalAlerts: (store) => store.totalAlerts,
        visibleQueriedAlertSummaries: "visibleQueriedAlertSummaries",
        visibleQueriedAlertsUuids: "visibleQueriedAlertsUuids",
      }),

      ...mapState(useSelectedAlertStore, {
        selectedAlerts: (store) => store.selected,
      }),

      sortFilter() {
        return this.sortField
          ? `${camelToSnakeCase(this.sortField)}|${this.sortOrder}`
          : null;
      },
      pageOptions() {
        return {
          limit: this.numRows,
          offset: this.numRows * this.page,
        };
      },
    },

    watch: {
      filters: {
        deep: true,
        handler: function () {
          this.loadAlerts();
        },
      },
    },

    async created() {
      this.initAlertTable();
      await this.loadAlerts(this.pageOptions);
    },

    methods: {
      ...mapActions(useAlertTableStore, ["readPage"]),

      ...mapActions(useSelectedAlertStore, {
        alertSelect: "select",
        alertSelectAll: "selectAll",
        alertUnselect: "unselect",
        alertUnselectAll: "unselectAll",
      }),

      reset() {
        // Sets the alert table selected columns, keyword search, and sort back to default
        this.initAlertTable();
        this.sort({ sortField: "eventTime", sortOrder: "-1" });
      },

      initAlertTable() {
        // Initializes alert filter (the keyword search)
        this.alertTableFilter = {
          global: { value: null, matchMode: FilterMatchMode.CONTAINS },
        };
        this.selectedColumns = [];
        this.selectedColumns = this.columns.filter((column) => {
          return this.defaultColumns.includes(column.field);
        });
        this.error = null;
      },

      onColumnToggle(value) {
        // Toggles selected columns to display
        // This method required/provided by Primevue 'ColToggle' docs
        this.selectedColumns = this.columns.filter((col) =>
          value.includes(col),
        );
      },

      exportCSV() {
        // Exports currently filtered alerts to CSV
        this.$refs.dt.exportCSV();
      },

      async sort(event) {
        if (event.sortField) {
          this.sortField = event.sortField;
          this.sortOrder = event.sortOrder > 0 ? "asc" : "desc";
          await this.loadAlerts();
        } else {
          this.sortField = null;
          this.sortOrder = null;
        }
      },

      async onPage(event) {
        this.selectedRows = [];
        this.numRows = event.rows;
        this.page = event.page;
        await this.loadAlerts();
      },

      async loadAlerts() {
        this.isLoading = true;
        try {
          await this.readPage({
            sort: this.sortFilter,
            ...this.pageOptions,
            ...this.filters,
          });
        } catch (error) {
          this.error = error.message || "Something went wrong!";
        }
        this.isLoading = false;
      },

      getAlertLink(uuid) {
        return "/alert/" + uuid;
      },

      formatDateTime(dateTime) {
        if (dateTime) {
          const d = new Date(dateTime);
          return d.toLocaleString("en-US");
        }

        return "None";
      },
    },
  };
</script>