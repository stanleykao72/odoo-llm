/** @odoo-module */

import { LLMChatContainer } from "@llm_thread/components/llm_chat_container/llm_chat_container";
import { registry } from "@web/core/registry";

// Define the client action function
function llmChatClientAction(env, action) {
    return {
        Component: LLMChatContainer,
        props: {
            action: action,
            actionId: action.id,
            className: action.context?.className || "",
            globalState: action.context?.globalState || {},
        },
    };
}

// Register the client action
registry
  .category("actions")
  .add("llm_thread.chat_client_action", llmChatClientAction);
