from odoo import models, fields


class G2PProgramEligibilityRule(models.Model):
    _name = "g2p.program.eligibility.rule"
    _description = "G2P Program Eligibility Rule"

    program_id = fields.Many2one(
        "g2p.program.definition", string="Program", required=True
    )
    eligibility_rule_id = fields.Many2one(
        "g2p.eligibility.rule.definition", string="Eligibility Rule", required=True
    )
