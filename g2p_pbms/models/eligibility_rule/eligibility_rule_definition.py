from odoo import models, fields


class G2PEligibilityRuleDefinition(models.Model):
    _name = "g2p.eligibility.rule.definition"
    _description = "G2P Program Eligibility Rule Definition"

    mneumonic = fields.Char(string="Rule Mnemonic", required=True)
    description = fields.Char(string="Description")
    target_registrant_type = fields.Many2one(
        "g2p.registry.type", string="Target Registrant Type", required=True
    )
    domain = fields.Char(string="Domain", required=True)
    sql_query = fields.Char(string="SQL Query", required=True)
