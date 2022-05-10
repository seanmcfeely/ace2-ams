<!-- AlertTableExpansion.vue -->
<!-- Contains logic and functionality for displaying data in alert row dropdown, currently list of alert's observables -->

<template>
  <div v-if="isLoading" style="flex: 1">
    <ul>
      <li><Skeleton width="30%" data-cy="loading-observable"></Skeleton></li>
      <li><Skeleton width="25%" data-cy="loading-observable"></Skeleton></li>
      <li><Skeleton width="30%" data-cy="loading-observable"></Skeleton></li>
      <li><Skeleton width="25%" data-cy="loading-observable"></Skeleton></li>
    </ul>
  </div>
  <span v-else-if="observablesIsEmpty"
    >No observables exist for this alert.</span
  >
  <ul v-else>
    <!-- List each observable with link to filter -->
    <li v-for="obs of observables" :key="obs.value">
      <span class="link-text" @click="filterByObservable(obs)">{{
        formatObservable(obs)
      }}</span>
      <!-- Display each observable's tags -->
      <NodeTagVue v-for="tag of obs.tags" :key="tag.value" :tag="tag" />
    </li>
  </ul>
</template>

<script setup lang="ts">
  import { computed, defineProps, PropType } from "vue";
  import Skeleton from "primevue/skeleton";

  import { useFilterStore } from "@/stores/filter";
  import NodeTagVue from "@/components/Node/NodeTag.vue";

  import { observableRead } from "@/models/observable";

  const props = defineProps({
    observables: {
      type: Array as PropType<observableRead[] | null>,
      required: true,
    },
  });

  const isLoading = computed(() => {
    return props.observables === null;
  });

  const observablesIsEmpty = computed(() => {
    return Array.isArray(props.observables) && !props.observables.length;
  });

  const formatObservable = (observable: observableRead) => {
    return `${observable.type.value} : ${observable.value}`;
  };

  const filterStore = useFilterStore();
  const filterByObservable = (observable: observableRead) => {
    filterStore.bulkSetFilters({
      nodeType: "alerts",
      filters: {
        observable: {
          category: observable.type,
          value: observable.value,
        },
      },
    });
  };
</script>

<style>
  .link-text:hover {
    cursor: pointer;
    text-decoration: underline;
    font-weight: bold;
  }
</style>