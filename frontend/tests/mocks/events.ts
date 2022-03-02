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
  name = "Test event",
  owner = undefined,
  ownershipTime = undefined,
  preventionTools = undefined,
  queue = "testQueue",
  remediationTime = undefined,
  riskLevel = undefined,
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
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediationTime: remediationTime,
  riskLevel: riskLevel,
  source: source,
  status: status,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  vectors: vectors,
});

export const eventReadFactory = ({
  autoAlertTime = null,
  autoDispositionTime = null,
  autoEventTime = null,
  autoOwnershipTime = null,
  alertTime = null,
  alertUuids = [],
  comments = [],
  containTime = null,
  creationTime = new Date("2020-01-01"),
  dispositionTime = null,
  eventTime = null,
  name = "Test Event",
  nodeType = "",
  owner = null,
  ownershipTime = null,
  preventionTools = [],
  queue = genericObjectReadFactory(),
  remediations = [],
  remediationTime = null,
  riskLevel = null,
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
  autoAlertTime: autoAlertTime,
  autoDispositionTime: autoDispositionTime,
  autoEventTime: autoEventTime,
  autoOwnershipTime: autoOwnershipTime,
  alertTime: alertTime,
  alertUuids: alertUuids,
  comments: comments,
  containTime: containTime,
  creationTime: creationTime,
  dispositionTime: dispositionTime,
  eventTime: eventTime,
  name: name,
  nodeType: nodeType,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediations: remediations,
  remediationTime: remediationTime,
  riskLevel: riskLevel,
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
  name = undefined,
  owner = undefined,
  ownershipTime = undefined,
  preventionTools = undefined,
  queue = undefined,
  remediationTime = undefined,
  riskLevel = undefined,
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
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  preventionTools: preventionTools,
  queue: queue,
  remediationTime: remediationTime,
  riskLevel: riskLevel,
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
  riskLevel = "None",
  status = "None",
  tags = [],
  threats = [],
  threatActors = [],
  type = "None",
  uuid = mockEventUUID,
  vectors = [],
  queue = "None",
}: Partial<eventSummary> = {}): eventSummary => ({
  comments: comments,
  createdTime: createdTime,
  name: name,
  owner: owner,
  preventionTools: preventionTools,
  riskLevel: riskLevel,
  status: status,
  tags: tags,
  threats: threats,
  threatActors: threatActors,
  type: type,
  uuid: uuid,
  vectors: vectors,
  queue: queue,
});
