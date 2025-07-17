
/** @odoo-module */

import { Component } from "@odoo/owl";
import { LLMChatSidebar } from "@llm_thread/components/llm_chat_sidebar/llm_chat_sidebar";
import { LLMChatThread } from "@llm_thread/components/llm_chat_thread/llm_chat_thread";

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

  /**
   * @returns {Boolean} Whether there's an active thread
   */
  get hasActiveThread() {
    return this.llmChatView.llmChat.activeThread !== null;
  }

  /**
   * @returns {Object} Active thread
   */
  get activeThread() {
    return this.llmChatView.llmChat.activeThread;
  }
}

LLMChat.props = { record: Object };
LLMChat.template = "llm_thread.LLMChat";
LLMChat.components = {
  LLMChatSidebar: LLMChatSidebar,
  LLMChatThread: LLMChatThread,
};
