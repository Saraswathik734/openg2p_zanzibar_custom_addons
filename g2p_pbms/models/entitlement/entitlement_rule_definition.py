from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

import logging
import json
from ..registries import G2PRegistryType

_logger = logging.getLogger(__name__)

class G2PEntitlementRuleDefinition(models.Model):
    _name = "g2p.entitlement.rule.definition"
    _description = "G2P Program Entitlement Rule Definition"
    _rec_name = "mnemonic"

    mnemonic = fields.Char(string="Rule Mnemonic", required=True)
    description = fields.Char(string="Description")
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program")
    benefit_code_id = fields.Many2one(
        'g2p.benefit.codes',
        string="Benefit Code",
        help="Select a benefit code defined in the selected program."
    )
    measurement_unit = fields.Char(
        string="Measurement Unit",
        related="benefit_code_id.measurement_unit",
        readonly=True,
    )
    quantity = fields.Integer(string="Quantity", required=True)
    multiplier = fields.Char(
        string="Multiplier",
        help="Select an integer field from the registry to use as a multiplier."
    )
    max_quantity = fields.Integer(
        string="Maximum Quantity",
        help="Set to 0 for no limit.",
        required=True,
    )
    target_registry = fields.Selection(
        related='program_id.target_registry', string="Registry Type", required=True
    )
    pbms_domain = fields.Char(string="Domain", required=True)
    sql_query = fields.Char(string="SQL Query", compute="_get_query", store=True)
    allowed_benefit_code_ids = fields.Many2many(
        'g2p.benefit.codes', related='program_id.benefit_code_ids', store=False
    )
    allowed_multipliers = fields.Char(compute='_compute_multiplier_options', store=False)

    @api.model
    def create(self, vals):
        multiplier_value = vals.get('multiplier')
        _logger.info("Multiplier in create: %s", multiplier_value)
        _logger.info("all VALS: %s", vals)

        # Add custom logic here
        return super().create(vals)

    @api.depends('program_id.target_registry')
    def _compute_multiplier_options(self):
        for rec in self:
            registry_type = rec.program_id.target_registry
            registry_map = {
                "student": "g2p.student.registry",
                "farmer": "g2p.farmer.registry",
            }
            model_name = registry_map.get(registry_type)
            if not model_name:
                rec.allowed_multipliers = "[]"
                continue

            model = self.env[model_name]
            int_fields = [
                (name, field.string or name)
                for name, field in model._fields.items()
                if field.type == 'integer'
            ]
            # rec.allowed_multipliers = str(int_fields)
            rec.allowed_multipliers = json.dumps(int_fields)

    # def _get_registry_integer_fields(self):
    #     registry_type = self.env['g2p.entitlement.rule.definition'].default_get(['target_registry'])
    #     print("Registry Type:", registry_type)

    #     target_model_mapping = {
    #         "student": "g2p.student.registry",
    #         "farmer": "g2p.farmer.registry",
    #         # Add more registry types here as needed
    #     }
    #     target_model = target_model_mapping.get(registry_type)
    #     print("Target Model:", target_model)
    #     if not target_model:
    #         return []

    #     model = self.env[target_model]
    #     integer_fields = [
    #         (name, field.string or name)
    #         for name, field in model._fields.items()
    #         if field.type == "integer"
    #     ]
    #     print("Integer Fields:", integer_fields)

    #     return sorted(integer_fields, key=lambda x: x[1])

    @api.depends("pbms_domain", "target_registry")
    def _get_query(self):
        for rec in self:
            try:
                # Convert the domain string into a valid Python list of tuples.
                domain_value = safe_eval(rec.pbms_domain or "[]")
            except Exception as e:
                _logger.error(
                    "Error evaluating domain for entitlement rule %s: %s",
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
            target_model_name = target_model_mapping.get(rec.target_registry)
            if not target_model_name:
                _logger.error(
                    "Unknown target_registry '%s' for rule %s",
                    rec.target_registry,
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
                    "Error formatting query for entitlement rule %s: %s",
                    rec.mnemonic,
                    e,
                )
                rec.sql_query = "Error formatting query"
    
    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Entitlement Rule Details",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "readonly"},
        }

