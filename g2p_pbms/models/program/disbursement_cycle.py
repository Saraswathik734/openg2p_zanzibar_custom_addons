from odoo import models, fields


class G2PDisbursementCycle(models.Model):
    _name = "g2p.disbursement.cycle"
    _description = "G2P Disbursement Cycle"
    _rec_name = "cycle_mnemonic"

    cycle_mnemonic = fields.Char(string="Cycle Mnemonic", required=True)
    pbms_request_id = fields.Char(string='PBMS Request ID')
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program")
    envelope_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Envelope Status",
        default="pending",
    )
    disbursement_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Entitlement Process Status",
        default="not_applicable",
    )
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now , readonly=True)
    processed_date = fields.Datetime(string="Processed Date", default=None, readonly=True)
    
    def action_open_cycle_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            "target_registry_type": self.program_id.target_registry_type,
            "brief": self.brief,
            "program_id": self.program_id.id,
            "pbms_request_id": self.pbms_request_id,
        }

        wizard = self.env["g2p.eee.cycle.summary.wizard"].create(wizard_vals)
        return {
            "name": "Cycle Summary Details",
            "view_mode": "form",
            "res_model": "g2p.eee.cycle.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_target_registry_type': self.program_id.target_registry_type,
                'default_program_id': self.program_id.id,
                'default_pbms_request_id': self.pbms_request_id,
            },
        }

    def action_open_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            "target_registry_type": self.program_id.target_registry_type,
            "brief": self.brief,
            "program_id": self.program_id.id,
            "pbms_request_id": self.pbms_request_id,
        }

        wizard = self.env["g2p.eee.summary.wizard"].create(wizard_vals)
        return {
            "name": "Eligibility Summary Details",
            "view_mode": "form",
            "res_model": "g2p.eee.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_target_registry_type': self.program_id.target_registry_type,
                'default_program_id': self.program_id.id,
                'default_pbms_request_id': self.pbms_request_id,
            },
        }
