from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PBenefitClassificationCodes(models.Model):
    _name = "g2p.benefit.classification.codes"
    _description = "Benefit Classification Codes"
    _table = "g2p_benefit_classification_codes"
    _rec_name = "benefit_classification_mnemonic"

    benefit_classification_mnemonic = fields.Char(
        string="Benefit Classification Mnemonic", required=True
    )
    description = fields.Char(string="Description")

    _sql_constraints = [
        (
            "unique_benefit_classification_mnemonic",
            "unique(benefit_classification_mnemonic)",
            "The benefit classification mnemonic must be unique!",
        )
    ]

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.benefit.classification.codes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'benefit_classification_code_form_edit':True},
        }



