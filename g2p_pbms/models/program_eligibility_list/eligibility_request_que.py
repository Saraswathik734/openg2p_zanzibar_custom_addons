import json
from odoo import models, fields, api


class G2PQueEligibilityRequest(models.Model):
    _name = "g2p.que.eligibility.request"
    _description = "G2P Eligibility Request Queue"

    program_id = fields.Many2one("g2p.program.definition", string="G2P Program")
    brief = fields.Text(string="Brief")
    sql_query_json = fields.Text(string="Complete SQL Query", store=True, readonly=True)
    enumeration_status = fields.Selection(
        [
            ("pending", "PENDING"),
            ("complete", "COMPLETE"),
        ],
        string="Enumeration Status",
        default="pending",
    )
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now , readonly=True)
    processed_date = fields.Datetime(string="Processed Date", default=None, readonly=True)


    @api.model
    def create(self, vals):
        program_id = vals.get("program_id")
        if program_id:
            # Fetch the eligibility rule IDs from the Many2many relation
            program = self.env["g2p.program.definition"].browse(program_id)
            eligibility_rules = program.eligibility_rule_ids

            queries = [
                rule.sql_query
                for rule in eligibility_rules
                if rule.sql_query
            ]

            # Store a snapshot of the current SQL queries as JSON object
            vals["sql_query_json"] = json.dumps(queries) if queries else "[]"

        return super().create(vals)
