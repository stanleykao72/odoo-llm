import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { loadJS, loadCSS } from "@web/core/assets";

/**
 * JSON Editor Field Component for Odoo 18.0
 * Uses dynamic loading of JSONEditor library with proper Owl lifecycle integration
 */
export class JsonEditorField extends Component {
    static template = "web_json_editor.JsonEditorField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };
    static supportedFieldTypes = ["text", "char", "json"];

    setup() {
        console.log('🚀 JsonEditorField.setup() called');
        console.log('Props in setup:', this.props);
        
        this.containerRef = useRef("container");
        this.textareaRef = useRef("textarea");
        this.editor = null;
        this.libraryLoaded = false;
        
        this.state = useState({
            isLoading: true,
            useRichEditor: false,
            isValid: true,
            errorMessage: '',
        });

        onMounted(async () => {
            console.log('🔄 JsonEditorField onMounted');
            await this.loadJSONEditor();
            
            // 延遲一小段時間確保 DOM 完全準備好
            setTimeout(async () => {
                console.log('📦 About to call initEditor (after DOM ready)');
                await this.initEditor();
                console.log('✅ initEditor completed');
            }, 50);
        });

        onWillUnmount(() => {
            if (this.editor && this.editor.destroy) {
                this.editor.destroy();
            }
        });
    }

    async loadJSONEditor() {
        console.log('📚 loadJSONEditor starting');
        try {
            // Load CSS first - 修正路徑
            await loadCSS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.css');
            console.log('✅ CSS loaded');
            
            // Load JS - 修正路徑
            await loadJS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.js');
            console.log('✅ JS loaded');
            
            // Check if JSONEditor is available
            if (window.JSONEditor) {
                this.libraryLoaded = true;
                this.state.useRichEditor = true;
                console.log('✅ JSONEditor library loaded successfully');
            } else {
                console.warn('⚠️ JSONEditor library not available, falling back to textarea');
                this.state.useRichEditor = false;
                this.libraryLoaded = false;
            }
        } catch (error) {
            console.error('❌ Failed to load JSONEditor library:', error);
            this.state.useRichEditor = false;
        } finally {
            this.state.isLoading = false;
            console.log('📚 loadJSONEditor completed. isLoading:', this.state.isLoading, 'useRichEditor:', this.state.useRichEditor);
        }
    }

    async initEditor() {
        console.log('🔧 initEditor called');
        console.log('useRichEditor:', this.state.useRichEditor);
        console.log('libraryLoaded:', this.libraryLoaded);
        console.log('containerRef.el:', this.containerRef.el);
        console.log('textareaRef.el:', this.textareaRef.el);
        
        if (this.state.useRichEditor && this.libraryLoaded) {
            // 等待容器元素準備好，最多重試 10 次
            let retries = 0;
            while (!this.containerRef.el && retries < 10) {
                console.log(`⏳ Waiting for container element, retry ${retries + 1}/10`);
                await new Promise(resolve => setTimeout(resolve, 50));
                retries++;
            }
            
            if (this.containerRef.el) {
                console.log('✅ Container element found, initializing rich editor');
                await this.initRichEditor();
            } else {
                console.warn('❌ Container element not found after retries, falling back to textarea');
                this.state.useRichEditor = false;
                await this.initSimpleEditor();
            }
        } else {
            if (!this.textareaRef.el) {
                // 等待 textarea 元素準備好
                let retries = 0;
                while (!this.textareaRef.el && retries < 10) {
                    console.log(`⏳ Waiting for textarea element, retry ${retries + 1}/10`);
                    await new Promise(resolve => setTimeout(resolve, 50));
                    retries++;
                }
            }
            
            if (this.textareaRef.el) {
                console.log('✅ Textarea element found, initializing simple editor');
                await this.initSimpleEditor();
            } else {
                console.error('❌ No editor element available for initialization');
                return;
            }
        }
    }

