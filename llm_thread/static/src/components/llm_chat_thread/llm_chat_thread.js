
/** @odoo-module */

import { Component } from "@odoo/owl";
import { registerMessagingComponent } from "@mail/utils/messaging_component";

export class LLMChatThread extends Component {
  get threadView() {
    return this.props.threadView;
  }

  /**
   * @returns {Thread}
   */
  get thread() {
    return this.props.record;
  }

  /**
   * @returns {Message[]}
   */
  get messages() {
    // Use ThreadCache's orderedMessages
    return this.thread.cache?.orderedMessages || [];
  }
}

LLMChatThread.props = {
  record: Object,
  threadView: Object,
};
LLMChatThread.template = "llm_thread.LLMChatThread";

registerMessagingComponent(LLMChatThread);
