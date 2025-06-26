import uuid
from odoo import fields, models


class G2PBeneficiaryListVerification(models.Model):
    _name = "g2p.beneficiary.list.verification"
    _description = "G2P Beneficiary List Verification"
    _rec_name = "name"

    verification_id = fields.Char(string="Feedback ID", unique=True, readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    beneficiary_list_id = fields.Many2one(
        "g2p.beneficiary.list", string="Beneficiary List", indexed=True, required=True
    )
    name = fields.Char(string="Verifier Name", required=True)
    comment = fields.Char(string="Comment", required=True)
    verification_status = fields.Selection(
        [
            ("pending", "PENDING"),
            ("verified", "VERIFIED")
        ],
        string="Verification Status",
        default="pending",
    )
    verification_timestamp = fields.Datetime(
        string="Verification Timestamp", default=fields.Datetime.now, readonly=True
    )

    def action_verify(self):
        self.ensure_one()
        self.verification_status = "verified"
        self.verification_timestamp = fields.Datetime.now()