/** @odoo-module */

import { Component, onWillDestroy, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { LLMChat } from "@llm_thread/components/llm_chat/llm_chat";

export class LLMChatContainer extends Component {
  setup() {
    super.setup();
    onWillDestroy(() => this._willDestroy());

    // Use Odoo 18.0 service architecture
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.notificationService = useService("notification");
    // Get current user info from session
    this.userId = this.env.services.user?.userId || this.env.session?.uid || 1;

    // Initialize state using Odoo 18.0 patterns
    this.state = useState({
      isInitialized: false,
      threads: [],
      activeThread: null,
      llmModels: [],
      tools: [],
      isLoading: true,
      error: null
    });

    // Initialize LLM chat functionality
    this.initializeLLMChat();
  }

  get llmChatView() {
    return {
      id: 'llm_chat_view',
      llmChat: {
        activeThread: this.state.activeThread,
        threads: this.state.threads,
        llmModels: this.state.llmModels,
        tools: this.state.tools,
        createNewThread: this.createNewThread.bind(this),
        selectThread: this.selectThread.bind(this),
        loadThreads: this.loadThreads.bind(this),
        loadLLMModels: this.loadLLMModels.bind(this),
        loadTools: this.loadTools.bind(this)
      },
      threadView: {
        id: 'thread_view'
      }
    };
  }

  get messaging() {
    return {
      llmChat: {
        llmChatView: this.llmChatView
      },
      isInitialized: this.state.isInitialized
    };
  }

  async initializeLLMChat() {
    try {
      this.state.isLoading = true;
      this.state.error = null;

      // Get action context
      const action = this.props.action || this.props;
      const initActiveId =
        (action.context && action.context.active_id) ||
        (action.params && action.params.default_active_id) ||
        null;

      console.log("Initializing LLM chat with action:", action);

      // Load essential data
      await Promise.all([
        this.loadLLMModels(),
        this.loadThreads(),
        this.loadTools()
      ]);

      // Handle initial thread selection
      if (initActiveId && this.state.threads.length > 0) {
        const thread = this.state.threads.find(t => t.id === initActiveId);
        if (thread) {
          this.state.activeThread = thread;
        }
      }

      this.state.isInitialized = true;
      this.state.isLoading = false;
    } catch (error) {
      console.error("Failed to initialize LLM chat:", error);
      this.state.error = error.message || "Failed to initialize chat";
      this.state.isLoading = false;
    }
  }

  async loadThreads() {
    try {
      const result = await this.orm.searchRead(
        "llm.thread",
        [["create_uid", "=", this.userId]],
        ["name", "id", "model_id", "provider_id", "write_date", "create_date"],
        {
          order: "write_date desc"
        }
      );

      this.state.threads = result.map(thread => ({
        id: thread.id,
        name: thread.name,
        model_id: thread.model_id,
        provider_id: thread.provider_id,
        write_date: thread.write_date,
        create_date: thread.create_date
      }));
    } catch (error) {
      console.error("Failed to load threads:", error);
      this.state.threads = [];
    }
  }

  async loadLLMModels() {
    try {
      const result = await this.orm.searchRead(
        "llm.model",
        [],
        ["name", "id", "provider_id", "default"]
      );

      this.state.llmModels = result.map(model => ({
        id: model.id,
        name: model.name,
        provider_id: model.provider_id,
        default: model.default
      }));
    } catch (error) {
      console.error("Failed to load LLM models:", error);
      this.state.llmModels = [];
    }
  }

  async loadTools() {
    try {
      const result = await this.orm.searchRead(
        "llm.tool",
        [["active", "=", true]],
        ["name", "id"]
      );

      this.state.tools = result.map(tool => ({
        id: tool.id,
        name: tool.name
      }));
    } catch (error) {
      console.error("Failed to load tools:", error);
      this.state.tools = [];
    }
  }

  async createNewThread() {
    try {
      if (this.state.llmModels.length === 0) {
        this.notificationService.add(
          "No LLM models available. Please configure a model first.",
          { type: "warning" }
        );
        return;
      }

      const defaultModel = this.state.llmModels.find(m => m.default) || this.state.llmModels[0];
      
      const threadData = {
        name: `New Chat ${new Date().toLocaleString()}`,
        model_id: defaultModel.id,
        provider_id: Array.isArray(defaultModel.provider_id) ? defaultModel.provider_id[0] : defaultModel.provider_id
      };

      const threadId = await this.orm.create("llm.thread", [threadData]);

      // Reload threads to get the new thread
      await this.loadThreads();
      
      // Select the new thread
      const newThread = this.state.threads.find(t => t.id === threadId);
      if (newThread) {
        this.state.activeThread = newThread;
      }

      this.notificationService.add(
        "New chat created successfully",
        { type: "success" }
      );
    } catch (error) {
      console.error("Failed to create new thread:", error);
      this.notificationService.add(
        "Failed to create new chat",
        { type: "danger" }
      );
    }
  }

  selectThread(threadId) {
    const thread = this.state.threads.find(t => t.id === threadId);
    if (thread) {
      this.state.activeThread = thread;
    }
  }

  _willDestroy() {
    // Clean up any subscriptions or timers if needed
    console.log("LLMChatContainer destroyed");
  }
}

LLMChatContainer.template = "llm_thread.LLMChatContainer";
LLMChatContainer.components = {
  LLMChat: LLMChat,
};
LLMChatContainer.props = ["*"];
