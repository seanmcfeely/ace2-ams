import { queueRead } from '@/models/queue';
import { defineStore } from "pinia";

export const useCurrentUserSettingsStore = defineStore({
  id: "currentUserSettingsStore",

  state: () => ({
    preferredEventQueue: null as unknown as queueRead,
    preferredAlertQueue: null as unknown as queueRead,
  }),
});
