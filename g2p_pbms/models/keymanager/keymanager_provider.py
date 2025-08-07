from odoo import models, api
import base64
import json
import logging
from datetime import datetime

import requests
from cryptography.hazmat.primitives.serialization import Encoding
from jose import jwt

_logger = logging.getLogger(__name__)


class KeymanagerProvider(models.AbstractModel):
    _name = 'keymanager.provider'
    _description = 'Keymanager Provider'

    @api.model
    def km_generate_current_time(self):
        return f'{datetime.now().isoformat(timespec = "milliseconds")}Z'

    def jwt_sign_keymanager(
        self,
        data,
        include_payload=True,
        include_certificate=False,
        include_cert_hash=False,
        **kwargs,
    ) -> str:
        self.keymanager_api_base_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_api_base_url')
        self.keymanager_api_timeout = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_api_timeout')
        self.keymanager_sign_application_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_sign_application_id')
        self.keymanager_sign_reference_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_sign_reference_id')

        self.ensure_one()
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()

        access_token = self.km_get_access_token()
        current_time = self.km_generate_current_time()
        url = f"{self.keymanager_api_base_url}/jwtSign"
        headers = {"Cookie": f"Authorization={access_token}"}
        payload = {
            "id": "string",
            "version": "string",
            "requesttime": current_time,
            "metadata": {},
            "request": {
                "dataToSign": self.km_urlsafe_b64encode(data),
                "applicationId": self.keymanager_sign_application_id or "",
                "referenceId": self.keymanager_sign_reference_id or "",
                "includePayload": include_payload,
                "includeCertificate": include_certificate,
                "includeCertHash": include_cert_hash,
            },
        }
        response = requests.post(url, json=payload, headers=headers, timeout=self.keymanager_api_timeout)
        _logger.debug("Keymanager JWT Sign API response: %s", response.text)
        response.raise_for_status()
        if response:
            response = response.json()
        if response:
            response = response.get("response", {})
        if response:
            return response.get("jwtSignedData")
        raise ValueError("Could not sign jwt, invalid keymanager response")

    def jwt_verify_keymanager(self, data: str, **kwargs):
        self.ensure_one()

        self.keymanager_api_base_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_api_base_url')
        self.keymanager_api_timeout = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_api_timeout')
        self.keymanager_sign_application_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_sign_application_id')
        self.keymanager_sign_reference_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_sign_reference_id')

        access_token = self.km_get_access_token()
        current_time = self.km_generate_current_time()
        url = f"{self.keymanager_api_base_url}/jwtVerify"
        headers = {"Cookie": f"Authorization={access_token}"}
        payload = {
            "id": "string",
            "version": "string",
            "requesttime": current_time,
            "metadata": {},
            "request": {
                "jwtSignatureData": data,
                "applicationId": self.keymanager_sign_application_id or "",
                "referenceId": self.keymanager_sign_reference_id or "",
                "validateTrust": False,
            },
        }
        response = requests.post(url, json=payload, headers=headers, timeout=self.keymanager_api_timeout)
        _logger.debug("Keymanager JWT Verify API response: %s", response.text)
        response.raise_for_status()
        if response:
            response = response.json()
        if response:
            response = response.get("response", {})
        if response:
            response = response.get("signatureValid", False)
        else:
            raise ValueError("Could not verify jwt, invalid keymanager response")
        if response:
            return jwt.get_unverified_claims(data)
        raise ValueError("invalid jwt signature")

    def km_get_access_token(self):
        self.ensure_one()

        self.keymanager_access_token = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_access_token')
        self.keymanager_access_token_expiry = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_access_token_expiry')
        self.keymanager_api_timeout = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_api_timeout')
        
        self.keycloak_auth_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keycloak_auth_url')
        self.keycloak_auth_client_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keycloak_auth_client_id')
        self.keycloak_auth_client_secret = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keycloak_auth_client_secret')
        self.keycloak_auth_grant_type = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keycloak_auth_grant_type')

        if (
            self.keymanager_access_token
            and self.keymanager_access_token_expiry
            and self.keymanager_access_token_expiry > datetime.now()
        ):
            return self.keymanager_access_token
        data = {
            "client_id": self.keycloak_auth_client_id,
            "client_secret": self.keycloak_auth_client_secret,
            "grant_type": self.keycloak_auth_grant_type,
        }
        response = requests.post(self.keycloak_auth_url, data=data, timeout=self.keymanager_api_timeout)
        _logger.debug("Keymanager get Certificates API response: %s", response.text)
        response.raise_for_status()
        access_token = response.json().get("access_token", None)
        token_exp = jwt.get_unverified_claims(access_token).get("exp")
        self.write(
            {
                "keymanager_access_token": access_token,
                "keymanager_access_token_expiry": datetime.fromtimestamp(token_exp)
                if isinstance(token_exp, int)
                else datetime.fromisoformat(token_exp)
                if isinstance(token_exp, str)
                else token_exp,
            }
        )
        return access_token

    @api.model
    def km_urlsafe_b64encode(self, input_data: bytes) -> str:
        return base64.urlsafe_b64encode(input_data).decode().rstrip("=")

    @api.model
    def km_urlsafe_b64decode(self, input_data: str) -> bytes:
        return base64.urlsafe_b64decode(input_data.encode() + b"=" * (-len(input_data) % 4))