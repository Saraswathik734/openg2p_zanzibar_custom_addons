import uuid
from odoo import fields, models, api
import base64

import logging

_logger = logging.getLogger(__name__)


class G2PBeneficiaryListFeedback(models.Model):
    _inherit = "storage.file"
    # TODO: Name defaults to UUID

    comment = fields.Char(string="Feedback Comment", readonly=True, required=False)
    beneficiary_list_id = fields.Many2one(
        "g2p.beneficiary.list", string="Beneficiary List", index=True, required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super(G2PBeneficiaryListFeedback, self).default_get(fields_list)
        if 'backend_id' in fields_list and not res.get('backend_id'):
            doc_store_id_str = (
                self.env["ir.config_parameter"].sudo().get_param("g2p_pbms.document_store")
            )
            if doc_store_id_str:
                res['backend_id'] = int(doc_store_id_str)
        return res
