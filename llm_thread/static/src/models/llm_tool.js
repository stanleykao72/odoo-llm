/** @odoo-module */

import { attr } from "@llm_thread/utils/compatibility";
import { registerModel } from "@llm_thread/utils/compatibility";

registerModel({
  name: "LLMTool",
  fields: {
    id: attr({
      identifying: true,
    }),
    name: attr({
      required: true,
    }),
  },
});
