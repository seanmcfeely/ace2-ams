import {
  observableInAlertRead,
  observableRead,
  observableTreeRead,
} from "@/models/observable";
import { analysisMetadataReadFactory } from "./analysisMetadata";
import { genericObjectReadFactory } from "./genericObject";

export const observableReadFactory = ({
  uuid = "observableUuid1",
  value = "TestObservable",
  comments = [],
  context = null,
  forDetection = false,
  expiresOn = null,
  tags = [],
  threatActors = [],
  threats = [],
  type = genericObjectReadFactory({ value: "testObservableType" }),
  version = "observableVersion1",
  observableRelationships = [],
}: Partial<observableRead> = {}): observableRead => ({
  uuid: uuid,
  value: value,
  comments: comments,
  context: context,
  forDetection: forDetection,
  expiresOn: expiresOn,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  objectType: "observable",
  version: version,
  observableRelationships: observableRelationships,
});

export const observableInAlertReadFactory = ({
  uuid = "observableUuid1",
  value = "TestObservable",
  analysisMetadata = analysisMetadataReadFactory(),
  comments = [],
  context = null,
  dispositionHistory = [],
  forDetection = false,
  expiresOn = null,
  tags = [],
  threatActors = [],
  threats = [],
  type = genericObjectReadFactory({ value: "testObservableType" }),
  version = "observableVersion1",
  observableRelationships = [],
}: Partial<observableInAlertRead> = {}): observableInAlertRead => ({
  uuid: uuid,
  value: value,
  analysisMetadata: analysisMetadata,
  comments: comments,
  context: context,
  dispositionHistory: dispositionHistory,
  forDetection: forDetection,
  expiresOn: expiresOn,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  objectType: "observable",
  version: version,
  observableRelationships: observableRelationships,
});

export const observableTreeReadFactory = ({
  children = [],
  uuid = "observableUuid1",
  value = "TestObservable",
  analysisMetadata = analysisMetadataReadFactory(),
  comments = [],
  context = null,
  dispositionHistory = [],
  firstAppearance = undefined,
  forDetection = false,
  expiresOn = null,
  tags = [],
  threatActors = [],
  threats = [],
  type = genericObjectReadFactory({ value: "testObservableType" }),
  version = "observableVersion1",
  observableRelationships = [],
}: Partial<observableTreeRead> = {}): observableTreeRead => ({
  children: children,
  uuid: uuid,
  version: version,
  value: value,
  analysisMetadata: analysisMetadata,
  comments: comments,
  context: context,
  dispositionHistory: dispositionHistory,
  firstAppearance: firstAppearance,
  forDetection: forDetection,
  expiresOn: expiresOn,
  tags: tags,
  threatActors: threatActors,
  threats: threats,
  type: type,
  objectType: "observable",
  observableRelationships: observableRelationships,
});
