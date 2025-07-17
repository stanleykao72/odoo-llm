/** @odoo-module */

import { useEffect, useRef } from "@odoo/owl";
import { Component } from "@odoo/owl";
import { Transition } from "@web/core/transition";
import { MinimalMessageList, registerMessagingComponent } from "@llm_thread/utils/compatibility";

export class LLMChatMessageList extends Component {
  setup() {
    super.setup();
    this.rootRef = useRef("root");
    // TODO check if we can do this also when chunks updates
    useEffect(
      () => {
        if (this.thread) {
          this._scrollToEnd();
        }
      },
      () => [this.thread, this.isStreaming]
    );
  }

  get thread() {
    return this.composerView.composer.thread;
  }

  get composerView() {
    return this.props.composerView;
  }

  get isStreaming() {
    return this.composerView.composer.isStreaming;
  }

  _scrollToEnd() {
    const scrollable = this.rootRef.el.closest(".o_LLMChatThread_content");
    if (scrollable) {
      const scrollHeight = scrollable.scrollHeight;
      const clientHeight = scrollable.clientHeight;
      const scrollTop = scrollHeight - clientHeight;
      scrollable.scrollTop = scrollTop;
    } else {
      // Fallback to original behavior
      const fallbackScrollable = this.rootRef.el;
      if (fallbackScrollable) {
        const scrollHeight = fallbackScrollable.scrollHeight;
        const clientHeight = fallbackScrollable.clientHeight;
        const scrollTop = scrollHeight - clientHeight;
        fallbackScrollable.scrollTop = scrollTop;
      }
    }
  }
}

LLMChatMessageList.components = { Transition };
LLMChatMessageList.props = { record: Object, composerView: Object };
LLMChatMessageList.template = "llm_thread.LLMChatMessageList";

registerMessagingComponent(LLMChatMessageList);
