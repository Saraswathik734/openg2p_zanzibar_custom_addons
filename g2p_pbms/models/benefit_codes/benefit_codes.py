from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PBenefitCodes(models.Model):
    _name = "g2p.benefit.codes"
    _description = "Benefit Codes"
    _table = "g2p_benefit_codes"
    _rec_name = "benefit_mnemonic"

    benefit_mnemonic = fields.Char(string="Benefit Mnemonic", required=True)
    benefit_type = fields.Selection(
        [   
            ("CASH", "Cash"),
            ("COMMODITY", "Commodity"),
            ("SERVICE", "Service"),
            ("COMBINATION", "Combination"),
        ],
        string="Benefit Type",
        required=True,
    )
    benefit_classification_id = fields.Many2one(
        "g2p.benefit.classification.codes",
        string="Benefit Classification",
        required=True,
    )
    benefit_description = fields.Text(string="Benefit Description")
    measurement_unit = fields.Char(string="Measurement Unit")

    _sql_constraints = [
        (
            "unique_benefit_mnemonic",
            "unique(benefit_mnemonic)",
            "The benefit mnemonic must be unique!",
        )
    ]

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.benefit.codes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'benefit_code_form_edit':True},
        }

