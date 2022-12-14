<template>
  <div class="formgrid grid">
    <div v-if="!fixedPropertyType" class="field col-fixed">
      <Dropdown
        v-model="propertyType"
        data-cy="property-input-type"
        :options="(propertyTypeOptions as any[])"
        option-label="label"
        type="text"
        class="w-13rem"
        tabindex="1"
        placeholder="Select a property"
        @change="
          clearPropertyValue();
          updatePropertyType($event);
        "
      />
    </div>
    <div class="col w-16rem">
      <div v-if="isInputText" class="field">
        <InputText
          v-model="propertyValue"
          data-cy="property-input-value"
          class="inputfield w-16rem"
          type="text"
          @input="updatePropertyValue"
        ></InputText>
      </div>
      <div v-else-if="isDropdown" class="field">
        <Dropdown
          v-model="propertyValue"
          data-cy="property-input-value"
          class="inputfield w-16rem"
          :options="propertyValueOptions"
          :option-label="propertyValueOptionProperty"
          type="text"
          placeholder="None"
          @change="updatePropertyValue"
        ></Dropdown>
      </div>
      <div v-else-if="isMultiSelect" class="field">
        <Multiselect
          v-model="propertyValue"
          data-cy="property-input-value"
          class="inputfield w-16rem"
          :options="propertyValueOptions"
          :option-label="propertyValueOptionProperty"
          type="text"
          placeholder="None"
          @change="updatePropertyValue"
        ></Multiselect>
      </div>
      <div v-else-if="isChips" class="field p-fluid">
        <Chips
          v-model="propertyValue"
          data-cy="property-input-value"
          class="w-full"
          @update:model-value="updatePropertyValue"
        ></Chips>
      </div>
      <div v-else-if="isDate" class="field">
        <UtcDatePicker
          v-model="propertyValue"
          data-cy="alert-date"
          class="inputfield w-16rem"
          placeholder="Enter a date!"
          @update:model-value="updatePropertyValue"
        />
      </div>
      <div v-else-if="isCategorizedValue">
        <div class="field">
          <Dropdown
            v-model="categorizedValueCategory"
            data-cy="property-input-value-category"
            :options="propertyValueOptions"
            :option-label="propertyValueOptionProperty"
            class="w-16rem"
            type="text"
            @change="updatePropertyValue(categorizedValueObject)"
          ></Dropdown>
        </div>
        <div class="field">
          <InputText
            v-model="categorizedValueValue"
            data-cy="property-input-value-value"
            class="w-16rem"
            type="text"
            @input="updatePropertyValue(categorizedValueObject)"
          ></InputText>
        </div>
      </div>
    </div>
    <div v-if="allowDelete" class="field col-fixed">
      <Button
        data-cy="property-input-delete"
        name="delete-property"
        icon="pi pi-times"
        class="w-3rem"
        @click="$emit('deleteFormField')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    computed,
    defineEmits,
    defineProps,
    inject,
    onMounted,
    ref,
    watch,
    PropType,
  } from "vue";

  import Button from "primevue/button";
  import Chips from "primevue/chips";
  import Dropdown from "primevue/dropdown";
  import InputText from "primevue/inputtext";
  import Multiselect from "primevue/multiselect";

  import UtcDatePicker from "@/components/UserInterface/UtcDatePicker.vue";

  import { propertyOption } from "@/models/base";
  import { isObject } from "@/etc/validators";

  const availableFilters = inject("availableFilters") as Record<
    string,
    readonly propertyOption[]
  >;
  const availableEditFields = inject("availableEditFields") as Record<
    string,
    readonly propertyOption[]
  >;

  interface modelValueProp {
    propertyType: any;
    propertyValue: any;
    notIncluded?: boolean;
  }

  const emit = defineEmits(["update:modelValue", "deleteFormField"]);
  const props = defineProps({
    queue: { type: String, required: true },
    modelValue: {
      type: Object as PropType<modelValueProp>,
      required: true,
    },
    formType: {
      type: String as PropType<"filter" | "edit">,
      required: true,
    },
    fixedPropertyType: { type: Boolean, required: false },
    allowDelete: { type: Boolean, required: false },
  });

  const propertyTypeOptions = computed((): readonly propertyOption[] => {
    return props.formType == "filter"
      ? availableFilters[props.queue]
      : props.formType == "edit"
      ? availableEditFields[props.queue]
      : [];
  });

  const getPropertyTypeObject = (propertyType: string) => {
    if (!propertyType) {
      return propertyTypeOptions.value
        ? propertyTypeOptions.value[0]
        : undefined;
    }
    const property: propertyOption | undefined = propertyTypeOptions.value.find(
      (option) => {
        return option.name === propertyType;
      },
    );
    return property;
  };

  const propertyType = ref(
    getPropertyTypeObject(props.modelValue.propertyType),
  );
  const propertyValue = ref(props.modelValue.propertyValue);

  // The categorizedValue property is a bit tricky
  // We need to copy the values and use those as the model
  // Otherwise, they will directly modify the filterStore state :/
  const categorizedValueCategory = ref();
  const categorizedValueValue = ref();

  const propertyValueOptions = computed(() => {
    if (propertyType.value) {
      let options: Record<string, any>[] = [];

      // Add the null option to the list options, only if the null option exists and is enabled for the current form type
      if (propertyType.value.nullOptions) {
        if (
          (props.formType == "filter" &&
            propertyType.value.nullOptions.nullableFilter) ||
          (props.formType == "edit" &&
            propertyType.value.nullOptions.nullableEdit)
        ) {
          options = [propertyType.value.nullOptions.nullOption];
        }
      }

      if (propertyType.value.store) {
        const store = propertyType.value.store();
        if (propertyType.value.queueDependent) {
          options = [...options, ...store.getItemsByQueue(props.queue)];
        } else {
          options = [...options, ...store.allItems];
        }

        return options;
      }
    }
    return [];
  });

  onMounted(() => {
    // This will update the property to the default if one wasn't provided
    if (propertyType.value) {
      updatePropertyType({ value: propertyType.value });
    }

    // This will udpate the property value to the default (if available) if one wasn't provided
    if (!propertyValue.value) {
      clearPropertyValue();
      updatePropertyValue(propertyValue.value);
    }

    // we need to fill in the placeholder refs (see note above) for categorized value
    else if (isCategorizedValue.value) {
      categorizedValueCategory.value = propertyValue.value.category;
      categorizedValueValue.value = propertyValue.value.value;
    }
  });

  const propertyValueOptionProperty = computed(() => {
    if (propertyType.value) {
      return propertyType.value.optionProperty
        ? propertyType.value.optionProperty
        : "value";
    }
    return undefined;
  });

  const isDate = computed(() => {
    return inputType.value == "date";
  });
  const isCategorizedValue = computed(() => {
    return inputType.value == "categorizedValue";
  });
  const categorizedValueObject = computed(() => {
    return {
      category: categorizedValueCategory.value,
      value: categorizedValueValue.value,
    };
  });
  const isChips = computed(() => {
    return inputType.value == "chips";
  });

  const isInputText = computed(() => {
    return inputType.value == "inputText";
  });

  const isDropdown = computed(() => {
    return inputType.value == "select";
  });

  const isMultiSelect = computed(() => {
    return inputType.value == "multiselect";
  });

  const inputType = computed(() => {
    return propertyType.value ? propertyType.value.type : null;
  });

  watch(propertyType, async () => {
    if (propertyType.value && propertyType.value.store) {
      const store = propertyType.value.store();
      await store.readAll();
    }
  });

  const clearPropertyValue = () => {
    if (isCategorizedValue.value) {
      propertyValue.value = {
        category: propertyValueOptions.value[0],
        value: null,
      };
      categorizedValueCategory.value = propertyValueOptions.value[0];
      categorizedValueValue.value = null;
    } else if (isDropdown.value) {
      propertyValue.value = propertyValueOptions.value[0];
    } else {
      propertyValue.value = null;
    }
  };

  const updatePropertyValue = (newValue: unknown) => {
    let val = newValue;
    if (isObject(newValue)) {
      if ("value" in newValue) {
        if ("category" in newValue || !isObject(newValue.value)) {
          val = newValue;
        } else {
          val = newValue.value;
        }
      } else if (
        "target" in newValue &&
        isObject(newValue.target) &&
        "value" in newValue.target
      ) {
        val = newValue.target.value;
      }
    }

    const updatedModelValue = {
      propertyType: propertyType.value
        ? propertyType.value.name
        : propertyType.value,
      propertyValue: val,
    };

    if (props.modelValue.notIncluded) {
      emit("update:modelValue", {
        ...updatedModelValue,
        notIncluded: props.modelValue.notIncluded,
      });
    } else {
      emit("update:modelValue", updatedModelValue);
    }
  };

  // updatePropertyType will be called from the PrimeVue Dropdown 'change' event or onMounted
  // And so we can guarantee that the type of 'newValue' will be { value: propertyOption }, even though it must be typed as any
  const updatePropertyType = (newValue: any) => {
    const updatedModelValue = {
      propertyType: newValue.value.name
        ? newValue.value.name
        : propertyType.value,
      propertyValue: propertyValue.value,
    };

    if (props.modelValue.notIncluded) {
      emit("update:modelValue", {
        ...updatedModelValue,
        notIncluded: props.modelValue.notIncluded,
      });
    } else {
      emit("update:modelValue", updatedModelValue);
    }
  };
</script>
