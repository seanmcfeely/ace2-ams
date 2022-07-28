<template>
  <div style="display: inline">
    <InputText
      v-model="displayUtcString"
      :placeholder="placeholder"
      :class="inputClass"
      @focus="toggle"
      @input="updateDateFromInput"
      @keydown.enter="updateModelValue"
    />
    <OverlayPanel ref="op" :style="overlayStyle">
      <Calendar
        v-model="calendarDate"
        :inline="true"
        :show-time="true"
        :show-seconds="true"
        @date-select="updateDateFromCalendar"
      />
      <Button
        name="save-date"
        icon="pi pi-check"
        style="margin-left: 23rem; margin-top: 1rem"
        @click="saveFromCalendar"
      />
    </OverlayPanel>
  </div>
</template>

<script setup lang="ts">
  import {
    defineEmits,
    defineProps,
    onMounted,
    PropType,
    ref,
    watch,
  } from "vue";
  import type CSS from "csstype";
  import moment from "moment";

  import Button from "primevue/button";
  import Calendar from "primevue/calendar";
  import InputText from "primevue/inputtext";
  import OverlayPanel from "primevue/overlaypanel";

  import { isValidDate } from "@/etc/validators";

  const emit = defineEmits(["update:modelValue"]);
  const props = defineProps({
    modelValue: {
      type: Date,
      required: true,
      default: undefined,
    },
    placeholder: {
      type: String,
      required: false,
      default: "Select a date",
    },
    overlayStyle: {
      type: Object as PropType<CSS.Properties>,
      required: false,
      default: undefined,
    },
  });

  const op = ref<OverlayPanel>();
  const overlayStyle = ref<CSS.Properties>();
  const displayUtcString = ref<string>("");
  const calendarDate = ref<Date>(); // Offset-adjusted date so that the primevue calendar is in UTC
  const inputClass = ref<string>();

  const setCalendarDateToOffset = (date: Date) => {
    const years = date.getUTCFullYear();
    const months = date.getUTCMonth();
    const days = date.getUTCDate();
    const hours = date.getUTCHours();
    const minutes = date.getUTCMinutes();
    const seconds = date.getUTCSeconds();
    calendarDate.value = new Date(years, months, days, hours, minutes, seconds);
  };

  const getUtcDateString = (date: Date): string => {
    return moment.utc(date).format("MM/DD/YYYY HH:mm:ss");
  };

  const parseUtcString = (dateString: string): Date => {
    return moment.utc(dateString, "MM/DD/YYYY HH:mm:ss").local().toDate();
  };

  onMounted(() => {
    if (!props.overlayStyle) {
      overlayStyle.value = {
        width: "450px",
      };
    } else {
      overlayStyle.value = props.overlayStyle;
    }

    if (props.modelValue) {
      displayUtcString.value = getUtcDateString(props.modelValue);
      setCalendarDateToOffset(props.modelValue);
    } else {
      setCalendarDateToOffset(new Date());
    }
  });

  watch(
    () => props.modelValue,
    () => {
      if (props.modelValue) {
        displayUtcString.value = getUtcDateString(props.modelValue);
        setCalendarDateToOffset(props.modelValue);
      } else {
        displayUtcString.value = "";
        setCalendarDateToOffset(new Date());
      }
    },
  );

  const updateDateFromCalendar = () => {
    if (!calendarDate.value) {
      return;
    }
    const years = calendarDate.value.getFullYear();
    const months = calendarDate.value.getMonth();
    const days = calendarDate.value.getDate();
    const hours = calendarDate.value.getHours();
    const minutes = calendarDate.value.getMinutes();
    const seconds = calendarDate.value.getSeconds();
    const calendarDateCorrect = new Date(
      Date.UTC(years, months, days, hours, minutes, seconds),
    );

    displayUtcString.value = getUtcDateString(calendarDateCorrect);
  };

  const updateDateFromInput = () => {
    const parsedDate = parseUtcString(displayUtcString.value);
    if (isValidDate(parsedDate)) {
      setCalendarDateToOffset(parsedDate);
      inputClass.value = "";
    } else if (displayUtcString.value.length === 0) {
      inputClass.value = "";
      setCalendarDateToOffset(new Date());
    } else {
      inputClass.value = "p-invalid";
    }
  };

  const updateModelValue = () => {
    const parsedDate = parseUtcString(displayUtcString.value);
    if (isValidDate(parsedDate)) {
      emit("update:modelValue", parsedDate);
    } else if (displayUtcString.value.length === 0) {
      emit("update:modelValue", null);
    }
  };

  const saveFromCalendar = () => {
    toggle(new Event("toggle"));
    updateModelValue();
  };

  const toggle = (event: Event) => {
    op.value?.toggle(event);
  };
</script>
