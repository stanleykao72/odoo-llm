import logging
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ModelLine(models.TransientModel):
    _name = "llm.fetch.models.line"
    _description = "LLM Model Import Line"
    _rec_name = "name"

    wizard_id = fields.Many2one(
        "llm.fetch.models.wizard",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Model Name",
        required=True,
    )
    model_use = fields.Selection(
        selection="_get_available_model_usages",
        required=True,
        default="chat",
    )
    status = fields.Selection(
        [
            ("new", "New"),
            ("existing", "Existing"),
            ("modified", "Modified"),
        ],
        required=True,
        default="new",
    )
    selected = fields.Boolean(default=True)
    details = fields.Json()  # Change to Json field to store structured data
    existing_model_id = fields.Many2one("llm.model")

    _sql_constraints = [
        (
            "unique_model_per_wizard",
            "UNIQUE(wizard_id, name)",
            "Each model can only be listed once per import.",
        )
    ]

    @api.model
    def _get_available_model_usages(self):
        return self.env["llm.model"]._get_available_model_usages()


class FetchModelsWizard(models.TransientModel):
    _name = "llm.fetch.models.wizard"
    _description = "Import LLM Models"

    provider_id = fields.Many2one(
        "llm.provider",
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        "llm.fetch.models.line",
        "wizard_id",
        string="Models",
    )
    model_count = fields.Integer(
        compute="_compute_model_count",
        string="Models Found",
    )
    new_count = fields.Integer(
        compute="_compute_model_count",
        string="New Models",
    )
    modified_count = fields.Integer(
        compute="_compute_model_count",
        string="Modified Models",
    )

    @api.depends("line_ids", "line_ids.status")
    def _compute_model_count(self):
        """Compute various model counts for display"""
        for wizard in self:
            wizard.model_count = len(wizard.line_ids)
            wizard.new_count = len(
                wizard.line_ids.filtered(lambda record: record.status == "new")
            )
            wizard.modified_count = len(
                wizard.line_ids.filtered(lambda record: record.status == "modified")
            )

    @api.model
    def default_get(self, fields_list):
        """Fetch models and prepare wizard data"""
        res = super().default_get(fields_list)

        # Check for provider_id in context first (from model form)
        default_provider_id = self._context.get("default_provider_id")
        if default_provider_id:
            provider = self.env["llm.provider"].browse(default_provider_id)
            if not provider.exists():
                raise UserError(_("Provider not found."))
            res["provider_id"] = provider.id
        # If no default_provider_id, try active_id (from provider form)
        elif self._context.get("active_id"):
            provider = self.env["llm.provider"].browse(self._context["active_id"])
            if not provider.exists():
                raise UserError(_("Provider not found."))
            res["provider_id"] = provider.id
        else:
            return res

        # Prepare model lines
        lines = []
        existing_models = {
            model.name: model
            for model in self.env["llm.model"].search(
                [("provider_id", "=", res["provider_id"])]
            )
        }

        # Fetch and process models
        model_to_fetch = self._context.get("default_model_to_fetch")
        models_data = []
        try:
            if model_to_fetch:
                models_data = provider.list_models(model_id=model_to_fetch)
            else:
                models_data = provider.list_models()
        except Exception as e:
            _logger.error("Error fetching models for provider %s: %s", provider.name, str(e))
            # Return empty wizard with error message
            return {
                "provider_id": provider.id,
                "line_ids": [],
                "model_count": 0,
                "new_count": 0,
                "modified_count": 0,
            }

        for model_data in models_data:
            details = model_data.get("details", {})
            name = model_data.get("name") or details.get("id")

            if not name:
                continue

            # Determine model use and capabilities
            capabilities = details.get("capabilities", ["chat"])
            model_use = self._determine_model_use(name, capabilities)

            # Check against existing models
            existing = existing_models.get(name)
            status = "new"
            if existing:
                # Compare details properly - convert both to JSON strings for comparison
                existing_details_json = json.dumps(existing.details or {}, sort_keys=True)
                new_details_json = json.dumps(details, sort_keys=True)
                status = "modified" if existing_details_json != new_details_json else "existing"

            # Only add lines for new or modified models to avoid duplicates
            if status in ["new", "modified"]:
                line_vals = {
                    "name": name,
                    "model_use": model_use,
                    "status": status,
                    "details": details,  # Store as dict directly for Json field
                    "existing_model_id": existing.id if existing else False,
                    "selected": True,  # Always select new and modified models
                }
                
                lines.append((0, 0, line_vals))

        if lines:
            res["line_ids"] = lines

        return res

    @api.model
    def _determine_model_use(self, name, capabilities):
        """Helper to determine model use based on name and capabilities"""
        if (
            any(cap in capabilities for cap in ["embedding", "text-embedding"])
            or "embedding" in name.lower()
        ):
            return "embedding"
        elif any(cap in capabilities for cap in ["multimodal", "vision"]):
            return "multimodal"
        return "chat"  # default

    def action_confirm(self):
        """Process selected models and create/update records"""
        self.ensure_one()
        Model = self.env["llm.model"]

        selected_lines = self.line_ids.filtered(
            lambda record: record.selected and record.name
        )
        
        if not selected_lines:
            raise UserError(_("Please select at least one model to import."))

        for line in selected_lines:
            
            # Use details directly as it's already a dict from Json field
            details_dict = line.details or {}
                
            values = {
                "name": line.name.strip(),
                "provider_id": self.provider_id.id,
                "model_use": line.model_use,
                "details": details_dict,  # Use dict directly
                "active": True,
            }

            # Search for existing model in the same provider with the same name
            existing_model = Model.search([
                ("provider_id", "=", self.provider_id.id),
                ("name", "=", line.name.strip())
            ], limit=1)

            if existing_model:
                existing_model.write(values)
            else:
                Model.create(values)

        # Return success message
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _(
                    "%d models have been imported/updated.", len(selected_lines)
                ),
                "sticky": False,
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
