<!-- TheAlertSummary.vue -->

<template>
  <Card v-if="alertStore.openAlertSummary">
    <template #title>
      {{ alertStore.open.name }}
      <Button
        icon="pi pi-link"
        class="p-button-secondary p-button-outlined p-button-sm"
        @click="copyLink"
      />
      <MetadataTag
        v-for="tag in getAllAlertTags(alertStore.open)"
        :key="tag.uuid"
        :tag="tag"
      ></MetadataTag>
    </template>

    <template #content>
      <Accordion :active-index="0">
        <AccordionTab header="Details">
          <div class="p-datatable-wrapper">
            <table class="p-datatable p-datatable-sm full-size-table">
              <tbody class="p-datatable-tbody">
                <tr v-for="key in alertDetailKeys" :key="key.value">
                  <td class="header-cell">{{ key.label }}</td>
                  <td class="content-cell">
                    <AlertTableCell
                      :field="key.value as string"
                      :data="alertStore.openAlertSummary"
                    ></AlertTableCell>
                  </td>
                </tr>
                <tr v-if="!alertStore.open.childDetectionPoints.length">
                  <td class="header-cell">No detections found</td>
                  <td></td>
                </tr>
                <tr
                  v-for="detection in alertStore.open.childDetectionPoints"
                  :key="detection.uuid"
                >
                  <td class="header-cell">Detection</td>
                  <td class="content-cell">
                    <span>
                      <span style="vertical-align: baseline">{{
                        detection.value
                      }}</span>
                      <Button
                        style="vertical-align: baseline"
                        icon="pi pi-directions"
                        class="p-button-rounded p-button-secondary p-button-text"
                        @click="scrollTo(detection.uuid)"
                      />
                    </span>
                  </td>
                </tr>
                <tr v-if="alertStore.open['instructions']">
                  <td class="header-cell">Instructions</td>
                  <td class="content-cell">
                    {{ alertStore.open["instructions"] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </AccordionTab>
      </Accordion>
    </template>
  </Card>
</template>

<script setup lang="ts">
  import Accordion from "primevue/accordion";
  import AccordionTab from "primevue/accordiontab";
  import Button from "primevue/button";
  import Card from "primevue/card";

  import MetadataTag from "@/components/Metadata/MetadataTag.vue";

  import { copyToClipboard, scrollTo } from "@/etc/helpers";
  import { useAlertStore } from "@/stores/alert";
  import { getAllAlertTags } from "@/etc/helpers";
  import AlertTableCell from "./AlertTableCell.vue";
  import { alertSummary } from "@/models/alert";

  const alertStore = useAlertStore();

  const alertDetailKeys: { value: keyof alertSummary; label: string }[] = [
    { value: "insertTime", label: "Insert Time (UTC)" },
    { value: "eventTime", label: "Event Time (UTC)" },
    { value: "status", label: "Status" },
    { value: "tool", label: "Tool" },
    { value: "toolInstance", label: "Tool Instance" },
    { value: "type", label: "Type" },
    { value: "dispositionWithUserAndTime", label: "Disposition" },
    { value: "eventUuid", label: "Event" },
    { value: "queue", label: "Queue" },
    { value: "ownerWithTime", label: "Owner" },
    { value: "comments", label: "Comments" },
  ];

  function copyLink() {
    copyToClipboard(window.location.href);
  }
</script>

<style scoped>
  .full-size-table {
    width: 100%;
  }

  .header-cell {
    width: 15%;
    font-weight: bold;
  }

  .content-cell {
    width: 85%;
  }
</style>
