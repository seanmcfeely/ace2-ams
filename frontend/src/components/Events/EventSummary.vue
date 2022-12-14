<!-- EventSummary.vue -->
<!-- "Event Summary" section on Event Details page -->

<template>
  <!-- Event Timeline -->
  <div id="event-summary-timeline">
    <Timeline :value="timelineEvents" layout="horizontal" align="bottom">
      <template #marker="slotProps">
        <span class="custom-marker" data-cy="event-summary-timeline-icon">
          <i :class="slotProps.item.icon"></i>
        </span>
      </template>
      <template #opposite="slotProps">
        <small
          class="p-text-secondary"
          data-cy="event-summary-timeline-datetime"
          >{{ formatDatetime(slotProps.item.datetime) }}</small
        >
      </template>
      <template #content="slotProps">
        <span data-cy="event-summary-timeline-label">{{
          slotProps.item.label
        }}</span>
      </template>
    </Timeline>
  </div>
  <!-- Event Details Table -->
  <div id="event-summary-table">
    <DataTable :value="eventTableData" :resizable-columns="true">
      <template #empty> Event data not found. </template>
      <!-- TABLE TOOLBAR-->
      <template #header>
        <Toolbar style="border: none">
          <template #start>
            <!-- COLUMN SELECT -->
            <MultiSelect
              :model-value="selectedColumns"
              :options="columnOptions"
              data-cy="table-column-select"
              option-label="header"
              placeholder="Select Columns"
              @update:model-value="onColumnToggle"
            />
          </template>
          <template #end>
            <Button
              data-cy="reset-table-button"
              icon="pi pi-refresh"
              class="p-button-rounded p-m-1"
              @click="resetColumns()"
            />
          </template>
        </Toolbar>
      </template>

      <!-- DATA COLUMNS -->
      <Column
        v-for="(col, index) of selectedColumns"
        :key="col.field + '_' + index"
        :field="col.field"
        :header="col.header"
      >
        <!-- DATA COLUMN CELL BODIES-->
        <template #body="{ data, field }">
          <EventTableCell
            :data="data"
            :field="field"
            :show-tags="false"
          ></EventTableCell>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script lang="ts">
  export default {
    inheritAttrs: false,
  };
</script>

<script setup lang="ts">
  import { ref, inject, computed, onMounted } from "vue";

  import { useEventStore } from "@/stores/event";
  import Button from "primevue/button";
  import Column from "primevue/column";
  import DataTable from "primevue/datatable";
  import EventTableCell from "./EventTableCell.vue";
  import MultiSelect from "primevue/multiselect";
  import Toolbar from "primevue/toolbar";
  import Timeline from "primevue/timeline";

  import { parseEventSummary } from "@/stores/eventTable";
  import { prettyPrintDateTime } from "@/etc/helpers";

  interface eventTimeEntry {
    label: string;
    datetime: string | Date | null;
    icon: string;
  }

  interface column {
    default: boolean;
    required: boolean;
    field: string;
    header: string;
  }

  const config = inject("config") as any;

  const eventStore = useEventStore();

  const eventTableData = ref(
    eventStore.open ? [parseEventSummary(eventStore.open)] : [],
  );
  const eventTimes = ref<eventTimeEntry[]>([]);
  const columns = ref<column[]>([]);
  const columnOptions = ref<column[]>([]);
  const selectedColumns = ref<column[]>([]);

  onMounted(() => {
    if (eventStore.open) {
      initData();
      resetColumns();
    }
  });

  const timelineEvents = computed(() => {
    // Eventually, more things will be added to this array and sorted by time
    return [...eventTimes.value];
  });

  const formatDatetime = (datetime: string) => {
    if (datetime == "TBD") {
      return datetime;
    }

    return prettyPrintDateTime(datetime);
  };

  const onColumnToggle = (val: any) => {
    // Toggles selected columns to display
    // This method required/provided by Primevue 'ColToggle' docs
    selectedColumns.value = columns.value.filter((col) => val.includes(col));
  };

  const initData = () => {
    columns.value =
      config.events.eventQueueColumnMappings[eventStore.open.queue.value];
    columnOptions.value = columns.value.filter((col) => !col.required);
    eventTimes.value = [
      {
        label: "Event",
        datetime:
          eventStore.open.eventTime || eventStore.open.autoEventTime || "TBD",
        icon: "pi pi-map-marker",
      },
      {
        label: "Alert",
        datetime:
          eventStore.open.alertTime || eventStore.open.autoAlertTime || "TBD",
        icon: "pi pi-exclamation-triangle",
      },
      {
        label: "Ownership",
        datetime:
          eventStore.open.ownershipTime ||
          eventStore.open.autoOwnershipTime ||
          "TBD",
        icon: "pi pi-user-plus",
      },
      {
        label: "Disposition",
        datetime:
          eventStore.open.dispositionTime ||
          eventStore.open.autoDispositionTime ||
          "TBD",
        icon: "pi pi-flag",
      },
      {
        label: "Contain",
        datetime: eventStore.open.containTime || "TBD",
        icon: "pi pi-shield",
      },
      {
        label: "Remediation",
        datetime: eventStore.open.remediationTime || "TBD",
        icon: "pi pi-check-circle",
      },
    ];
  };

  const resetColumns = () => {
    selectedColumns.value = columns.value.filter((col) => col.default);
  };
</script>
