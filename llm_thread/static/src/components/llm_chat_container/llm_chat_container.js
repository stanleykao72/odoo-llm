/** @odoo-module */

import { Component, onWillDestroy } from "@odoo/owl";
import { getMessagingComponent, useModels } from "@llm_thread/utils/compatibility";
import { useService } from "@web/core/utils/hooks";

export class LLMChatContainer extends Component {
  setup() {
    useModels();
    super.setup();
    onWillDestroy(() => this._willDestroy());

    // Use service hook for messaging
    this.messagingService = useService("messaging");
    
    // Simplified initialization
    try {
      const action = this.props.action || this.props;
      const initActiveId =
        (action.context && action.context.active_id) ||
        (action.params && action.params.default_active_id) ||
        null;

      // Initialize LLM chat functionality
      this.initializeLLMChat(action, initActiveId);
    } catch (error) {
      console.warn("LLMChatContainer initialization warning:", error);
    }

    // Keep track of current instance to handle cleanup
    LLMChatContainer.currentInstance = this;
  }

  get messaging() {
    return this.messagingService || {};
  }

  initializeLLMChat(action, initActiveId) {
    // Simplified LLM chat initialization
    if (this.messaging.llmChat) {
      this.llmChat = this.messaging.llmChat;
      this.llmChat.initializeLLMChat(action, initActiveId);
    }
  }

  _willDestroy() {
    if (this.llmChat && LLMChatContainer.currentInstance === this) {
      this.llmChat.close();
    }
  }
}

LLMChatContainer.template = "llm_thread.LLMChatContainer";
LLMChatContainer.components = {
  LLMChat: getMessagingComponent("LLMChat"),
};
LLMChatContainer.props = ["*"];
