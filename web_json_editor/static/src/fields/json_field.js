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
        this.validateJSON(this.fieldValue);
    }
    
    validateJSON(value) {
        try {
            // Handle object values (already valid JSON)
            if (typeof value === 'object') {
                this.state.isValid = true;
                this.state.errorMessage = "";
                return true;
            }
            
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
        const value = this.fieldValue;
        if (!value) return "";
        
        // Handle both object and string values
        if (typeof value === 'object') {
            return JSON.stringify(value, null, 2);
        }
        
        try {
            const parsed = JSON.parse(value);
            return JSON.stringify(parsed, null, 2);
        } catch {
            return value;
        }
    }
    
    get fieldValue() {
        // Extract field value from record in Odoo 18.0
        if (this.props.record && this.props.name) {
            const value = this.props.record.data[this.props.name];
            return value;
        }
        return this.props.value;
    }
    
    get displayValue() {
        const value = this.fieldValue;
        
        if (this.props.readonly) {
            return this.formattedValue;
        }
        
        // Handle both object and string values for edit mode
        if (typeof value === 'object' && value !== null) {
            return JSON.stringify(value, null, 2);
        }
        
        return value || "";
    }
    
    onChange(ev) {
        const value = ev.target.value;
        this.validateJSON(value);
        
        // Try to parse and store as object if valid JSON, otherwise store as string
        try {
            if (value.trim() === "") {
                this.updateField(false); // Empty field should be false for JSON fields
            } else {
                const parsed = JSON.parse(value);
                this.updateField(parsed);
            }
        } catch {
            // Invalid JSON, store as string
            this.updateField(value);
        }
    }
    
    updateField(value) {
        if (this.props.update) {
            this.props.update(value);
        } else if (this.props.record && this.props.name) {
            // Fallback for direct record update
            this.props.record.update({ [this.props.name]: value });
        }
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
            const value = this.fieldValue;
            let parsed;
            if (typeof value === 'object') {
                parsed = value;
            } else {
                parsed = JSON.parse(value || "{}");
            }
            this.updateField(parsed); // Store as object, display will handle formatting
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