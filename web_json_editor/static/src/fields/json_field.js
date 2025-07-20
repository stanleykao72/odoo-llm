import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { loadJS, loadCSS } from "@web/core/assets";

/**
 * JSON Editor Field Component for Odoo 18.0
 * Simplified version matching Odoo 16.0 structure
 */
export class JsonEditorField extends Component {
    static template = "web_json_editor.JsonEditorField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };
    static supportedFieldTypes = ["text", "char", "json"];

    setup() {
        this.containerRef = useRef("container");
        this.editor = null;

        onMounted(() => this.initEditor());
        onWillUnmount(() => this.destroyEditor());
    }

    async initEditor() {
        if (!this.containerRef.el || this.props.readonly) return;

        try {
            // Load JSONEditor library
            await loadCSS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.css');
            await loadJS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.js');

            // Initialize JSONEditor with options  
            const options = {
                mode: 'code',
                modes: ['code', 'tree', 'view'],
                search: true,
                history: true,
                onChange: () => {
                    if (this.editor && !this.props.readonly) {
                        try {
                            const value = this.editor.get();
                            const jsonString = JSON.stringify(value);
                            this.props.record.update({ [this.props.name]: jsonString });
                        } catch (error) {
                            console.error('Error updating JSON value:', error);
                        }
                    }
                }
            };

            // Create editor instance
            this.editor = new window.JSONEditor(this.containerRef.el, options);

            // Set initial value
            const currentValue = this.formatValue();
            if (currentValue) {
                try {
                    const parsed = JSON.parse(currentValue);
                    this.editor.set(parsed);
                } catch (error) {
                    console.warn('Failed to parse initial value:', error);
                    this.editor.setText(currentValue);
                }
            }
        } catch (error) {
            console.error('Failed to initialize JSON editor:', error);
        }
    }

    destroyEditor() {
        if (this.editor && this.editor.destroy) {
            this.editor.destroy();
            this.editor = null;
        }
    }

    formatValue() {
        const value = this.props.record.data[this.props.name];
        
        if (!value) {
            return '';
        }
        
        try {
            if (typeof value === 'string') {
                // 嘗試解析並重新格式化
                const parsed = JSON.parse(value);
                return JSON.stringify(parsed, null, 2);
            } else {
                // 如果是物件，直接格式化
                return JSON.stringify(value, null, 2);
            }
        } catch (error) {
            return String(value);
        }
    }
}

/**
 * JSON Inline Field Component for Odoo 18.0
 * A simplified version of JSON editor that only shows code mode
 */
export class JsonInlineField extends Component {
    static template = "web_json_editor.JsonInlineField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };
    static supportedFieldTypes = ["text", "char", "json"];

    setup() {
        this.containerRef = useRef("container");
        this.editor = null;

        onMounted(() => this.initEditor());
        onWillUnmount(() => this.destroyEditor());
    }

    async initEditor() {
        if (!this.containerRef.el || this.props.readonly) return;

        try {
            // Load JSONEditor library
            await loadCSS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.css');
            await loadJS('/web_json_editor/static/lib/jsoneditor/jsoneditor.min.js');

            // Initialize JSONEditor with inline options (code mode only)
            const options = {
                mode: 'code',
                modes: ['code'], // Only code mode for inline version
                search: false, // Disable search for compact view
                history: false, // Disable history for compact view
                navigationBar: false, // Disable navigation bar
                statusBar: false, // Disable status bar
                onChange: () => {
                    if (this.editor && !this.props.readonly) {
                        try {
                            const value = this.editor.get();
                            const jsonString = JSON.stringify(value);
                            this.props.record.update({ [this.props.name]: jsonString });
                        } catch (error) {
                            console.error('Error updating JSON value:', error);
                        }
                    }
                }
            };

            // Create editor instance
            this.editor = new window.JSONEditor(this.containerRef.el, options);

            // Set initial value
            const currentValue = this.formatValue();
            if (currentValue) {
                try {
                    const parsed = JSON.parse(currentValue);
                    this.editor.set(parsed);
                } catch (error) {
                    console.warn('Failed to parse initial value:', error);
                    this.editor.setText(currentValue);
                }
            }
        } catch (error) {
            console.error('Failed to initialize JSON inline editor:', error);
        }
    }

    destroyEditor() {
        if (this.editor && this.editor.destroy) {
            this.editor.destroy();
            this.editor = null;
        }
    }

    formatValue() {
        const value = this.props.record.data[this.props.name];
        
        if (!value) {
            return '';
        }
        
        try {
            if (typeof value === 'string') {
                // 嘗試解析並重新格式化
                const parsed = JSON.parse(value);
                return JSON.stringify(parsed, null, 2);
            } else {
                // 如果是物件，直接格式化
                return JSON.stringify(value, null, 2);
            }
        } catch (error) {
            return String(value);
        }
    }
}

// Register the component
JsonEditorField.displayName = "JsonEditorField";
JsonEditorField.component = JsonEditorField;
JsonInlineField.displayName = "JsonInlineField";
JsonInlineField.component = JsonInlineField;

registry.category("fields").add("json_editor", JsonEditorField);
registry.category("fields").add("json_inline", JsonInlineField);
