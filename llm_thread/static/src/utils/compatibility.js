/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

// Compatibility layer for Odoo 18.0 migration
// This provides minimal replacements for removed mail module functionality

// Hook replacements
export function useModels() {
    // Simplified implementation that returns a basic store-like object
    const messaging = useService("messaging");
    return messaging || {};
}

export function useComponentToModel() {
    // Minimal implementation for compatibility
    return { 
        fieldName: '', 
        modelName: '', 
        propNameAsRecordLocalId: '' 
    };
}

export function useRefToModel() {
    // Minimal implementation for compatibility
    return {};
}

// Component registration replacement
export function registerMessagingComponent(name, component) {
    // Try to register in available registries
    try {
        registry.category("discuss.component").add(name, component);
    } catch (e) {
        // Fallback to components registry
        registry.category("components").add(name, component);
    }
}

export function getMessagingComponent(name) {
    // Try to get component from available registries
    try {
        return registry.category("discuss.component").get(name);
    } catch (e) {
        try {
            return registry.category("components").get(name);
        } catch (e2) {
            // Return a minimal component as fallback
            return Component;
        }
    }
}

// Model system replacements
export function registerModel(modelName, modelClass) {
    // Minimal implementation - just register in a basic registry
    if (!window.llmModels) {
        window.llmModels = {};
    }
    window.llmModels[modelName] = modelClass;
}

export function registerPatch(modelName, patchData) {
    // Minimal implementation for patches
    if (!window.llmPatches) {
        window.llmPatches = {};
    }
    window.llmPatches[modelName] = patchData;
}

// Field definitions (simplified)
export function attr(config = {}) {
    return { type: 'attr', ...config };
}

export function one(relationName, config = {}) {
    return { type: 'one', relation: relationName, ...config };
}

export function many(relationName, config = {}) {
    return { type: 'many', relation: relationName, ...config };
}

// Field commands (simplified)
export function clear() {
    return { command: 'clear' };
}

// Minimal component implementations
export class MinimalComposer extends Component {
    setup() {
        super.setup();
    }
    
    static template = "llm_thread.MinimalComposer";
    static props = ["*"];
}

export class MinimalMessageList extends Component {
    setup() {
        super.setup();
    }
    
    static template = "llm_thread.MinimalMessageList";
    static props = ["*"];
}