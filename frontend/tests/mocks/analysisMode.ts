import { analysisModeRead } from "@/models/analysisMode";

export const analysisModeReadFactory = ({
  analysisModuleTypes = [],
  description = null,
  value = "defaultMode",
  uuid = "e77f200e-93c9-4db8-b8b9-a0daddae1f0d",
}: Partial<analysisModeRead> = {}): analysisModeRead => ({
  analysisModuleTypes: analysisModuleTypes,
  description: description,
  value: value,
  uuid: uuid,
});
