/** @odoo-module */

import { MinimalComposer } from "@llm_thread/utils/compatibility";
import { registerMessagingComponent } from "@llm_thread/utils/compatibility";

export class LLMChatComposerTextInput extends MinimalComposer {
  /**
   * @override
   */
  setup() {
    super.setup();
    this._composerView();
  }
  /**
   * Intercept input event before passing to composer view
   * @private
   * @param {InputEvent} ev
   */
  _onInput(ev) {
    // Call original handler
    this._composerView();
    this.composerView.onInputTextarea(ev);
  }

  _composerView() {
    return this.props.record;
  }

  /**
   * Intercept keydown event
   * @private
   * @param {KeyboardEvent} ev
   */
  _onKeydown(ev) {
    this.composerView.onKeydownTextareaForLLM(ev);
  }
}

LLMChatComposerTextInput.props = { record: Object };
LLMChatComposerTextInput.template = "llm_thread.LLMChatComposerTextInput";

registerMessagingComponent(LLMChatComposerTextInput);
