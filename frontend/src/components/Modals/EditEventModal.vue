]
<!-- EditEventModal.vue -->
<!-- Edit various configured properties of an event -->

<template>
  <BaseModal
    :name="name"
    header="Edit Event"
    :style="{ width: '70vw' }"
    data-cy="edit-event-modal"
  >
    <div>
      <div v-if="error" class="p-col">
        <Message severity="error" @close="handleError">{{ error }}</Message>
      </div>
    </div>
    <div v-if="isLoading">Loading...</div>
    <div v-else class="p-grid p-fluid p-formgrid p-grid">
      <div v-for="field of fieldOptions" :key="field.name" class="field grid">
        <label for="field.name" class="col-fixed" style="width: 30%"
          ><span style="font-weight: bold">{{ field.label }}</span></label
        >
        <div class="col" :data-cy="`event-${field.name}-field`">
          <NodeThreatSelector
            v-if="field.name == 'threats'"
            v-model="formFields['threats'].propertyValue"
          ></NodeThreatSelector>
          <NodeCommentEditor
            v-else-if="field.name == 'comments'"
            v-model="formFields['comments'].propertyValue"
          ></NodeCommentEditor>
          <NodePropertyInput
            v-else
            id="field.name"
            v-model="formFields[field.name]"
            :queue="event.queue.value"
            :fixed-property-type="true"
            :allow-delete="false"
            form-type="edit"
          />
        </div>
      </div>
    </div>
    <template #footer>
      <Button
        data-cy="nevermind-edit-event-button"
        label="Nevermind"
        icon="pi pi-times"
        class="p-button-text"
        @click="close"
      />
      <Button
        label="Save"
        icon="pi pi-check"
        data-cy="save-edit-event-button"
        @click="saveEvent()"
      />
    </template>
  </BaseModal>
</template>

<script setup>
  import {
    computed,
    defineEmits,
    defineProps,
    onMounted,
    ref,
    inject,
    watch,
  } from "vue";

  import Button from "primevue/button";
  import Message from "primevue/message";

  import BaseModal from "@/components/Modals/BaseModal.vue";
  import NodePropertyInput from "../Node/NodePropertyInput.vue";
  import NodeThreatSelector from "../Node/NodeThreatSelector.vue";

  import { Event } from "@/services/api/event";
  import { useEventStore } from "@/stores/event";
  import { useModalStore } from "@/stores/modal";
  import { populateEventStores } from "@/etc/helpers";
  import { isObject } from "@/etc/validators";
  import NodeCommentEditor from "../Node/NodeCommentEditor.vue";
  import { NodeComment } from "@/services/api/nodeComment";

  const modalStore = useModalStore();
  const eventStore = useEventStore();

  const props = defineProps({
    name: { type: String, required: true },
    eventUuid: { type: String, required: true },
  });

  const emit = defineEmits(["requestReload"]);

  const availableEditFields = inject("availableEditFields");

  const error = ref(null);
  const event = ref(null);
  const fieldOptionObjects = ref({});
  const formFields = ref({});
  const isLoading = ref(false);

  onMounted(async () => {
    await fetchEvent();

    for (const option of availableEditFields[event.value.queue.value]) {
      // Create a lookup by field/option name of all the fieldOptionObjects
      fieldOptionObjects.value[option.name] = option;
      // Set up all the form field objects (to be used in NodePropertyInput)
      formFields.value[option.name] = {
        propertyType: option.name,
        propertyValue: null,
      };
    }
  });

  // Load event data only when modal becomes active
  watch(modalStore, async () => {
    if (modalStore.active === props.name) {
      await initializeData();
    }
  });

  const fieldOptions = computed(() => {
    if (event.value) {
      return availableEditFields[event.value.queue.value];
    } else {
      return [];
    }
  });

  const updateData = computed(() => {
    // All updateData will have the event uuid
    const data = { uuid: props.eventUuid };
    // Add the formatted valueds for all fields in the form
    for (const field in formFields.value) {
      data[field] = formatValue(field, formFields.value[field].propertyValue);
    }
    return [data];
  });

  const fetchEvent = async () => {
    event.value = await Event.read(props.eventUuid);
  };

  const initializeData = async () => {
    isLoading.value = true;
    try {
      await fetchEvent();
      await populateEventStores();
      await resetForm();
    } catch (err) {
      error.value = err.message;
    }
    isLoading.value = false;
  };

  const resetForm = async () => {
    if (event.value) {
      fillFormFields();
    }
  };

  const fillFormFields = () => {
    // Fill in form field values with data from event
    for (const field in formFields.value) {
      formFields.value[field].propertyValue =
        event.value[formFields.value[field].propertyType];
    }
  };

  const saveEvent = async () => {
    isLoading.value = true;

    try {
      await eventStore.update(updateData.value);
      if ("comments" in formFields.value) {
        await saveEventComments();
      }
    } catch (err) {
      error.value = err.message;
    }

    isLoading.value = false;
    if (!error.value) {
      close();
      emit("requestReload");
    }
  };

  const saveEventComments = async () => {
    for (const comment of formFields.value["comments"].propertyValue) {
      await NodeComment.update(comment.uuid, {
        value: comment.value,
      });
    }
  };

  function formatValue(field, value) {
    // If the field value is an array, try to build a list of strings using either
    // the valueProperty (if available), or 'value' as the valueProperty as default
    if (Array.isArray(value)) {
      let valueProperty = "value";
      if (fieldOptionObjects.value[field].valueProperty) {
        valueProperty = fieldOptionObjects.value[field].valueProperty;
      }
      return value.map((x) => (x[valueProperty] ? x[valueProperty] : x));
    } else if (
      isObject(value) &&
      fieldOptionObjects.value[field].valueProperty
    ) {
      // If there is a 'valueProperty' available for the field, and the field value
      // Is an object, use that property as a value
      return value[fieldOptionObjects.value[field].valueProperty];
    }
    // Otherwise return the plain value
    return value;
  }

  const handleError = () => {
    error.value = null;
    close();
  };

  const close = () => {
    modalStore.close(props.name);
  };
</script>