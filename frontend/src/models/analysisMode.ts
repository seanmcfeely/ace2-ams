import { genericObjectRead } from "./base";

import { analysisModuleTypeRead } from "./analysisModuleType";

export interface analysisModeRead extends genericObjectRead {
  analysisModuleTypes: analysisModuleTypeRead[];
}
