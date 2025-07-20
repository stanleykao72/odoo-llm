/** @odoo-module **/

// Debug script to test JSON Editor loading
import { registry } from "@web/core/registry";

console.log("=== JSON Editor Debug Info ===");
console.log("Registry fields:", registry.category("fields"));
console.log("Available field widgets:", Object.keys(registry.category("fields").content));

// Check if json_editor is registered
const jsonEditorWidget = registry.category("fields").get("json_editor", null);
console.log("JSON Editor Widget:", jsonEditorWidget);

if (jsonEditorWidget) {
    console.log("✅ JSON Editor widget is registered successfully");
    console.log("Supported types:", jsonEditorWidget.supportedFieldTypes);
    console.log("Props:", jsonEditorWidget.props);
} else {
    console.error("❌ JSON Editor widget is NOT registered");
}

console.log("=== End Debug Info ===");
