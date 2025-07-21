import uuid
from odoo import fields, models
import base64

import logging

_logger = logging.getLogger(__name__)


class G2PBeneficiaryListFeedback(models.Model):
    _name = "g2p.beneficiary.list.feedback"
    _description = "G2P Beneficiary List Feedback"
    _rec_name = "comment"

    feedback_id = fields.Char(string="Feedback ID", unique=True, readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    comment = fields.Char(string="Feedback Comment", readonly=True, required=True)
    file = fields.Binary(string="File", readonly=True, required=True, attachment=True)
    filename = fields.Char(string="Filename", readonly=True)
    content_type = fields.Char(string="Content Type", readonly=True)
    minio_file_id = fields.Char(string="Minio File ID", readonly=True)
    beneficiary_list_id = fields.Many2one(
        "g2p.beneficiary.list", string="Beneficiary List", index=True, required=True
    )
    feedback_datetime = fields.Datetime(string="Feedback Timestamp", default=fields.Datetime.now)

    def create(self, vals):
        # Upload the file to MinIO before creating the record
        file_content = vals.get('file')
        filename = vals.get('filename', '')
        if file_content:
            try:
                # Use the minio.client model to upload the file and get the file id
                minio_file_id = self.env['minio.client'].upload_file(
                    file_content,
                    filename=filename
                )
                vals['minio_file_id'] = minio_file_id
                
                # Store the detected content type for future preview use
                file_bytes = base64.b64decode(file_content)
                content_type = self.env['minio.client']._detect_content_type_from_content(file_bytes)
                vals['content_type'] = content_type
            except Exception as e:
                raise ValueError(f"Failed to upload feedback file: {str(e)}")
        return super(G2PBeneficiaryListFeedback, self).create(vals)

    def write(self, vals):
        # If the file is being updated, upload the new file to MinIO
        if 'file' in vals and vals['file']:
            filename = vals.get('filename', '')
            try:
                minio_file_id = self.env['minio.client'].upload_file(
                    vals['file'],
                    filename=filename
                )
                vals['minio_file_id'] = minio_file_id
                
                # Store the detected content type for future preview use
                file_bytes = base64.b64decode(vals['file'])
                content_type = self.env['minio.client']._detect_content_type_from_content(file_bytes)
                vals['content_type'] = content_type
            except Exception as e:
                raise ValueError(f"Failed to upload feedback file: {str(e)}")
        return super(G2PBeneficiaryListFeedback, self).write(vals)

    def action_view_feedback_file(self):
        self.ensure_one()
        if not self.minio_file_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'No File Uploaded',
                'view_mode': 'form',
                'res_model': self._name,
                'res_id': self.id,
                'target': 'new',
                'context': dict(self.env.context, no_file=True),
            }
        try:
            url = self.env['minio.client'].get_file_preview_url(
                self.minio_file_id, 
                content_type=self.content_type
            )
            _logger.debug("MinIO file preview URL: %s", url)

        except Exception as e:
            return {
                'type': 'ir.actions.act_window',
                'name': str(e),
                'view_mode': 'form',
                'res_model': self._name,
                'res_id': self.id,
                'target': 'new',
                'context': dict(self.env.context, file_preview_error=str(e)),
            }
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }