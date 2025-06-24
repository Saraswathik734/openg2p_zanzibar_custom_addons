import logging
import requests
from odoo import models, fields, api
import datetime

_logger = logging.getLogger(__name__)

class G2PDisbursementEnvelopeSummaryWizard(models.TransientModel):
    _name = 'g2p.disbursement.envelope.summary.wizard'
    _description = 'G2P Disbursement Envelope Status Summary Wizard'
    
    program_mnemonic = fields.Char(string="Program Mnemonic")
    cycle_mnemonic = fields.Char(string="Cycle Mnemonic")
    beneficiary_list_id = fields.Char(string="Beneficiary List ID")
    disbursement_envelope_id = fields.Char(string="Disbursement Envelope ID")
    measurement_unit = fields.Char(string="Measurement Unit")
    
    number_of_disbursements_received = fields.Integer(string="Disbursements Received", compute='_action_fetch_summary')
    total_disbursement_amount_received = fields.Char(string="Total Amount Received")
    
    funds_available_with_bank = fields.Char(string="Funds Available With Bank")
    funds_available_latest_timestamp = fields.Datetime(string="Funds Available Latest Timestamp")
    funds_available_latest_error_code = fields.Char(string="Funds Available Latest Error Code")
    funds_available_attempts = fields.Integer(string="Funds Available Attempts")
    
    funds_blocked_with_bank = fields.Char(string="Funds Blocked With Bank")
    funds_blocked_latest_timestamp = fields.Datetime(string="Funds Blocked Latest Timestamp")
    funds_blocked_latest_error_code = fields.Char(string="Funds Blocked Latest Error Code")
    funds_blocked_attempts = fields.Integer(string="Funds Blocked Attempts")
    funds_blocked_reference_number = fields.Char(string="Funds Blocked Reference Number")
        
    number_of_disbursements_shipped = fields.Integer(string="Disbursements Shipped")
    number_of_disbursements_reconciled = fields.Integer(string="Disbursements Reconciled")
    number_of_disbursements_reversed = fields.Integer(string="Disbursements Reversed")

    def _parse_datetime(self, dt_str):
        """
        Convert ISO datetime string (with T and microseconds) into
        Odoo's datetime format: 'YYYY-MM-DD HH:MM:SS'
        """
        if dt_str:
            try:
                # Convert using fromisoformat (Python 3.7+)
                dt = datetime.datetime.fromisoformat(dt_str)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                _logger.error("Error parsing datetime '%s': %s", dt_str, e)
                return dt_str
        return False
    
    def _action_fetch_summary(self):
        self.ensure_one()
        # Retrieve the endpoint from system parameters
        g2p_bridge_api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.g2p_bridge_api_url')
        if not g2p_bridge_api_url:
            _logger.error("G2P Bridge API URL not set in configuration")
            return

        endpoint = f"{g2p_bridge_api_url}/get_disbursement_envelope_status"
        payload = {
            "signature": "string",
            "header": {
                "version": "1.0.0",
                "message_id": "string",
                "message_ts": "string",
                "action": "get_disbursement_envelope_status",
                "sender_id": "string",
                "sender_uri": "",
                "receiver_id": "",
                "total_count": 0,
                "is_msg_encrypted": False,
                "meta": "string"
            },
            "message": self.disbursement_envelope_id
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            api_response = response.json()
            _logger.info("API response: %s", api_response)
        except Exception as e:
            _logger.error("API call failed: %s", e)
            return

        message = api_response.get('message', {})
        # TODO: check if message is None
        self.disbursement_envelope_id = message.get('disbursement_envelope_id', self.disbursement_envelope_id)
        self.number_of_disbursements_received = message.get('number_of_disbursements_received', 0)
        self.total_disbursement_amount_received = f"{self.measurement_unit} {format(float(message.get('total_disbursement_amount_received', 0)), ',')}"
        self.funds_available_with_bank = message.get('funds_available_with_bank', '')
        self.funds_available_latest_timestamp = self._parse_datetime(message.get('funds_available_latest_timestamp'))
        self.funds_available_latest_error_code = message.get('funds_available_latest_error_code') if message.get('funds_available_latest_error_code') else 'No errors'
        self.funds_available_attempts = message.get('funds_available_attempts', 0)
        self.funds_blocked_with_bank = message.get('funds_blocked_with_bank', '')
        self.funds_blocked_latest_timestamp = self._parse_datetime(message.get('funds_blocked_latest_timestamp'))
        self.funds_blocked_latest_error_code = message.get('funds_blocked_latest_error_code') if message.get('funds_blocked_latest_error_code') else 'No errors'
        self.funds_blocked_attempts = message.get('funds_blocked_attempts', 0)
        self.funds_blocked_reference_number = message.get('funds_blocked_reference_number', '')
        self.number_of_disbursements_shipped = message.get('number_of_disbursements_shipped', 0)
        self.number_of_disbursements_reconciled = message.get('number_of_disbursements_reconciled', 0)
        self.number_of_disbursements_reversed = message.get('number_of_disbursements_reversed', 0)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.disbursement.envelope.summary.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    def reload_wizard(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
