<template>
  <InputText
    id="test"
    v-model="displayUtcString"
    :placeholder="placeholder"
    :class="inputClass"
    @focus="toggle"
    @input="updateDateFromInput"
    @keydown.esc="updateModelValue"
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
      @click="hidePanel"
    />
  </OverlayPanel>
</template>

<script setup lang="ts">
  import {
    ref,
    defineProps,
    defineEmits,
    onMounted,
    PropType,
    watch,
  } from "vue";
  import { isValidDate } from "@/etc/validators";
  import OverlayPanel from "primevue/overlaypanel";
  import type CSS from "csstype";

  import Calendar from "primevue/calendar";
  import InputText from "primevue/inputtext";
  import Button from "primevue/button";

  import moment from "moment";

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
  const emit = defineEmits(["update:modelValue"]);

  const overlayStyle = ref<CSS.Properties>();
  const displayUtcString = ref<string>("");
  const calendarDate = ref<Date>();
  const inputClass = ref<string>();
  const hidePanel = () => {
    toggle(new Event("toggle"));
    updateModelValue();
  };

  const op = ref<OverlayPanel>();
  const toggle = (event: Event) => {
    op.value?.toggle(event);
  };

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
    // emit("update:modelValue", parseUtcString(displayUtcString.value));
  };

  const updateDateFromInput = () => {
    const parsedDate = parseUtcString(displayUtcString.value);
    if (isValidDate(parsedDate)) {
      setCalendarDateToOffset(parsedDate);
      // emit("update:modelValue", parsedDate);
      inputClass.value = "";
    } else if (displayUtcString.value.length === 0) {
      inputClass.value = "";
      // emit("update:modelValue", null);
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
</script>
