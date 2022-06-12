import { observableRead, observableTreeRead } from "@/models/observable";
import { genericObjectReadFactory } from "./genericObject";

export const observableReadFactory = ({
  time = new Date("2020-01-01"),
  uuid = "observableUuid1",
  value = "TestObservable",
  comments = [],
  context = null,
  directives = [],
  detectionPoints = [],
  forDetection = false,
  expiresOn = null,
  permanentTags = [],
  threatActors = [],
  threats = [],
  type = genericObjectReadFactory({ value: "testObservableType" }),
  version = "observableVersion1",
  observableRelationships = [],
}: Partial<observableRead> = {}): observableRead => ({
  time: time,
  uuid: uuid,
  value: value,
  comments: comments,
  context: context,
  directives: directives,
  detectionPoints: detectionPoints,
  forDetection: forDetection,
  expiresOn: expiresOn,
  permanentTags: permanentTags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  nodeType: "observable",
  version: version,
  observableRelationships: observableRelationships,
});

export const observableTreeReadFactory = ({
  children = [],
  time = new Date("2020-01-01"),
  uuid = "observableUuid1",
  value = "TestObservable",
  comments = [],
  context = null,
  directives = [],
  detectionPoints = [],
  firstAppearance = undefined,
  forDetection = false,
  expiresOn = null,
  metadata = [],
  permanentTags = [],
  threatActors = [],
  threats = [],
  type = genericObjectReadFactory({ value: "testObservableType" }),
  version = "observableVersion1",
  observableRelationships = [],
}: Partial<observableTreeRead> = {}): observableTreeRead => ({
  children: children,
  uuid: uuid,
  version: version,
  time: time,
  value: value,
  comments: comments,
  context: context,
  directives: directives,
  detectionPoints: detectionPoints,
  firstAppearance: firstAppearance,
  forDetection: forDetection,
  expiresOn: expiresOn,
  metadata: metadata,
  permanentTags: permanentTags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  nodeType: "observable",
  observableRelationships: observableRelationships,
});
