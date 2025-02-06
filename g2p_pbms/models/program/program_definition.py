from odoo import models, fields


class G2PProgramDefinition(models.Model):
    _name = "g2p.program.definition"
    _description = "G2P Program Definition"
    _table = "g2p_program_definition"

    program_mnemonic = fields.Char(string="Program Mnemonic", required=True)
    description = fields.Char(string="Description")
    delivery_id = fields.Many2one(
        "g2p.delivery.codes", string="Delivery Code", required=True
    )
    target_registrant_type = fields.Many2one(
        "g2p.registry.type", string="Target Registrant Type", required=True
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

    _sql_constraints = [
        (
            "unique_program_mnemonic",
            "unique(program_mnemonic)",
            "The program mnemonic must be unique!",
        )
    ]
