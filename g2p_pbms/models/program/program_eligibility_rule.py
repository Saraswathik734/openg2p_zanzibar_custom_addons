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
    eligibility_rule_description = fields.Char(
        string="Description",
        related="eligibility_rule_id.description"
    )

    def action_open_view_eligibility_domain(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Eligibility Rule Details',
            'res_model': 'g2p.eligibility.rule.definition',
            'res_id': self.eligibility_rule_id.id,
            'view_mode': 'form',
            "view_id": self.env.ref("g2p_pbms.view_g2p_eligibility_rule_definition").id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }