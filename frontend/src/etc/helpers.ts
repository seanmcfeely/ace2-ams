import { useAlertDispositionStore } from "@/stores/alertDisposition";
import { useAlertQueueStore } from "@/stores/alertQueue";
import { useAlertToolStore } from "@/stores/alertTool";
import { useAlertToolInstanceStore } from "@/stores/alertToolInstance";
import { useAlertTypeStore } from "@/stores/alertType";
import { useEventPreventionToolStore } from "@/stores/eventPreventionTool";
import { useEventQueueStore } from "@/stores/eventQueue";
import { useEventRiskLevelStore } from "@/stores/eventRiskLevel";
import { useEventStatusStore } from "@/stores/eventStatus";
import { useEventTypeStore } from "@/stores/eventType";
import { useEventVectorStore } from "@/stores/eventVector";
import { useNodeDirectiveStore } from "@/stores/nodeDirective";
import { useObservableTypeStore } from "@/stores/observableType";
import { useUserStore } from "@/stores/user";

export const camelToSnakeCase = (str: string): string =>
  str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

export async function populateCommonStores(): Promise<void> {
  const alertDispositionStore = useAlertDispositionStore();
  const alertQueueStore = useAlertQueueStore();
  const alertTypeStore = useAlertTypeStore();
  const alertToolStore = useAlertToolStore();
  const alertToolInstanceStore = useAlertToolInstanceStore();
  const eventPreventionToolStore = useEventPreventionToolStore();
  const eventQueueStore = useEventQueueStore();
  const eventRiskLevelStore = useEventRiskLevelStore();
  const eventStatusStore = useEventStatusStore();
  const eventTypeStore = useEventTypeStore();
  const eventVectorStore = useEventVectorStore();
  const nodeDirectiveStore = useNodeDirectiveStore();
  const observableTypeStore = useObservableTypeStore();
  const userStore = useUserStore();

  await Promise.all([
    alertDispositionStore.readAll(),
    alertQueueStore.readAll(),
    alertTypeStore.readAll(),
    alertToolStore.readAll(),
    alertToolInstanceStore.readAll(),
    eventPreventionToolStore.readAll(),
    eventQueueStore.readAll(),
    eventRiskLevelStore.readAll(),
    eventStatusStore.readAll(),
    eventTypeStore.readAll(),
    eventVectorStore.readAll(),
    nodeDirectiveStore.readAll(),
    observableTypeStore.readAll(),
    userStore.readAll(),
  ]).catch((error) => {
    throw error;
  });
}

// https://stackoverflow.com/a/33928558
export function copyToClipboard(text: string) {
  if (
    document.queryCommandSupported &&
    document.queryCommandSupported("copy")
  ) {
    const textarea = document.createElement("textarea");
    textarea.textContent = text;
    textarea.style.position = "fixed"; // Prevent scrolling to bottom of page in Microsoft Edge.
    document.body.appendChild(textarea);
    textarea.select();
    try {
      return document.execCommand("copy"); // Security exception may be thrown by some browsers.
    } catch (ex) {
      console.warn("Copy to clipboard failed.", ex);
      return prompt("Copy to clipboard: Ctrl+C, Enter", text);
    } finally {
      document.body.removeChild(textarea);
    }
  }
}

// https://stackoverflow.com/questions/1353684/detecting-an-invalid-date-date-instance-in-javascript
export function isValidDate(d: unknown): boolean {
  return d instanceof Date && !isNaN(d.getTime());
}

export function isObject(o: unknown): boolean {
  return typeof o === "object" && o !== null;
}