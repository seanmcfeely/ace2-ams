import { historyUsername, pageOptionParams, UUID } from "./base";
import { nodeCreate, nodeRead, nodeReadPage, nodeUpdate } from "./node";
import { alertDispositionRead } from "./alertDisposition";
import { alertToolRead } from "./alertTool";
import { alertToolInstanceRead } from "./alertToolInstance";
import { alertTypeRead } from "./alertType";
import { analysisTreeRead } from "./analysis";
import { userRead } from "./user";
import { nodeCommentRead } from "./nodeComment";
import { nodeDetectionPointRead } from "./nodeDetectionPoint";
import { nodeTagRead } from "./nodeTag";
import { observableCreate, observableTreeRead } from "./observable";
import { observableTypeRead } from "./observableType";
import { nodeThreatActorRead } from "./nodeThreatActor";
import { nodeThreatRead } from "./nodeThreat";
import { queueRead } from "./queue";

export interface alertCreate extends nodeCreate, historyUsername {
  alert: boolean;
  description?: string;
  eventTime?: Date;
  insertTime?: Date;
  instructions?: string;
  name: string;
  observables: observableCreate[];
  owner?: string;
  queue: string;
  tags?: string[];
  threatActors?: string[];
  threats?: string[];
  tool?: string;
  toolInstance?: string;
  type: string;
  [key: string]: unknown;
}

export interface alertRead extends nodeRead {
  alert: boolean;
  childDetectionPoints: nodeDetectionPointRead[];
  childTags: nodeTagRead[];
  childThreatActors: nodeThreatActorRead[];
  childThreats: nodeThreatRead[];
  comments: nodeCommentRead[];
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
  ownershipTime: Date | null;
  queue: queueRead;
  tags: nodeTagRead[];
  threatActors: nodeThreatActorRead[];
  threats: nodeThreatRead[];
  tool: alertToolRead | null;
  toolInstance: alertToolInstanceRead | null;
  type: alertTypeRead;
  [key: string]: unknown;
}

// High-level alert data that will be displayed in Manage Alerts or in an event
export interface alertSummary {
  childTags: nodeTagRead[];
  comments: nodeCommentRead[];
  description: string;
  disposition: string;
  dispositionTime: Date | null;
  dispositionUser: string;
  dispositionWithUserAndTime: string;
  eventTime: Date;
  eventUuid: string;
  insertTime: Date;
  name: string;
  owner: string;
  ownershipTime: Date | null;
  ownerWithTime: string;
  queue: string;
  tags: nodeTagRead[];
  tool: string;
  toolInstance: string;
  type: string;
  uuid: UUID;
}

export interface alertTreeRead extends alertRead {
  rootAnalysisUuid: UUID;
  children: (analysisTreeRead | observableTreeRead)[];
}

export interface alertReadPage extends nodeReadPage {
  items: alertRead[];
}

export interface alertUpdate extends nodeUpdate, historyUsername {
  description?: string | null;
  disposition?: string;
  eventTime?: Date;
  eventUuid?: UUID | null;
  insertTime?: Date;
  instructions?: string | null;
  owner?: string;
  queue?: string;
  tags?: string[];
  threatActors?: string[];
  threats?: string[];
  uuid: UUID;
  [key: string]: unknown;
}

export interface alertFilterParams extends pageOptionParams {
  alertType?: alertTypeRead;
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
  queue?: queueRead;
  sort?: string;
  tags?: string[];
  threatActor?: nodeThreatActorRead;
  threats?: nodeThreatRead[];
  tool?: alertToolRead;
  toolInstance?: alertToolInstanceRead;
  [key: string]: any;
}

export type alertFilterNameTypes = Extract<keyof alertFilterParams, string>;
export type alertFilterValues =
  | (
      | string
      | observableTypeRead[]
      | nodeThreatRead[]
      | nodeTagRead[]
      | Date
      | {
          category: observableTypeRead;
          value: string;
        }
      | alertDispositionRead
      | userRead
      | queueRead
      | nodeThreatActorRead
      | alertToolRead
      | alertToolInstanceRead
      | alertTypeRead
    )
  | undefined;
