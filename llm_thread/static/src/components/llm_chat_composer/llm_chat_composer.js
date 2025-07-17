
/** @odoo-module */

import { Component } from "@odoo/owl";
import { registerMessagingComponent } from "@llm_thread/utils/compatibility";
import { useComponentToModel } from "@llm_thread/utils/compatibility";

export class LLMChatComposer extends Component {
  /**
   * @override
   */
  setup() {
    super.setup();
    useComponentToModel({ fieldName: "component" });
  }

  /**
   * @returns {ComposerView}
   */
  get composerView() {
    return this.props.record;
  }

  /**
   * @returns {Boolean}
   */
  get isDisabled() {
    // Read the computed disabled state from the model.
    return this.composerView.composer.isSendDisabled;
  }

  get isStreaming() {
    return this.composerView.composer.isStreaming;
  }

  // --------------------------------------------------------------------------
  // Private
  // --------------------------------------------------------------------------

  /**
   * Intercept send button click
   * @private
   */
  _onClickSend() {
    if (this.isDisabled) {
      return;
    }

    this.composerView.composer.postUserMessageForLLM();
  }

  /**
   * Handles click on the stop button.
   *
   * @private
   */
  _onClickStop() {
    this.composerView.composer.stopLLMThreadLoop();
  }
}

LLMChatComposer.props = { record: Object };
LLMChatComposer.template = "llm_thread.LLMChatComposer";

registerMessagingComponent(LLMChatComposer);
