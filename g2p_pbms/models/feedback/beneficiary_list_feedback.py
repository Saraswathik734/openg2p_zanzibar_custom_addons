import uuid
from odoo import fields, models


class G2PBeneficiaryListFeedback(models.Model):
    _name = "g2p.beneficiary.list.feedback"
    _description = "G2P Beneficiary List Feedback"
    _rec_name = "comment"

    feedback_id = fields.Char(string="Feedback ID", unique=True, readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    comment = fields.Char(string="Comment", readonly=True, required=True)
    file = fields.Binary(string="File", readonly=True, required=True)
    minio_file_id = fields.Char(string="Minio File ID", readonly=True)
    beneficiary_list_id = fields.Many2one(
        "g2p.beneficiary.list", string="Beneficiary List", indexed=True, required=True
    )
