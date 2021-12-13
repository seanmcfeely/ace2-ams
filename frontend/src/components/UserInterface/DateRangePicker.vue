<template>
  <!--      DATE PICKER OPTIONS  -->
  <Button icon="pi pi-calendar" @click="toggleOptionsMenu" />
  <OverlayPanel ref="op">
    <div class="p-d-flex">
      <Dropdown v-model="currentRangeFilter" :options="rangeFilterOptions" />
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

  <!--      DATE PICKERS -->
  <DatePicker
    v-model="startDate"
    mode="dateTime"
    is24hr
    @update:model-value="dateSelect($event, startFilter)"
    @update:model-value.delete="dateSelect(null)"
  >
    <template #default="{ inputValue, inputEvents }">
      <div class="p-inputgroup">
        <InputText
          v-tooltip.top="{
            value: startDateUTC,
            disabled: !startDateUTC,
          }"
          type="text"
          :value="inputValue"
          placeholder="The beginning of time"
          v-on="inputEvents"
        />
        <Button
          icon="pi pi-times"
          class="p-button-outlined p-button-secondary"
          @click="clearDate(startFilter)"
        />
      </div>
    </template>
  </DatePicker>
  <span> to </span>
  <DatePicker
    v-model="endDate"
    mode="dateTime"
    is24hr
    @update:model-value="dateSelect($event, endFilter)"
    @update:model-value.delete="dateSelect(null)"
  >
    <template #default="{ inputValue, inputEvents }">
      <div class="p-inputgroup">
        <InputText
          v-tooltip.top="{
            value: endDateUTC,
            disabled: !endDateUTC,
          }"
          type="text"
          :value="inputValue"
          placeholder="Now"
          v-on="inputEvents"
        />
        <Button
          icon="pi pi-times"
          class="p-button-outlined p-button-secondary"
          @click="clearDate(endFilter)"
        />
      </div>
    </template>
  </DatePicker>
</template>

<script setup>
  import { computed, inject, ref, watch } from "vue";

  import Dropdown from "primevue/dropdown";
  import Button from "primevue/button";
  import OverlayPanel from "primevue/overlaypanel";
  import InputText from "primevue/inputtext";
  import { DatePicker } from "v-calendar";

  import { useFilterStore } from "@/stores/filter";

  const TODAY = "today";
  const YESTERDAY = "yesterday";
  const LAST_SEVEN = "last_seven";
  const LAST_THIRTY = "last_thirty";
  const LAST_SIXTY = "last_sixty";
  const THIS_MONTH = "this_month";
  const LAST_MONTH = "last_month";

  const filterStore = useFilterStore();

  const filterType = inject("filterType");
  const rangeFilters = inject("rangeFilters");

  const currentRangeFilter = ref(Object.keys(rangeFilters)[0]);
  const op = ref(null);

  const filters = computed(() => {
    return filterStore.$state[filterType];
  });

  const startFilter = computed(() => {
    return rangeFilters[currentRangeFilter.value].start;
  });

  const endFilter = computed(() => {
    return rangeFilters[currentRangeFilter.value].end;
  });

  const startDate = computed(() => {
    return filters.value[startFilter.value]
      ? filters.value[startFilter.value]
      : null;
  });

  const endDate = computed(() => {
    return filters.value[endFilter.value]
      ? filters.value[endFilter.value]
      : null;
  });

  const startDateUTC = computed(() => {
    return startDate.value ? startDate.value.toUTCString() : null;
  });

  const endDateUTC = computed(() => {
    return endDate.value ? endDate.value.toUTCString() : null;
  });

  const rangeFilterOptions = computed(() => {
    return Object.keys(rangeFilters);
  });

  watch(currentRangeFilter, (_newValue, oldValue) => {
    clearDate(rangeFilters[oldValue].start);
    clearDate(rangeFilters[oldValue].end);
  });

  const dateSelect = (date, filterName) => {
    if (date == null) {
      return;
    }

    filterStore.setFilter({
      filterType: filterType,
      filterName: filterName,
      filterValue: date,
    });
  };

  const clearDate = (filterName) => {
    filterStore.unsetFilter({
      filterType: filterType,
      filterName: filterName,
    });
  };

  const setRange = (rangeType) => {
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
        startDate = new Date(today.setMonth(pastDate));
        endDate = new Date(today.setMonth(pastDate + 1));
        startDate.setDate(1);
        endDate.setDate(0); // 0 will set the date to the last day of the previous month
        break;
      default:
        break;
    }
    // Set start and end date times to capture entierty of each day
    startDate.setHours(0, 0, 0, 0);
    endDate.setHours(23, 59, 59, 0);
    dateSelect(startDate, startFilter.value);
    dateSelect(endDate, endFilter.value);
  };

  const toggleOptionsMenu = (event) => {
    op.value.toggle(event);
  };
</script>