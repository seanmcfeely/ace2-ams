import { UUID } from "./base";
import { userRead } from "./user";

export interface nodeCommentCreate {
  nodeUuid: UUID;
  uuid?: UUID;
  username: string;
  value: string;
  [key: string]: unknown;
}

export interface nodeCommentRead {
  insertTime: string;
  nodeUuid: UUID;
  user: userRead;
  uuid: UUID;
  value: string;
}

export interface nodeCommentUpdate {
  username: string;
  value: string;
  [key: string]: unknown;
}
