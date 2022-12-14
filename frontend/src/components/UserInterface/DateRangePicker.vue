<template>
  <div>
    <!--      DATE PICKER OPTIONS  -->
    <Button
      icon="pi pi-calendar"
      data-cy="date-range-picker-options-button"
      @click="toggleOptionsMenu"
    />
    <OverlayPanel ref="op">
      <div class="p-d-flex">
        <Dropdown
          v-model="currentRangeFilter"
          :options="rangeFilterOptions"
          @change="toggleOptionsMenu"
        />
      </div>
      <div class="p-d-flex p-flex-column p-jc-center">
        <div class="p-mb-2">
          <Button label="Today" class="p-button-sm" @click="setRange(TODAY)" />
        </div>
        <div class="p-mb-2">
          <Button
            label="Yesterday"
            class="p-button-sm"
            @click="setRange(YESTERDAY)"
          />
        </div>
        <div class="p-mb-2">
          <Button
            label="Last 7 Days"
            class="p-button-sm"
            @click="setRange(LAST_SEVEN)"
          />
        </div>
        <div class="p-mb-2">
          <Button
            label="Last 30 Days"
            class="p-button-sm"
            @click="setRange(LAST_THIRTY)"
          />
        </div>
        <div class="p-mb-2">
          <Button
            label="Last 60 Days"
            class="p-button-sm"
            @click="setRange(LAST_SIXTY)"
          />
        </div>
        <div class="p-mb-2">
          <Button
            label="This Month"
            class="p-button-sm"
            @click="setRange(THIS_MONTH)"
          />
        </div>
        <div class="p-mb-2">
          <Button
            label="Last Month"
            class="p-button-sm"
            @click="setRange(LAST_MONTH)"
          />
        </div>
      </div>
    </OverlayPanel>
    <span style="postition: absolute">
      <UtcDatePicker
        v-model="startDate"
        v-tooltip.top="{
          value: startDateLocal,
          disabled: !startDateLocal,
          class: 'tooltip',
        }"
        data-cy="date-range-picker-start-input"
        placeholder="The beginning of time"
        @update:model-value="dateSelect($event, startFilter)"
        @update:model-value.delete="dateSelect(null)"
      ></UtcDatePicker>
      <Button
        data-cy="date-range-picker-start-clear"
        icon="pi pi-times"
        class="p-button-outlined p-button-secondary"
        @click="clearDate(startFilter)"
      />
    </span>
    <span style="postition: absolute"> to </span>
    <span style="postition: absolute">
      <UtcDatePicker
        v-model="endDate"
        v-tooltip.top="{
          value: endDateLocal,
          disabled: !endDateLocal,
          class: 'tooltip',
        }"
        data-cy="date-range-picker-end-input"
        placeholder="Now"
        @update:model-value="dateSelect($event, endFilter)"
        @update:model-value.delete="dateSelect(null)"
      ></UtcDatePicker>
      <Button
        data-cy="date-range-picker-end-clear"
        icon="pi pi-times"
        class="p-button-outlined p-button-secondary"
        @click="clearDate(endFilter)"
      />
    </span>
  </div>
</template>

