/** @odoo-module */

import { one } from "@llm_thread/utils/compatibility";
import { registerPatch } from "@llm_thread/utils/compatibility";

registerPatch({
  name: "Messaging",
  fields: {
    llmChat: one("LLMChat", {
      default: {},
      isCausal: true,
    }),
  },
});
