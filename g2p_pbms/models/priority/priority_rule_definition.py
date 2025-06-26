from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

import logging
from ..registries import G2PRegistryType

_logger = logging.getLogger(__name__)

class G2PPriorityRuleDefinition(models.Model):
    _name = "g2p.priority.rule.definition"
    _description = "G2P Priority Rule Definition"
    _rec_name = "mnemonic"

    mnemonic = fields.Char(string="Rule Mnemonic", required=True)
    description = fields.Char(string="Description")
    disbursement_cycle_id = fields.Many2one("g2p.disbursement.cycle", string="Disbursement Cycle")
    program_id = fields.Integer(related="disbursement_cycle_id.program_id.id", string="Program ID", readonly=True)
    target_registry_type = fields.Selection(
        selection=G2PRegistryType.selection(), string="Registry Type", required=True
    )
    pbms_domain = fields.Char(string="Domain", required=True)
    sql_query = fields.Char(string="SQL Query", compute="_get_query", store=True)

    @api.depends("pbms_domain", "target_registry_type")
    def _get_query(self):
        for rec in self:
            try:
                # Convert the domain string into a valid Python list of tuples.
                domain_value = safe_eval(rec.pbms_domain or "[]")
            except Exception as e:
                _logger.error(
                    "Error evaluating domain for priority rule %s: %s",
                    rec.mnemonic,
                    e,
                )
                rec.sql_query = "Invalid domain"
                continue

            # Define a mapping from the selection value to the target model.
            target_model_mapping = {
                "student": "g2p.student.registry",
                "farmer": "g2p.farmer.registry",
                # add additional mappings if needed
            }
            target_model_name = target_model_mapping.get(rec.target_registry_type)
            if not target_model_name:
                _logger.error(
                    "Unknown target_registry_type '%s' for rule %s",
                    rec.target_registry_type,
                    rec.mnemonic,
                )
                rec.sql_query = "Unknown target registry type"
                continue

            # Get the target model's recordset.
            target_model = self.env[target_model_name]

            try:
                # Calculate the where clause for the target model based on the evaluated domain.
                query = target_model._where_calc(domain_value)
            except Exception as e:
                _logger.error(
                    "Error calculating where clause for rule %s: %s", rec.mnemonic, e
                )
                rec.sql_query = "Error calculating query"
                continue

            try:
                from_clause, where_clause, where_clause_params = query.get_sql()
            except Exception as e:
                _logger.error(
                    "Error generating SQL from query for rule %s: %s", rec.mnemonic, e
                )
                rec.sql_query = "Error generating SQL"
                continue

            where_str = (" WHERE %s" % where_clause) if where_clause else ""
            # Use the target model's table name in the SQL query.
            query_str = (
                'SELECT "%s".unique_id FROM ' % target_model._table + from_clause + where_str
            )

            # Format the parameters as strings.
            formatted_params = list(
                map(lambda x: "'" + str(x) + "'", where_clause_params)
            )

            try:
                rec.sql_query = query_str % tuple(formatted_params)
                _logger.info("Query for rule %s: %s", rec.mnemonic, rec.sql_query)
            except Exception as e:
                _logger.error(
                    "Error formatting query for priority rule %s: %s",
                    rec.mnemonic,
                    e,
                )
                rec.sql_query = "Error formatting query"

    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Priority Rule Details",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "readonly"},
        }

