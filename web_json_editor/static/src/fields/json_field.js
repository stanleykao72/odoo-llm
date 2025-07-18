/** @odoo-module **/

import { Component, useState, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class JsonFieldWidget extends Component {
    static template = "web_json_editor.JsonFieldWidget";
    
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
        height: { type: String, optional: true },
    };
    
    static supportedTypes = ["text", "char", "json"];
    
    setup() {
        this.state = useState({
            isValid: true,
            errorMessage: ""
        });
        
        onWillUpdateProps((nextProps) => {
            if (nextProps.value !== this.props.value) {
                this.validateJSON(nextProps.value);
            }
        });
        
        // Validate initial value
        this.validateJSON(this.props.value);
    }
    
    validateJSON(value) {
        try {
            if (!value || value.trim() === "") {
                this.state.isValid = true;
                this.state.errorMessage = "";
                return true;
            }
            JSON.parse(value);
            this.state.isValid = true;
            this.state.errorMessage = "";
            return true;
        } catch (e) {
            this.state.isValid = false;
            this.state.errorMessage = `Invalid JSON: ${e.message}`;
            return false;
        }
    }
    
    get formattedValue() {
        if (!this.props.value) return "";
        try {
            const parsed = JSON.parse(this.props.value);
            return JSON.stringify(parsed, null, 2);
        } catch {
            return this.props.value;
        }
    }
    
    get displayValue() {
        if (this.props.readonly) {
            return this.formattedValue;
        }
        return this.props.value || "";
    }
    
    onChange(ev) {
        const value = ev.target.value;
        this.validateJSON(value);
        this.props.update(value);
    }
    
    onKeyDown(ev) {
        // Allow Tab key for indentation
        if (ev.key === 'Tab') {
            ev.preventDefault();
            const start = ev.target.selectionStart;
            const end = ev.target.selectionEnd;
            const value = ev.target.value;
            
            ev.target.value = value.substring(0, start) + '  ' + value.substring(end);
            ev.target.selectionStart = ev.target.selectionEnd = start + 2;
            
            this.onChange(ev);
        }
    }
    
    formatJSON() {
        try {
            const parsed = JSON.parse(this.props.value || "{}");
            const formatted = JSON.stringify(parsed, null, 2);
            this.props.update(formatted);
        } catch (e) {
            // Invalid JSON, don't format
        }
    }
}

// Register the widget
registry.category("fields").add("json_editor", {
    component: JsonFieldWidget,
    supportedTypes: ["text", "char", "json"],
});

// Also register as json_inline for backward compatibility
registry.category("fields").add("json_inline", {
    component: JsonFieldWidget,
    supportedTypes: ["text", "char", "json"],
});