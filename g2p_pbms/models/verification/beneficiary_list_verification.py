import uuid
from odoo import fields, models, api


class G2PBeneficiaryListVerification(models.Model):
    _name = "g2p.beneficiary.list.verification"
    _description = "G2P Beneficiary List Verification"
    _rec_name = "name"

    verification_id = fields.Char(string="Verification ID", unique=True, readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    beneficiary_list_id = fields.Many2one(
        "g2p.beneficiary.list", string="Beneficiary List", index=True, required=True
    )
    name = fields.Char(
        string="Verifier Name",
        required=True,
        readonly=True,
        default=lambda self: self.env.user.name if self.env.user else "Anonymous"
    )
    comment = fields.Text(string="Comment", required=True)
    verification_timestamp = fields.Datetime(
        string="Verification Timestamp", default=fields.Datetime.now, readonly=True
    )

    def action_add_verification(self):
        context = self.env.context
        beneficiary_list_id = context.get('default_beneficiary_list_id') or context.get('active_id') or self.beneficiary_list_id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Verification',
            'res_model': 'g2p.beneficiary.list.verification',
            'view_mode': 'form',
            'view_id': self.env.ref('g2p_pbms.view_g2p_beneficiary_list_verification_form').id,
            'target': 'new',
            'context': {
                'default_beneficiary_list_id': beneficiary_list_id,
            },
        }