from odoo import models, fields
from ..registries import G2PRegistryType


class G2PProgramDefinition(models.Model):
    _name = "g2p.program.definition"
    _description = "G2P Program Definition"
    _table = "g2p_program_definition"
    _rec_name = "program_mnemonic"

    program_mnemonic = fields.Char(string="Program Mnemonic", required=True)
    description = fields.Char(string="Description")
    delivery_id = fields.Many2one(
        "g2p.delivery.codes", string="Delivery Code", required=True
    )
    target_registry_type = fields.Selection(
        selection=G2PRegistryType.selection(), string="Registry Type", required=True
    )
    program_status = fields.Selection(
        [
            ("ACTIVE", "Active"),
            ("PAUSED", "Paused"),
            ("CLOSED", "Closed"),
        ],
        string="Program Status",
        required=True,
    )
    eligibility_rule_ids = fields.One2many(
        "g2p.program.eligibility.rule", "program_id", "Eligibility Rule"
    )

    eligibility_summary_farmer_ids = fields.One2many(
        "g2p.eligibility.summary.farmer",
        "program_id",
        string="Farmer Eligibility Summary",
    )
    eligibility_summary_student_ids = fields.One2many(
        "g2p.eligibility.summary.student",
        "program_id",
        string="Student Eligibility Summary",
    )

    _sql_constraints = [
        (
            "unique_program_mnemonic",
            "unique(program_mnemonic)",
            "The program mnemonic must be unique!",
        )
    ]

    def action_open_edit(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Edit Program Deatils",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "edit"},
        }

    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Program Details",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "readonly"},
        }

    def action_create_eligibility_list(self):
        self.ensure_one()
        eligibility_obj = self.env["g2p.eligibility.request.queue"]
        eligibility_record = eligibility_obj.create(
            {
                "program_id": self.id,
                "brief": self.description or "",
                "enumeration_status": "pending",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "g2p.eligibility.request.queue",
            "view_mode": "form",
            "res_id": eligibility_record.id,
            "target": "current",
        }
