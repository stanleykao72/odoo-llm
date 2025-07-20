import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { loadJS, loadCSS } from "@web/core/assets";

/**
 * JSON Editor Field Component for Odoo 18.0
 * Uses dynamic loading of JSONEditor library with proper Owl lifecycle integration
 */
export class JsonEditorField extends Component {
    setup() {
        console.log("🚀 JsonEditorField.setup() called");
        console.log("Props in setup:", this.props);
        
        this.containerRef = useRef("container");
        this.textareaRef = useRef("textarea");
        this.jsonEditor = null;
        this.libraryLoaded = false;
        
        this.state = useState({
            isLoading: true,
            useRichEditor: false,
            isValid: true,
            errorMessage: "",
        });

        onMounted(async () => {
            console.log("🔄 JsonEditorField onMounted");
            await this.loadJSONEditor();
            this.initEditor();
        });

        onWillUnmount(() => {
            console.log("🗑️ JsonEditorField onWillUnmount");
            if (this.jsonEditor) {
                this.jsonEditor.destroy();
                this.jsonEditor = null;
            }
        });
    }

    /**
     * Dynamically load JSONEditor library
     */
    async loadJSONEditor() {
        try {
            // Load CSS first
            await loadCSS("/web_json_editor/static/lib/jsoneditor/jsoneditor.min.css");
            
            // Then load JavaScript
            await loadJS("/web_json_editor/static/lib/jsoneditor/jsoneditor.min.js");
            
            // Verify the library is available
            if (typeof window.JSONEditor !== 'undefined') {
                this.libraryLoaded = true;
                this.state.useRichEditor = true;
                console.log("JSONEditor library loaded successfully");
            } else {
                throw new Error("JSONEditor not available after loading");
            }
        } catch (error) {
            console.warn("Failed to load JSONEditor library, falling back to textarea:", error);
            this.libraryLoaded = false;
            this.state.useRichEditor = false;
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Initialize the appropriate editor
     */
    initEditor() {
        console.log("🔧 initEditor called");
        console.log("useRichEditor:", this.state.useRichEditor);
        console.log("libraryLoaded:", this.libraryLoaded);
        console.log("containerRef.el:", this.containerRef.el);
        console.log("textareaRef.el:", this.textareaRef.el);
        
        if (this.state.useRichEditor && this.libraryLoaded && this.containerRef.el) {
            console.log("Initializing rich editor");
            this.initRichEditor();
        } else if (this.textareaRef.el) {
            console.log("Initializing simple editor");
            this.initSimpleEditor();
        } else {
            console.warn("No editor element available for initialization");
        }
    }

    /**
     * Initialize rich JSONEditor
     */
    initRichEditor() {
        try {
            console.log("🎨 initRichEditor starting");
            const options = {
                mode: 'code',
                theme: 'ace/theme/textmate',
                onChangeText: (text) => {
                    if (!this.props.readonly) {
                        this.updateValue(text);
                    }
                },
                onError: (error) => {
                    console.warn("JSONEditor validation error:", error);
                    this.state.isValid = false;
                    this.state.errorMessage = error.toString();
                }
            };

            console.log("Creating JSONEditor with options:", options);
            this.jsonEditor = new window.JSONEditor(this.containerRef.el, options);
            
            // Set initial value
            const value = this.formatValue();
            console.log("Setting initial value:", value);
            try {
                this.jsonEditor.setText(value);
                console.log("✅ Initial value set successfully");
            } catch (error) {
                console.warn("Error setting initial value:", error);
                this.jsonEditor.setText("{}");
            }

            // Make readonly if needed
            if (this.props.readonly) {
                console.log("Setting editor to readonly mode");
                this.jsonEditor.setMode('view');
            }

        } catch (error) {
            console.error("❌ Error initializing rich editor:", error);
            // Fallback to simple editor
            this.state.useRichEditor = false;
            this.initSimpleEditor();
        }
    }

    /**
     * Initialize simple textarea editor (fallback)
     */
    initSimpleEditor() {
        if (!this.textareaRef.el) return;

        // Set initial value
        this.textareaRef.el.value = this.formatValue();
        
        // Add event listeners
        this.textareaRef.el.addEventListener('input', this.onTextChange.bind(this));
        this.textareaRef.el.addEventListener('blur', this.validateJSON.bind(this));
    }

    /**
     * Format the value for display
     */
    formatValue() {
        try {
            console.log("📊 JsonEditorField.formatValue called");
            console.log("Props:", this.props);
            console.log("Props.value:", this.props.value);
            console.log("Props.record:", this.props.record);
            console.log("Field info:", this.props.record?.fields?.[this.props.name]);
            
            const value = this.props.value;
            
            // Handle null, undefined, or empty values
            if (value === null || value === undefined || value === "") {
                console.log("Value is empty, returning default {}");
                return "{}";
            }

            // Handle string values
            if (typeof value === "string") {
                if (value.trim() === "") {
                    console.log("Value is empty string, returning default {}");
                    return "{}";
                }
                try {
                    // Try to parse and reformat
                    const parsed = JSON.parse(value);
                    const formatted = JSON.stringify(parsed, null, 2);
                    console.log("Successfully parsed and formatted string value");
                    return formatted;
                } catch (e) {
                    // Return as-is if not valid JSON, but ensure it's a string
                    console.log("Failed to parse JSON, returning original string:", e.message);
                    return value;
                }
            }

            // Handle object values (already parsed JSON)
            if (typeof value === "object") {
                const formatted = JSON.stringify(value, null, 2);
                console.log("Successfully formatted object value");
                return formatted;
            }

            // For other types, try to stringify
            const formatted = JSON.stringify(value, null, 2);
            console.log("Successfully stringified other type value");
            return formatted;
        } catch (error) {
            console.error("❌ Error in formatValue:", error, "Value:", this.props.value);
            return "{}";
        }
    }

    /**
     * Update field value
     */
    updateValue(text) {
        if (this.props.readonly) return;

        try {
            const parsed = JSON.parse(text);
            
            // Handle different field types
            if (this.props.record.fields[this.props.name].type === "json") {
                // For JSON fields, pass the object directly
                this.props.update(parsed);
            } else {
                // For text and char fields, convert to a JSON string
                this.props.update(text);
            }
            
            this.state.isValid = true;
            this.state.errorMessage = "";
        } catch (e) {
            // For invalid JSON, still update with the text value for text/char fields
            if (this.props.record.fields[this.props.name].type !== "json") {
                this.props.update(text);
            }
            
            this.state.isValid = false;
            this.state.errorMessage = `Invalid JSON: ${e.message}`;
        }
    }

    /**
     * Handle text changes in simple editor
     */
    onTextChange(event) {
        const text = event.target.value;
        this.validateJSON();
        this.updateValue(text);
    }

    /**
     * Validate JSON syntax
     */
    validateJSON() {
        if (!this.textareaRef.el) return;
        
        const text = this.textareaRef.el.value;
        
        try {
            JSON.parse(text);
            this.state.isValid = true;
            this.state.errorMessage = "";
            this.textareaRef.el.classList.remove('is-invalid');
        } catch (e) {
            this.state.isValid = false;
            this.state.errorMessage = `Invalid JSON: ${e.message}`;
            this.textareaRef.el.classList.add('is-invalid');
        }
    }

    /**
     * Format JSON (prettify) - for simple editor
     */
    formatJSON() {
        if (!this.textareaRef.el || this.props.readonly) return;
        
        try {
            const parsed = JSON.parse(this.textareaRef.el.value);
            const formatted = JSON.stringify(parsed, null, 2);
            this.textareaRef.el.value = formatted;
            this.onTextChange({ target: this.textareaRef.el });
        } catch (e) {
            // Show error but don't change the text
            this.state.isValid = false;
            this.state.errorMessage = `Cannot format: ${e.message}`;
        }
    }

    /**
     * Minify JSON (compact) - for simple editor
     */
    minifyJSON() {
        if (!this.textareaRef.el || this.props.readonly) return;
        
        try {
            const parsed = JSON.parse(this.textareaRef.el.value);
            const minified = JSON.stringify(parsed);
            this.textareaRef.el.value = minified;
            this.onTextChange({ target: this.textareaRef.el });
        } catch (e) {
            // Show error but don't change the text
            this.state.isValid = false;
            this.state.errorMessage = `Cannot minify: ${e.message}`;
        }
    }
}

JsonEditorField.template = "web_json_editor.JsonEditorField";

// Enhanced props definition for Odoo 18.0 compatibility
JsonEditorField.props = {
    ...standardFieldProps,
    readonly: { type: Boolean, optional: true },
    nodeOptions: { type: Object, optional: true },
};

// Critical: Define the component attribute for proper field recognition
JsonEditorField.component = JsonEditorField;

// Define supported field types for proper widget recognition
JsonEditorField.supportedTypes = ["text", "char", "json"];

// Extract to static property for better Owl compatibility
JsonEditorField.supportedFieldTypes = ["text", "char", "json"];

// Additional Odoo 18.0 compatibility properties
JsonEditorField.displayName = "JsonEditorField";
JsonEditorField.description = "JSON Editor Field Widget";

// Register the field widget with proper error handling
try {
    registry.category("fields").add("json_editor", JsonEditorField);
    console.log("✅ JsonEditorField successfully registered");
    console.log("Component name:", JsonEditorField.name);
    console.log("Component:", JsonEditorField.component);
} catch (error) {
    console.error("❌ Failed to register JsonEditorField:", error);
}