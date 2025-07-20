/** @odoo-module **/

// Enhanced debug script to test JSON Editor loading
import { registry } from "@web/core/registry";

console.log("=== Enhanced JSON Editor Debug Info ===");
console.log("Registry fields:", registry.category("fields"));
console.log("Available field widgets:", Object.keys(registry.category("fields").content));

// Check if json_editor is registered
const jsonEditorWidget = registry.category("fields").get("json_editor", null);
console.log("JSON Editor Widget:", jsonEditorWidget);

if (jsonEditorWidget) {
    console.log("✅ JSON Editor widget is registered successfully");
    console.log("Supported types:", jsonEditorWidget.supportedFieldTypes);
    console.log("Props:", jsonEditorWidget.props);
    console.log("Component:", jsonEditorWidget.component);
    console.log("Component name:", jsonEditorWidget.name);
    console.log("Display name:", jsonEditorWidget.displayName);
    console.log("Template:", jsonEditorWidget.template);
    
    // Test if the component has necessary properties
    console.log("Has setup method:", typeof jsonEditorWidget.prototype?.setup === 'function');
    console.log("Is Component class:", jsonEditorWidget.prototype?.constructor?.name);
} else {
    console.error("❌ JSON Editor widget is NOT registered");
}

// Check registry structure
console.log("Registry content keys:", Object.keys(registry.category("fields").content));

// Check other field widgets for comparison
const textWidget = registry.category("fields").get("text", null);
if (textWidget) {
    console.log("📝 Text widget for comparison:");
    console.log("Text widget name:", textWidget.name);
    console.log("Text widget component:", textWidget.component);
    console.log("Text widget has component property:", !!textWidget.component);
}

console.log("=== End Enhanced Debug Info ===");
