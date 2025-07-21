from odoo import fields, models, api
from urllib.parse import urlparse


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    g2p_pbms_eee_api_url = fields.Char(string="EEE API URL", config_parameter="g2p_pbms.eee_api_url")
    g2p_bridge_api_url = fields.Char(string="G2P Bridge API URL", config_parameter="g2p_pbms.g2p_bridge_api_url")

    minio_endpoint = fields.Char(string="MinIO Endpoint", config_parameter="minio.endpoint")
    minio_access_key = fields.Char(string="MinIO Access Key", config_parameter="minio.access_key")
    minio_secret_key = fields.Char(string="MinIO Secret Key", config_parameter="minio.secret_key")
    minio_bucket = fields.Char(string="MinIO Bucket", config_parameter="minio.bucket")
