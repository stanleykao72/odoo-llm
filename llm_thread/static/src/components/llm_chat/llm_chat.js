
/** @odoo-module */

import { Component } from "@odoo/owl";
import { registerMessagingComponent } from "@mail/utils/messaging_component";
export class LLMChat extends Component {
  // --------------------------------------------------------------------------
  // Public
  // --------------------------------------------------------------------------

  /**
   * @returns {LLMChatView}
   */
  get llmChatView() {
    return this.props.record;
  }
}

LLMChat.props = { record: Object };
LLMChat.template = "llm_thread.LLMChat";

registerMessagingComponent(LLMChat);
