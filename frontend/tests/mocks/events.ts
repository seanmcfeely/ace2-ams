import { UUID } from "@/models/base";
import {
  eventRead,
  eventCreate,
  eventSummary,
  eventUpdate,
} from "@/models/event";
import { genericObjectReadFactory } from "./genericObject";

export const mockEventUUID: UUID = "testEvent1";

export const eventCreateFactory = ({
  alertTime = undefined,
  containTime = undefined,
  dispositionTime = undefined,
  eventTime = undefined,
  historyUsername = "analyst",
  name = "Test event",
  owner = undefined,
  ownershipTime = undefined,
  preventionTools = undefined,
  queue = "testQueue",
  remediationTime = undefined,
  severity = undefined,
  source = undefined,
  status = "OPEN",
  tags = undefined,
  threatActors = undefined,
  threats = undefined,
  type = undefined,
  vectors = undefined,
}: Partial<eventCreate> = {}): eventCreate => ({
  alertTime: alertTime,
  containTime: containTime,
  dispositionTime: dispositionTime,
  eventTime: eventTime,
  historyUsername: historyUsername,
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediationTime: remediationTime,
  severity: severity,
  source: source,
  status: status,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  vectors: vectors,
});

export const eventReadFactory = ({
  allTags = [],
  analysisTypes = [],
  autoAlertTime = null,
  autoDispositionTime = null,
  autoEventTime = null,
  autoOwnershipTime = null,
  alertTime = null,
  alertUuids = [],
  comments = [],
  containTime = null,
  createdTime = "2020-01-01T00:00:00.000000+00:00",
  dispositionTime = null,
  eventTime = null,
  name = "Test Event",
  objectType = "",
  owner = null,
  ownershipTime = null,
  preventionTools = [],
  queue = genericObjectReadFactory(),
  remediations = [],
  remediationTime = null,
  severity = null,
  source = null,
  status = null,
  tags = [],
  threatActors = [],
  threats = [],
  type = null,
  uuid = mockEventUUID,
  vectors = [],
  version = "testEventVersion1",
}: Partial<eventRead> = {}): eventRead => ({
  allTags: allTags,
  analysisTypes: analysisTypes,
  autoAlertTime: autoAlertTime,
  autoDispositionTime: autoDispositionTime,
  autoEventTime: autoEventTime,
  autoOwnershipTime: autoOwnershipTime,
  alertTime: alertTime,
  alertUuids: alertUuids,
  comments: comments,
  containTime: containTime,
  createdTime: createdTime,
  dispositionTime: dispositionTime,
  eventTime: eventTime,
  name: name,
  objectType: objectType,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediations: remediations,
  remediationTime: remediationTime,
  severity: severity,
  source: source,
  status: status,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  uuid: uuid,
  vectors: vectors,
  version: version,
});

export const eventUpdateFactory = ({
  alertTime = undefined,
  containTime = undefined,
  dispositionTime = undefined,
  eventTime = undefined,
  historyUsername = "analyst",
  name = undefined,
  owner = undefined,
  ownershipTime = undefined,
  preventionTools = undefined,
  queue = undefined,
  remediationTime = undefined,
  severity = undefined,
  source = undefined,
  status = undefined,
  tags = undefined,
  threatActors = undefined,
  threats = undefined,
  type = undefined,
  uuid = mockEventUUID,
  vectors = undefined,
}: Partial<eventUpdate> = {}): eventUpdate => ({
  alertTime: alertTime,
  containTime: containTime,
  dispositionTime: dispositionTime,
  eventTime: eventTime,
  historyUsername: historyUsername,
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediationTime: remediationTime,
  severity: severity,
  source: source,
  status: status,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  uuid: uuid,
  vectors: vectors,
});

export const eventSummaryFactory = ({
  comments = [],
  createdTime = new Date("2020-01-01"),
  name = "Test Event",
  owner = "None",
  preventionTools = [],
  severity = "None",
  status = "None",
  tags = [],
  threats = [],
  threatActors = [],
  type = "None",
  uuid = mockEventUUID,
  vectors = [],
  queue = "None",
  remediations = [],
}: Partial<eventSummary> = {}): eventSummary => ({
  comments: comments,
  createdTime: createdTime,
  name: name,
  owner: owner,
  preventionTools: preventionTools,
  severity: severity,
  status: status,
  tags: tags,
  threats: threats,
  threatActors: threatActors,
  type: type,
  uuid: uuid,
  vectors: vectors,
  queue: queue,
  remediations: remediations,
});
