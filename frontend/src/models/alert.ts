import { pageOptionParams, UUID } from "./base";
import { nodeCreate, nodeRead, nodeReadPage, nodeUpdate } from "./node";
import { alertDispositionRead } from "./alertDisposition";
import { alertQueueRead } from "./alertQueue";
import { alertToolRead } from "./alertTool";
import { alertToolInstanceRead } from "./alertToolInstance";
import { alertTypeRead } from "./alertType";
import { analysisTreeRead } from "./analysis";
import { userRead } from "./user";
import { nodeCommentRead } from "./nodeComment";
import { nodeTagRead } from "./nodeTag";
import { observableTreeRead } from "./observable";
import { observableTypeRead } from "./observableType";
import { nodeThreatActorRead } from "./nodeThreatActor";
import { nodeThreatRead } from "./nodeThreat";

export interface alertCreate extends nodeCreate {
  description?: string;
  eventTime?: Date;
  insertTime?: Date;
  instructions?: string;
  name: string;
  observables: { type: string; value: string }[];
  owner?: string;
  queue: string;
  tool?: string;
  toolInstance?: string;
  type: string;
  [key: string]: unknown;
}

export interface alertSummaryRead extends nodeRead {
  description: string | null;
  disposition: alertDispositionRead | null;
  dispositionTime: Date | null;
  dispositionUser: userRead | null;
  eventTime: Date;
  eventUuid: UUID | null;
  insertTime: Date;
  instructions: string | null;
  name: string;
  owner: userRead | null;
  queue: alertQueueRead;
  tool: alertToolRead | null;
  toolInstance: alertToolInstanceRead | null;
  type: alertTypeRead;
}

// High-level alert data that will be displayed in Manage Alerts or in an event
export interface alertTableSummary {
  comments: nodeCommentRead[];
  description: string;
  disposition: string;
  dispositionTime: Date | null;
  dispositionUser: string;
  eventTime: Date;
  insertTime: Date;
  name: string;
  owner: string;
  queue: string;
  tags: nodeTagRead[];
  tool: string;
  type: string;
  uuid: UUID;
}

export interface alertTreeRead {
  alert: alertSummaryRead;
  tree: (analysisTreeRead | observableTreeRead)[];
}

export interface alertReadPage extends nodeReadPage {
  items: alertSummaryRead[];
}

export interface alertUpdate extends nodeUpdate {
  description?: string | null;
  disposition?: string;
  eventTime?: Date;
  eventUuid?: UUID;
  insertTime?: Date;
  instructions?: string | null;
  owner?: string;
  queue?: string;
  [key: string]: unknown;
}

export interface alertFilterParams extends pageOptionParams {
  disposition?: alertDispositionRead;
  dispositionUser?: userRead;
  dispositionedAfter?: Date;
  dispositionedBefore?: Date;
  eventUuid?: string;
  eventTimeAfter?: Date;
  eventTimeBefore?: Date;
  insertTimeAfter?: Date;
  insertTimeBefore?: Date;
  name?: string;
  observable?: { category: observableTypeRead; value: string };
  observableTypes?: observableTypeRead[];
  observableValue?: string;
  owner?: userRead;
  queue?: alertQueueRead;
  sort?: string;
  tags?: nodeTagRead[];
  threatActor?: nodeThreatActorRead;
  threats?: nodeThreatRead[];
  tool?: alertToolRead;
  toolInstance?: alertToolInstanceRead;
  type?: alertTypeRead;
}

export type alertFilterNameTypes = Extract<keyof alertFilterParams, string>;
export type alertFilterValues =
  | (string &
      observableTypeRead[] &
      nodeThreatRead[] &
      nodeTagRead[] &
      Date & {
        category: observableTypeRead;
        value: string;
      } & alertDispositionRead &
      userRead &
      alertQueueRead &
      nodeThreatActorRead &
      alertToolRead &
      alertToolInstanceRead &
      alertTypeRead)
  | undefined;
