import { alertFilterNameTypes } from "@/models/alert";
import { filterOption } from "@/models/base";
import { alertDispositionRead } from "@/models/alertDisposition";
import { alertQueueRead } from "@/models/alertQueue";
import { alertToolRead } from "@/models/alertTool";
import { alertToolInstanceRead } from "@/models/alertToolInstance";
import { alertTypeRead } from "@/models/alertType";
import { nodeTagRead } from "@/models/nodeTag";
import { nodeThreatActorRead } from "@/models/nodeThreatActor";
import { observableTypeRead } from "@/models/observableType";
import { userRead } from "@/models/user";

// ** Base ** //

export const filterTypes = {
  MULTISELECT: "multiselect",
  CHIPS: "chips",
  SELECT: "select",
  DATE: "date",
  INPUT_TEXT: "inputText",
  CATEGORIZED_VALUE: "categorizedValue",
};

// ** Alerts ** //

export const alertFilterNames: Record<string, alertFilterNameTypes> = {
  DISPOSITION_FILTER: "disposition",
  DISPOSITION_USER_FILTER: "dispositionUser",
  DISPOSITIONED_AFTER_FILTER: "dispositionedAfter",
  DISPOSITIONED_BEFORE_FILTER: "dispositionedBefore",
  EVENT_UUID_FILTER: "eventUuid",
  EVENT_TIME_AFTER_FILTER: "eventTimeAfter",
  EVENT_TIME_BEFORE_FILTER: "eventTimeBefore",
  INSERT_TIME_AFTER_FILTER: "insertTimeAfter",
  INSERT_TIME_BEFORE_FILTER: "insertTimeBefore",
  NAME_FILTER: "name",
  OBSERVABLE_FILTER: "observable",
  OBSERVABLE_TYPES_FILTER: "observableTypes",
  OBSERVABLE_VALUE_FILTER: "observableValue",
  OWNER_FILTER: "owner",
  QUEUE_FILTER: "queue",
  TAGS_FILTER: "tags",
  THREAT_ACTOR_FILTER: "threatActor",
  THREATS_FILTER: "threats",
  TOOL_FILTER: "tool",
  TOOL_INSTANCE_FILTER: "toolInstance",
  TYPE_FILTER: "type",
};

export const alertFilters: readonly filterOption[] = [
  {
    name: alertFilterNames.DISPOSITION_FILTER,
    label: "Disposition",
    type: filterTypes.SELECT,
    options: "alertDisposition",
    formatForAPI: (filter: alertDispositionRead) => {
      return filter.value;
    },
  },
  {
    name: alertFilterNames.DISPOSITION_USER_FILTER,
    label: "Dispositioned By",
    type: filterTypes.SELECT,
    options: "users",
    optionLabel: "displayName",
    formatForAPI: (filter: userRead) => {
      return filter.username;
    },
  },
  {
    name: alertFilterNames.DISPOSITIONED_AFTER_FILTER,
    label: "Dispositioned After",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.DISPOSITIONED_BEFORE_FILTER,
    label: "Dispositioned Before",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.EVENT_UUID_FILTER,
    label: "Event",
    type: filterTypes.SELECT,
    options: "events",
  },
  {
    name: alertFilterNames.EVENT_TIME_AFTER_FILTER,
    label: "Event Time After",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.EVENT_TIME_BEFORE_FILTER,
    label: "Event Time Before",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.INSERT_TIME_AFTER_FILTER,
    label: "Insert Time After",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.INSERT_TIME_BEFORE_FILTER,
    label: "Insert Time Before",
    type: filterTypes.DATE,
  },
  {
    name: alertFilterNames.NAME_FILTER,
    label: "Name",
    type: filterTypes.INPUT_TEXT,
  },
  {
    name: alertFilterNames.OBSERVABLE_FILTER,
    label: "Observable",
    type: filterTypes.CATEGORIZED_VALUE,
    options: "observableType",
    formatForAPI: (filter: { category: observableTypeRead; value: string }) => {
      return `${filter.category.value}|${filter.value}`;
    },
  },
  {
    name: alertFilterNames.OBSERVABLE_TYPES_FILTER,
    label: "Observable Types",
    type: filterTypes.MULTISELECT,
    options: "observableType",
    formatForAPI: (filter: observableTypeRead[]) => {
      return filter
        .map(function (elem) {
          return elem.value;
        })
        .join();
    },
  },
  {
    name: alertFilterNames.OBSERVABLE_VALUE_FILTER,
    label: "Observable Value",
    type: filterTypes.INPUT_TEXT,
  },
  {
    name: alertFilterNames.OWNER_FILTER,
    label: "Owner",
    type: filterTypes.SELECT,
    options: "users",
    optionLabel: "displayName",
    formatForAPI: (filter: userRead) => {
      return filter.username;
    },
  },
  {
    name: alertFilterNames.QUEUE_FILTER,
    label: "Queue",
    type: filterTypes.SELECT,
    options: "alertQueue",
    formatForAPI: (filter: alertQueueRead) => {
      return filter.value;
    },
  },
  {
    name: alertFilterNames.TAGS_FILTER,
    label: "Tags",
    type: filterTypes.CHIPS,
    options: "nodeTag",
    formatForAPI: (filter: nodeTagRead[]) => {
      return filter
        .map(function (elem) {
          return elem.value;
        })
        .join();
    },
  },
  {
    name: alertFilterNames.THREAT_ACTOR_FILTER,
    label: "Threat Actor",
    type: filterTypes.SELECT,
    options: "nodeThreat",
    formatForAPI: (filter: nodeThreatActorRead) => {
      return filter.value;
    },
  },
  {
    name: alertFilterNames.THREATS_FILTER,
    label: "Threats",
    type: filterTypes.CHIPS,
    options: "nodeThreatActor",
    formatForAPI: (filter: nodeThreatActorRead[]) => {
      return filter
        .map(function (elem) {
          return elem.value;
        })
        .join();
    },
  },
  {
    name: alertFilterNames.TOOL_FILTER,
    label: "Tool",
    type: filterTypes.SELECT,
    options: "tool",
    formatForAPI: (filter: alertToolRead) => {
      return filter.value;
    },
  },
  {
    name: alertFilterNames.TOOL_INSTANCE_FILTER,
    label: "Tool Instance",
    type: filterTypes.SELECT,
    options: "toolInstance",
    formatForAPI: (filter: alertToolInstanceRead) => {
      return filter.value;
    },
  },
  {
    name: alertFilterNames.TYPE_FILTER,
    label: "Type",
    type: filterTypes.SELECT,
    options: "alertType",
    formatForAPI: (filter: alertTypeRead) => {
      return filter.value;
    },
  },
] as const;

export const alertRangeFilters = {
  "Event Time": {
    start: alertFilterNames.EVENT_TIME_AFTER_FILTER,
    end: alertFilterNames.EVENT_TIME_BEFORE_FILTER,
  },
  "Insert Time": {
    start: alertFilterNames.INSERT_TIME_AFTER_FILTER,
    end: alertFilterNames.INSERT_TIME_BEFORE_FILTER,
  },
  "Disposition Time": {
    start: alertFilterNames.DISPOSITIONED_AFTER_FILTER,
    end: alertFilterNames.DISPOSITIONED_BEFORE_FILTER,
  },
};
