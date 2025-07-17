
/** @odoo-module */

import { Component } from "@odoo/owl";

export class LLMChatSidebar extends Component {
  setup() {
    super.setup();
  }

  /**
   * @returns {LLMChatView}
   */
  get llmChatView() {
    return this.props.record;
  }

  /**
   * @returns {Array} List of threads
   */
  get threads() {
    return this.llmChatView.llmChat.threads || [];
  }

  /**
   * @returns {Object} Active thread
   */
  get activeThread() {
    return this.llmChatView.llmChat.activeThread;
  }

  /**
   * Handle new chat button click
   */
  async _onClickNewChat() {
    console.log("New Chat button clicked!");
    try {
      await this.llmChatView.llmChat.createNewThread();
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  }

  /**
   * Handle thread selection
   * @param {Event} event
   */
  _onClickThread(event) {
    const threadId = parseInt(event.currentTarget.dataset.threadId);
    if (threadId) {
      this.llmChatView.llmChat.selectThread(threadId);
    }
  }

  /**
   * Handle backdrop click to close sidebar on mobile
   */
  _onBackdropClick() {
    // Handle mobile responsive behavior if needed
    console.log("Backdrop clicked");
  }

  /**
   * Format thread display name
   * @param {Object} thread
   * @returns {String}
   */
  getThreadDisplayName(thread) {
    if (!thread || !thread.name) {
      return "Untitled Chat";
    }
    return thread.name.length > 25 ? thread.name.substring(0, 25) + "..." : thread.name;
  }

  /**
   * Format thread date
   * @param {Object} thread
   * @returns {String}
   */
  getThreadDate(thread) {
    if (!thread || !thread.write_date) {
      return "";
    }
    
    const date = new Date(thread.write_date);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return "Today";
    } else if (diffDays === 2) {
      return "Yesterday";
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  /**
   * Check if thread is active
   * @param {Object} thread
   * @returns {Boolean}
   */
  isThreadActive(thread) {
    return this.activeThread && this.activeThread.id === thread.id;
  }
}

LLMChatSidebar.props = { record: Object };
LLMChatSidebar.template = "llm_thread.LLMChatSidebar";
