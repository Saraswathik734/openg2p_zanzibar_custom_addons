from odoo import models, fields, api
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
        'g2p.eligibility.rule.definition', 'program_id', string="Eligibility Rules"
    )
    entitlement_rule_ids = fields.One2many(
        'g2p.entitlement.rule.definition', 'program_id', string="Entitlement Rules"
    )
    que_eee_request_ids = fields.One2many(
        "g2p.que.eee.request",
        "program_id",
        string="Eligibility Request Queue",
        states={'draft': [('readonly', False)], 'confirm': [('readonly', True)]},
    )

    #Entitlement Configuration
    max_quantity = fields.Integer(string="Max Quantity")

    # Cycle configuration
    disbursement_frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annually', 'Semi-Annually'),
        ('annually', 'Annually'),
        ('on_demand', 'On-Demand'),
    ], string="Disbursement Frequency", required=True, default='on_demand')

    disbursement_type = fields.Selection([
        ('auto', 'Auto'),
        ('manual', 'Manual')
    ], string="Disbursement Type", required=True, default='manual')

    disbursement_cycle_list = fields.Selection([
        ('latest_always', 'Latest Always'),
        ('labeled', 'Labeled')
    ], string="Disbursement Cycle List", required=True, default='latest_always')

    _sql_constraints = [
        (
            "unique_program_mnemonic",
            "unique(program_mnemonic)",
            "The program mnemonic must be unique!",
        )
    ]

    @api.depends('entitlement_id')
    def _compute_entitlement_inline_ids(self):
        for rec in self:
            rec.entitlement_inline_ids = rec.entitlement_id or False

    def action_open_edit(self):
        self.ensure_one()
        edit_view_id = self.env.ref('g2p_pbms.view_g2p_pgm_edit').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.program.definition',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(edit_view_id, 'form')],
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }
