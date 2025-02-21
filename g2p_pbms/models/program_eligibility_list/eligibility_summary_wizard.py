from odoo import models, fields, api


class G2PEligibilitySummaryWizard(models.TransientModel):
    _name = "g2p.eligibility.summary.wizard"
    _description = "Eligibility Summary Wizard"

    target_registry_type = fields.Selection(
        selection=lambda self: self.env["g2p.registry.type"].selection()
        or [("farmer", "Farmer"), ("student", "Student")],
        string="Registry Type",
        required=True,
    )

    # Farmer-specific fields
    farmer_registry_summary_id = fields.Many2one(
        "g2p.eligibility.summary.farmer", string="Farmer Registry Summary"
    )

    land_quartile_25 = fields.Float(string="Land Quartile 25")
    land_quartile_50 = fields.Float(string="Land Quartile 50")
    land_quartile_75 = fields.Float(string="Land Quartile 75")

    # Student-specific fields
    student_registry_summary_id = fields.Many2one(
        "g2p.eligibility.summary.student", string="Student Registry Summary"
    )
    age_quartile_25 = fields.Float(string="Age Quartile 25")
    age_quartile_50 = fields.Float(string="Age Quartile 50")
    age_quartile_75 = fields.Float(string="Age Quartile 75")

    def action_close(self):
        return {"type": "ir.actions.act_window_close"}
