import { propertyOption } from "@/models/base";
import {
  alertPropertyTypes,
  alertDispositionProperty,
  alertDispositionedAfterProperty,
  alertDispositionedBeforeProperty,
  alertDispositionUserProperty,
  alertEventTimeAfterProperty,
  alertEventTimeBeforeProperty,
  alertInsertTimeAfterProperty,
  alertInsertTimeBeforeProperty,
  alertToolInstanceProperty,
  alertToolProperty,
  alertTypeProperty,
} from "@/etc/constants/alerts";
import {
  nameProperty,
  observableProperty,
  observableTypesProperty,
  observableValueProperty,
  ownerProperty,
  nodeTagsProperty,
  nodeThreatActorProperty,
  nodeThreatsProperty,
  queueProperty,
} from "../constants/base";

const defaultAlertFilters = [
  alertDispositionProperty,
  alertDispositionUserProperty,
  alertDispositionedAfterProperty,
  alertDispositionedBeforeProperty,
  alertEventTimeAfterProperty,
  alertEventTimeBeforeProperty,
  alertInsertTimeAfterProperty,
  alertInsertTimeBeforeProperty,
  nameProperty,
  observableProperty,
  observableTypesProperty,
  observableValueProperty,
  ownerProperty,
  queueProperty,
  nodeTagsProperty,
  nodeThreatActorProperty,
  nodeThreatsProperty,
  alertToolProperty,
  alertToolInstanceProperty,
  alertTypeProperty,
];

export const alertFilters: Record<string, readonly propertyOption[]> = {
  external: defaultAlertFilters,
  intel: defaultAlertFilters,
  internal: defaultAlertFilters,
} as const;

export const alertRangeFilters = {
  "Event Time": {
    start: alertPropertyTypes.EVENT_TIME_AFTER_PROPERTY,
    end: alertPropertyTypes.EVENT_TIME_BEFORE_PROPERTY,
  },
  "Insert Time": {
    start: alertPropertyTypes.INSERT_TIME_AFTER_PROPERTY,
    end: alertPropertyTypes.INSERT_TIME_BEFORE_PROPERTY,
  },
  "Disposition Time": {
    start: alertPropertyTypes.DISPOSITIONED_AFTER_PROPERTY,
    end: alertPropertyTypes.DISPOSITIONED_BEFORE_PROPERTY,
  },
};