    async initRichEditor() {
        console.log('🎨 initRichEditor called');
        console.log('Container element:', this.containerRef.el);
        console.log('Current value:', this.props.record.data[this.props.name]);
        
        if (!this.containerRef.el) {
            console.error('❌ Container element not found for rich editor');
            return;
        }
        
        try {
            const options = {
                mode: 'code',  // 改為預設代碼模式
                modes: ['code', 'tree', 'view'],  // 支援三種模式切換
                search: true,
                history: true,
                onChange: () => {
                    if (this.editor && !this.props.readonly) {
                        try {
                            const value = this.editor.get();
                            const jsonString = JSON.stringify(value);
                            this.props.record.update({ [this.props.name]: jsonString });
                            this.state.isValid = true;
                            this.state.errorMessage = '';
                        } catch (error) {
                            console.error('❌ Error updating value:', error);
                            this.state.isValid = false;
                            this.state.errorMessage = error.message;
                        }
                    }
                }
            };
            
            // 創建 JSONEditor 實例
            this.editor = new window.JSONEditor(this.containerRef.el, options);
            console.log('✅ JSONEditor instance created:', this.editor);
            
            // 設置初始值
            const currentValue = this.formatValue();
            console.log('Setting initial value:', currentValue);
            
            if (currentValue) {
                try {
                    const parsed = JSON.parse(currentValue);
                    this.editor.set(parsed);
                    console.log('✅ Initial value set successfully');
                } catch (error) {
                    console.warn('⚠️ Failed to parse initial value, setting as text:', error);
                    this.editor.setText(currentValue);
                }
            }
            
        } catch (error) {
            console.error('❌ Error initializing rich editor:', error);
            this.state.useRichEditor = false;
            await this.initSimpleEditor();
        }
    }

    async initSimpleEditor() {
        console.log('📝 initSimpleEditor called');
        console.log('Textarea element:', this.textareaRef.el);
        
        if (!this.textareaRef.el) {
            console.error('❌ Textarea element not found');
            return;
        }
        
        // 設置初始值
        const currentValue = this.formatValue();
        console.log('Setting textarea value:', currentValue);
        this.textareaRef.el.value = currentValue || '';
        
        // 添加事件監聽器
        if (!this.props.readonly) {
            this.textareaRef.el.addEventListener('input', (event) => {
                const value = event.target.value;
                try {
                    if (value.trim()) {
                        JSON.parse(value); // 驗證 JSON
                    }
                    this.state.isValid = true;
                    this.state.errorMessage = '';
                    this.props.record.update({ [this.props.name]: value });
                } catch (error) {
                    this.state.isValid = false;
                    this.state.errorMessage = `Invalid JSON: ${error.message}`;
                }
            });
        }
        
        console.log('✅ Simple editor initialized');
    }

    formatValue() {
        console.log('🔧 formatValue called');
        const value = this.props.record.data[this.props.name];
        console.log('Raw value:', value, 'Type:', typeof value);
        
        if (!value) {
            console.log('📝 No value, returning empty string');
            return '';
        }
        
        try {
            if (typeof value === 'string') {
                // 嘗試解析並重新格式化
                const parsed = JSON.parse(value);
                const formatted = JSON.stringify(parsed, null, 2);
                console.log('✅ Formatted JSON string:', formatted);
                return formatted;
            } else {
                // 如果是物件，直接格式化
                const formatted = JSON.stringify(value, null, 2);
                console.log('✅ Formatted object:', formatted);
                return formatted;
            }
        } catch (error) {
            console.warn('⚠️ formatValue error, returning raw value:', error);
            return String(value);
        }
    }

    formatJSON() {
        if (this.textareaRef.el) {
            try {
                const value = this.textareaRef.el.value;
                const parsed = JSON.parse(value);
                const formatted = JSON.stringify(parsed, null, 2);
                this.textareaRef.el.value = formatted;
                this.props.record.update({ [this.props.name]: formatted });
                this.state.isValid = true;
                this.state.errorMessage = '';
            } catch (error) {
                this.state.isValid = false;
                this.state.errorMessage = `Invalid JSON: ${error.message}`;
            }
        }
    }

    minifyJSON() {
        if (this.textareaRef.el) {
            try {
                const value = this.textareaRef.el.value;
                const parsed = JSON.parse(value);
                const minified = JSON.stringify(parsed);
                this.textareaRef.el.value = minified;
                this.props.record.update({ [this.props.name]: minified });
                this.state.isValid = true;
                this.state.errorMessage = '';
            } catch (error) {
                this.state.isValid = false;
                this.state.errorMessage = `Invalid JSON: ${error.message}`;
            }
        }
    }
}

// Register the component
JsonEditorField.displayName = "JsonEditorField";
JsonEditorField.component = JsonEditorField;

registry.category("fields").add("json_editor", JsonEditorField);

console.log('✅ JsonEditorField successfully registered');
console.log('Component name:', JsonEditorField.displayName);
console.log('Component:', JsonEditorField);