<!-- TheAlertActionToolbar.vue -->
<!-- Toolbar containing alert-specific actions, such as Disposition and Remediation -->

<template>
  <div>
    <TheObjectActionToolbarVue
      ref="toolbar"
      :reload-object="props.reloadObject"
    >
      <template #start-left>
        <!-- FALSE POSITIVE -->
        <Button
          v-if="showFalsePositiveShortcut"
          data-cy="false-positive-button"
          class="p-m-1 p-button-normal p-button-success"
          icon="pi pi-thumbs-up"
          label="FP"
          @click="emit('falsePositiveClicked')"
        />
        <!-- IGNORE -->
        <Button
          v-if="showIgnoreShortcut"
          data-cy="ignore-button"
          class="p-m-1 p-button-normal p-button-secondary"
          icon="pi pi-check"
          label="Ignore"
          @click="emit('ignoreClicked')"
        />
        <!-- DISPOSITION -->
        <Button
          data-cy="disposition-button"
          class="p-m-1 p-button-normal p-button-secondary"
          icon="pi pi-thumbs-up"
          label="Disposition"
          @click="open('DispositionModal')"
        />
        <DispositionModal
          name="DispositionModal"
          @request-reload="requestReload"
        />
      </template>
      <template #start-right>
        <!-- ADD OBSERVABLES MODAL -->
        <span v-if="props.reloadObject == 'object'">
          <Button
            data-cy="add-observable-button"
            class="p-m-1 p-button-sm p-button-secondary p-button-outlined"
            style="width: 180px"
            icon="pi pi-plus-circle"
            label="Add Observable(s)"
            @click="open('AddObservablesModal')"
          />
          <AddObservablesModal
            name="AddObservablesModal"
            @request-reload="requestReload"
          />
        </span>
        <!-- REMEDIATE MODAL -->
        <Button
          data-cy="remediate-button"
          class="p-m-1 p-button-sm p-button-secondary p-button-outlined"
          icon="pi pi-times-circle"
          label="Remediate"
          disabled
          @click="open('RemediationModal')"
        />
        <!-- <RemediationModal /> -->
      </template>
    </TheObjectActionToolbarVue>
  </div>
</template>

<script setup lang="ts">
  import { ref, defineEmits, defineProps, PropType } from "vue";

  import Button from "primevue/button";

  import TheObjectActionToolbarVue from "@/components/Objects/TheObjectActionToolbar.vue";
  import DispositionModal from "@/components/Modals/DispositionModal.vue";
  import AddObservablesModal from "@/components/Modals/AddObservablesModal.vue";

  import { useModalStore } from "@/stores/modal";

  const emit = defineEmits(["falsePositiveClicked", "ignoreClicked"]);

  const props = defineProps({
    reloadObject: {
      type: String as PropType<"table" | "object">,
      required: true,
    },
    showFalsePositiveShortcut: {
      type: Boolean,
      required: false,
      default: false,
    },
    showIgnoreShortcut: { type: Boolean, required: false, default: false },
  });

  const modalStore = useModalStore();
  const open = (name: string) => {
    modalStore.open(name);
  };

  const toolbar = ref<InstanceType<typeof TheObjectActionToolbarVue>>();
  const requestReload = () => {
    toolbar.value?.requestReload();
  };
</script>
