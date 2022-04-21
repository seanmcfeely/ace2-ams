import {
  observableActionCommand,
  observableTreeRead,
} from "@/models/observable";
import { observableTypeMetaData } from "@/models/observableType";
import {
  enableDetection,
  disableDetection,
  updateDetectionExpiration,
} from "../../constants/observables";

type FILE = "file";
type URL = "url";
type IPV4 = "ipv4";

type knownObservables = FILE | URL | IPV4;

type PartialRecord<K extends keyof any, T> = Partial<Record<K, T>>;

export const commonObservableActions = [
  enableDetection,
  disableDetection,
  updateDetectionExpiration,
];

const ipv4SpecificObservableAction: observableActionCommand = {
  type: "command",
  label: "IPV4 Command",
  description: "Test command",
  icon: "pi pi=check",
  reloadPage: false,
  command: (obs: observableTreeRead) => {
    console.log(obs.uuid);
  },
};

export const observableMetadata: PartialRecord<
  knownObservables,
  observableTypeMetaData
> = {
  file: {
    style: { color: "red" },
  },
  ipv4: {
    actions: [{ items: [ipv4SpecificObservableAction], label: "Subheader" }],
    style: { color: "blue" },
  },
};
