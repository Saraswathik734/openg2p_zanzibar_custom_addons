from odoo import models, fields, api

from ..registries import G2PRegistryType


class G2PEligibilitySummary(models.AbstractModel):
    _name = "g2p.eligibility.summary"
    _description = "Abstract Eligibility Summary"

    program_id = fields.Many2one("g2p.program.definition", string="Program")
    program_mnemonic = fields.Char(string="Program Mnemonic")
    target_registry_type = fields.Selection(
        selection=G2PRegistryType.selection(), string="Registry Type", required=True
    )
    eligibility_request_id = fields.Many2one(
        "g2p.que.eligibility.request", string="Eligibility Request ID"
    )
    number_of_registrants = fields.Integer(string="Number of Registrants")
    date_created = fields.Datetime(string="Date Created", default=fields.Datetime.now)

    def action_open_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            "target_registry_type": self.target_registry_type,
        }
        if self.target_registry_type == "farmer":
            wizard_vals.update(
                {
                    "farmer_registry_summary_id": self.id,
                    "land_quartile_25": self.land_quartile_25,
                    "land_quartile_50": self.land_quartile_50,
                    "land_quartile_75": self.land_quartile_75,
                }
            )
        elif self.target_registry_type == "student":
            wizard_vals.update(
                {
                    "student_registry_summary_id": self.id,
                    "age_quartile_25": self.age_quartile_25,
                    "age_quartile_50": self.age_quartile_50,
                    "age_quartile_75": self.age_quartile_75,
                }
            )
        wizard = self.env["g2p.eligibility.summary.wizard"].create(wizard_vals)
        return {
            "name": "Eligibility Summary Details",
            "view_mode": "form",
            "res_model": "g2p.eligibility.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
