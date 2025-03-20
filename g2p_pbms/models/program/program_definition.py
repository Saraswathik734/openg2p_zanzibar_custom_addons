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

    # Add related field for measurement_unit from delivery_id
    measurement_unit = fields.Char(
        related='delivery_id.measurement_unit',
        string="Measurement Unit",
        readonly=True
    )
    display_quantity = fields.Char(string="Quantity", compute="_compute_display_quantity")

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

    @api.depends('max_quantity', 'measurement_unit')
    def _compute_display_quantity(self):
        for rec in self:
            rec.display_quantity = f"{rec.max_quantity} {rec.measurement_unit or ''}"

    @api.depends('entitlement_id')
    def _compute_entitlement_inline_ids(self):
        for rec in self:
            rec.entitlement_inline_ids = rec.entitlement_id or False

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.program.definition',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'program_form_edit':True},
        }
