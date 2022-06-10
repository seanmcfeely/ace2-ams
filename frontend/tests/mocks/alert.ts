import {
  alertCreate,
  alertRead,
  alertReadPage,
  alertSummary,
  alertTreeRead,
} from "@/models/alert";
import { genericObjectReadFactory } from "./genericObject";

export const alertCreateFactory = ({
  name = "",
  observables = [],
  queue = "",
  type = "",
  historyUsername = "analyst",
}: Partial<alertCreate> = {}): alertCreate => ({
  alert: true,
  name: name,
  observables: observables,
  queue: queue,
  type: type,
  historyUsername: historyUsername,
});

export const alertTreeReadFactory = ({
  children = [],
  childDetectionPoints = [],
  childTags = [],
  childThreatActors = [],
  childThreats = [],
  comments = [],
  description = "",
  disposition = null,
  dispositionTime = null,
  dispositionUser = null,
  eventTime = new Date(Date.UTC(2022, 2, 24)),
  eventUuid = "",
  insertTime = new Date(Date.UTC(2022, 2, 24)),
  instructions = "",
  name = "Test Alert",
  owner = null,
  ownershipTime = null,
  queue = genericObjectReadFactory({ value: "testAlertQueue" }),
  tags = [],
  threatActors = [],
  threats = [],
  tool = genericObjectReadFactory({ value: "testAlertTool" }),
  toolInstance = genericObjectReadFactory({ value: "testAlertToolInstance" }),
  type = genericObjectReadFactory({ value: "testAlertType" }),
  nodeType = "alert",
  uuid = "testAlertUuid",
  version = "testAlertVersion",
  rootAnalysisUuid = "testRootAnalysisUuid",
}: Partial<alertTreeRead> = {}): alertTreeRead => ({
  alert: true,
  children: children,
  childDetectionPoints: childDetectionPoints,
  childTags: childTags,
  childThreatActors: childThreatActors,
  childThreats: childThreats,
  comments: comments,
  description: description,
  disposition: disposition,
  dispositionTime: dispositionTime,
  dispositionUser: dispositionUser,
  eventTime: eventTime,
  eventUuid: eventUuid,
  insertTime: insertTime,
  instructions: instructions,
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  queue: queue,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  tool: tool,
  toolInstance: toolInstance,
  type: type,
  nodeType: nodeType,
  uuid: uuid,
  version: version,
  rootAnalysisUuid: rootAnalysisUuid,
});

export const alertReadFactory = ({
  childDetectionPoints = [],
  childTags = [],
  childThreatActors = [],
  childThreats = [],
  comments = [],
  description = "",
  disposition = null,
  dispositionTime = null,
  ownershipTime = null,
  dispositionUser = null,
  eventTime = new Date(Date.UTC(2022, 2, 24)),
  eventUuid = "",
  insertTime = new Date(Date.UTC(2022, 2, 24)),
  instructions = "",
  name = "Test Alert",
  owner = null,
  queue = genericObjectReadFactory({ value: "testAlertQueue" }),
  tags = [],
  threatActors = [],
  threats = [],
  tool = genericObjectReadFactory({ value: "testAlertTool" }),
  toolInstance = genericObjectReadFactory({ value: "testAlertToolInstance" }),
  type = genericObjectReadFactory({ value: "testAlertType" }),
  nodeType = "alert",
  uuid = "testAlertUuid",
  version = "testAlertVersion",
}: Partial<alertRead> = {}): alertRead => ({
  alert: true,
  childDetectionPoints: childDetectionPoints,
  childTags: childTags,
  childThreatActors: childThreatActors,
  childThreats: childThreats,
  comments: comments,
  description: description,
  disposition: disposition,
  dispositionTime: dispositionTime,
  dispositionUser: dispositionUser,
  eventTime: eventTime,
  eventUuid: eventUuid,
  insertTime: insertTime,
  instructions: instructions,
  name: name,
  owner: owner,
  ownershipTime: ownershipTime,
  queue: queue,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  tool: tool,
  toolInstance: toolInstance,
  type: type,
  nodeType: nodeType,
  uuid: uuid,
  version: version,
});

// These defaults are made with the defaults of the alert and alertTree factories in mind
export const alertSummaryFactory = ({
  childTags = [],
  comments = [],
  description = "",
  disposition = "OPEN",
  dispositionTime = null,
  dispositionUser = "None",
  dispositionWithUserAndTime = "OPEN",
  eventTime = new Date(Date.UTC(2022, 2, 24)),
  eventUuid = "None",
  insertTime = new Date(Date.UTC(2022, 2, 24)),
  name = "Test Alert",
  owner = "None",
  ownerWithTime = "None",
  ownershipTime = null,
  queue = "testAlertQueue",
  tags = [],
  tool = "testAlertTool",
  toolInstance = "testAlertToolInstance",
  type = "testAlertType",
  uuid = "testAlertUuid",
}: Partial<alertSummary> = {}): alertSummary => ({
  childTags: childTags,
  comments: comments,
  description: description,
  disposition: disposition,
  dispositionTime: dispositionTime,
  dispositionUser: dispositionUser,
  dispositionWithUserAndTime: dispositionWithUserAndTime,
  eventTime: eventTime,
  eventUuid: eventUuid,
  insertTime: insertTime,
  name: name,
  owner: owner,
  ownerWithTime: ownerWithTime,
  ownershipTime: ownershipTime,
  queue: queue,
  tags: tags,
  tool: tool,
  toolInstance: toolInstance,
  type: type,
  uuid: uuid,
});

export const alertReadPageFactory = (
  alerts: alertTreeRead[] | alertRead[] = [],
  limit = 50,
  offset = 0,
): alertReadPage => ({
  items: alerts,
  total: alerts.length,
  limit: limit,
  offset: offset,
});
