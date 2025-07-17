/** @odoo-module */

import { attr, many, one } from "@llm_thread/utils/compatibility";
import { registerModel } from "@llm_thread/utils/compatibility";

registerModel({
  name: "LLMModel",
  fields: {
    id: attr({
      identifying: true,
    }),
    name: attr({
      required: true,
    }),
    llmProvider: one("LLMProvider", {
      inverse: "llmModels",
    }),
    threads: many("Thread", {
      inverse: "llmModel",
    }),
    default: attr({
      default: false,
    }),
  },
});
