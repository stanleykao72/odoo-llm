import json
import logging

from odoo import models, tools

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"
    
    # 18.0 Enhanced Methods

    def openai_format_message(self):
        """Provider-specific formatting for OpenAI."""
        self.ensure_one()
        body = self.body
        if body:
            body = tools.html2plaintext(body)

        if self.is_llm_user_message()[self]:
            formatted_message = {"role": "user"}
            if body:
                formatted_message["content"] = body
            return formatted_message

        elif self.is_llm_assistant_message()[self]:
            formatted_message = {"role": "assistant"}

            formatted_message["content"] = body

            # Add tool calls if present in body_json
            tool_calls = self.get_tool_calls()
            if tool_calls:
                formatted_message["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                        },
                    }
                    for tc in tool_calls
                ]

            return formatted_message

        elif self.is_llm_tool_message()[self]:
            tool_data = self.body_json
            if not tool_data:
                _logger.warning(
                    f"OpenAI Format: Skipping tool message {self.id}: no tool data found."
                )
                return None

            tool_call_id = tool_data.get("tool_call_id")
            if not tool_call_id:
                _logger.warning(
                    f"OpenAI Format: Skipping tool message {self.id}: missing tool_call_id."
                )
                return None

            # Get result content
            if "result" in tool_data:
                content = json.dumps(tool_data["result"])
            elif "error" in tool_data:
                content = json.dumps({"error": tool_data["error"]})
            else:
                content = ""

            formatted_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
            return formatted_message
        else:
            return None
    
    # 18.0 Enhanced Methods
    def _openai_format_message_safe(self):
        """18.0 enhanced method: Safe message formatting with error handling"""
        self.ensure_one()
        try:
            return self.openai_format_message()
        except Exception as e:
            _logger.error(f"Error formatting message {self.id} for OpenAI: {e}")
            return None
    
    def _get_openai_role(self):
        """18.0 enhanced method: Get OpenAI-specific role for message"""
        self.ensure_one()
        if self.is_llm_user_message()[self]:
            return "user"
        elif self.is_llm_assistant_message()[self]:
            return "assistant"
        elif self.is_llm_tool_message()[self]:
            return "tool"
        else:
            return None
    
    def _validate_openai_message_structure(self):
        """18.0 enhanced method: Validate message structure for OpenAI"""
        self.ensure_one()
        formatted = self.openai_format_message()
        if not formatted:
            return False
        
        # Check required fields
        if 'role' not in formatted:
            return False
        
        # Role-specific validation
        if formatted['role'] == 'tool' and 'tool_call_id' not in formatted:
            return False
        
        return True