<script setup lang="ts">
  import { computed, inject, ref, watch } from "vue";

  import Dropdown from "primevue/dropdown";
  import Button from "primevue/button";
  import OverlayPanel from "primevue/overlaypanel";

  import UtcDatePicker from "@/components/UserInterface/UtcDatePicker.vue";

  import { useFilterStore } from "@/stores/filter";

  interface rangeFilter {
    start: string;
    end: string;
  }

  const TODAY = "today";
  const YESTERDAY = "yesterday";
  const LAST_SEVEN = "last_seven";
  const LAST_THIRTY = "last_thirty";
  const LAST_SIXTY = "last_sixty";
  const THIS_MONTH = "this_month";
  const LAST_MONTH = "last_month";

  const filterStore = useFilterStore();

  const objectType = inject("objectType") as "alerts" | "events";
  const rangeFilters = inject("rangeFilters") as Record<string, rangeFilter>;

  const currentRangeFilter = ref(Object.keys(rangeFilters)[0]);
  const op = ref();

  const filters = computed(() => {
    return filterStore.$state[objectType];
  });

  const startFilter = computed(() => {
    return rangeFilters[currentRangeFilter.value].start;
  });

  const endFilter = computed(() => {
    return rangeFilters[currentRangeFilter.value].end;
  });

  const startDate = computed(() => {
    return filters.value[startFilter.value] &&
      filters.value[startFilter.value].included.length
      ? filters.value[startFilter.value].included[0]
      : null;
  });

  const endDate = computed(() => {
    return filters.value[endFilter.value] &&
      filters.value[endFilter.value].included.length
      ? filters.value[endFilter.value].included[0]
      : null;
  });

  const startDateLocal = computed(() => {
    return startDate.value
      ? startDate.value.toLocaleString("en-US", { timeZoneName: "short" })
      : null;
  });

  const endDateLocal = computed(() => {
    return endDate.value
      ? endDate.value.toLocaleString("en-US", { timeZoneName: "short" })
      : null;
  });

  const rangeFilterOptions = computed(() => {
    return Object.keys(rangeFilters);
  });

  watch(currentRangeFilter, (_newValue, oldValue) => {
    clearDate(rangeFilters[oldValue].start);
    clearDate(rangeFilters[oldValue].end);
  });

  const dateSelect = (date: Date | null, filterName?: string) => {
    if (date == null) {
      return;
    }

    if (filterName) {
      filterStore.unsetFilter({
        objectType: objectType,
        filterName: filterName,
      });
      filterStore.setFilter({
        objectType: objectType,
        filterName: filterName,
        filterValue: date,
        isIncluded: true,
      });
    }
  };

  const clearDate = (filterName: string) => {
    filterStore.unsetFilter({
      objectType: objectType,
      filterName: filterName,
    });
  };

  const setRange = (rangeType: string) => {
    const today = new Date();
    let startDate = null;
    let endDate = null;
    let pastDate = null;
    switch (rangeType) {
      case TODAY:
        startDate = new Date();
        endDate = new Date();
        break;
      case YESTERDAY:
        pastDate = today.getDate() - 1;
        startDate = new Date(today.setDate(pastDate));
        endDate = new Date(today.setDate(pastDate));
        break;
      case LAST_SEVEN:
        pastDate = today.getDate() - 7;
        startDate = new Date(today.setDate(pastDate));
        endDate = new Date();
        break;
      case LAST_THIRTY:
        pastDate = today.getDate() - 30;
        startDate = new Date(today.setDate(pastDate));
        endDate = new Date();
        break;
      case LAST_SIXTY:
        pastDate = today.getDate() - 60;
        startDate = new Date(today.setDate(pastDate));
        endDate = new Date();
        break;
      case THIS_MONTH:
        pastDate = today.getMonth();
        startDate = new Date(today.setMonth(pastDate));
        startDate.setDate(1);
        endDate = new Date();
        break;
      case LAST_MONTH:
        pastDate = today.getMonth() - 1;
        today.setDate(1); // Need to reset day of the month, otherwise date will be wonky if prev. month has less days
        startDate = new Date(today.setMonth(pastDate));
        endDate = new Date(today.setMonth(pastDate + 1));
        startDate.setDate(1);
        endDate.setDate(0); // 0 will set the date to the last day of the previous month
        break;
      default:
        break;
    }
    // Set start and end date times to capture entierty of each day
    if (startDate && endDate) {
      startDate.setUTCHours(0, 0, 0, 0);
      endDate.setUTCHours(23, 59, 59, 0);
      dateSelect(startDate, startFilter.value);
      dateSelect(endDate, endFilter.value);
    }

    toggleOptionsMenu();
  };

  const toggleOptionsMenu = (event?: unknown) => {
    const e = event ? event : undefined;
    op.value.toggle(e);
  };
</script>

<style>
  .tooltip {
    position: absolute;
    z-index: 2;
  }
</style>
