/** @odoo-module */

import { attr, many } from "@llm_thread/utils/compatibility";
import { registerModel } from "@llm_thread/utils/compatibility";

registerModel({
  name: "LLMProvider",
  fields: {
    id: attr({
      identifying: true,
    }),
    name: attr({
      required: true,
    }),
    llmModels: many("LLMModel", {
      inverse: "llmProvider",
    }),
  },
});
