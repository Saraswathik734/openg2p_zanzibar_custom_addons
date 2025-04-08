from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class G2PDisbursementCycle(models.Model):
    _name = "g2p.disbursement.cycle"
    _description = "G2P Disbursement Cycle"
    _rec_name = "cycle_mnemonic"

    cycle_mnemonic = fields.Char(string="Cycle Mnemonic", required=True)
    pbms_request_id = fields.Char(string='PBMS Request ID')
    bridge_envelope_id = fields.Char(string='Bridge Envelope ID')
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program")
    envelope_creation_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Envelope Status",
        default="pending",
    )
    batch_creation_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Entitlement Process Status",
        default="not_applicable",
    )
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now, readonly=True)

    envelope_creation_latest_error_code = fields.Char(
        string="Envelope Creation Latest Error Code",
        help="Latest error code for envelope creation",
    )
    envelope_creation_attempts = fields.Integer(
        string="Envelope Creation Attempts", default=0
    )
    batch_creation_latest_error_code = fields.Char(
        string="Batch Creation Latest Error Code",
        help="Latest error code for batch creation",
    )
    batch_creation_attempts = fields.Integer(
        string="Batch Creation Attempts", default=0
    )
    disbursement_schedule_date = fields.Date(
        string="Disbursement Schedule Date", required=True
    )
    envelope_creation_latest_timestamp = fields.Datetime(
        string="Envelope Creation Latest Timestamp"
    )
    batch_creation_latest_timestamp = fields.Datetime(
        string="Batch Creation Latest Timestamp"
    )

    def _calculate_schedule_date(self, program):
        current_str = fields.Datetime.now()
        current = fields.Datetime.from_string(current_str)
        freq = program.disbursement_frequency

        if freq == 'Daily':
            return current.date()

        elif freq == 'Weekly':
            # Compute next occurrence based on configured day of week.
            weekday_mapping = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
                'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            target_weekday = weekday_mapping.get(program.disbursement_day_of_week)
            if target_weekday is None:
                return current.date()
            current_date = current.date()
            current_weekday = current_date.weekday()
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:
                days_ahead += 7
            next_date = current_date + datetime.timedelta(days=days_ahead)
            return next_date

        elif freq == 'Fortnightly':
            return (current + datetime.timedelta(days=14)).date()

        elif freq in ('Monthly', 'BiMonthly', 'Quarterly', 'SemiAnnually', 'Annually'):
            increment = 1
            if freq == 'BiMonthly':
                increment = 2
            elif freq == 'Quarterly':
                increment = 3
            elif freq == 'SemiAnnually':
                increment = 6
            elif freq == 'Annually':
                increment = 12

            # Use the disbursement_day_of_month from the program if set; otherwise, use current day.
            day = program.disbursement_day_of_month if program.disbursement_day_of_month else current.day
            try:
                candidate = current.replace(day=day)
                if candidate <= current:
                    candidate = (current + relativedelta(months=increment)).replace(day=day)
            except ValueError:
                # If the day is invalid, set to the last day of the month.
                candidate = (current + relativedelta(months=increment)).replace(day=1) + datetime.timedelta(days=-1)
            return candidate.date()

        elif freq == 'OnDemand':
            # For on-demand cycles, return current date.
            return current.date()

        else:
            return current.date()


    @api.model
    def create(self, vals):
        if not vals.get('disbursement_schedule_date') and vals.get('program_id'):
            program = self.env['g2p.program.definition'].browse(vals['program_id'])
            if self.program_id.beneficiary_list == 'labeled' and self.program_id.label_for_beneficiary_list_id:
                vals['pbms_request_id'] = self.program_id.label_for_beneficiary_list_id.pbms_request_id
            else:
                # Get the latest PBMS request ID from the program
                latest_request = self.env['g2p.que.eee.request'].search([
                    ('program_id', '=', program.id),
                    ('eligibility_process_status', '=', 'complete'),
                    ('entitlement_process_status', '=', 'complete')
                ], limit=1, order='creation_date desc')
                if latest_request:
                    vals['pbms_request_id'] = latest_request.pbms_request_id
                else:
                    # If no request found, raise an error or handle it as needed
                    raise ValueError("No eligible request found for the program.")
            calculated_date = self._calculate_schedule_date(program)
            if calculated_date:
                vals['disbursement_schedule_date'] = calculated_date
        return super(G2PDisbursementCycle, self).create(vals)

    
    def action_open_disbursement_envelope_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            'disbursement_envelope_id': self.bridge_envelope_id,
            "pbms_request_id": self.pbms_request_id,
            "program_mnemonic": self.program_id.program_mnemonic,
            "cycle_mnemonic": self.cycle_mnemonic,
        }

        wizard = self.env["g2p.disbursement.envelope.summary.wizard"].create(wizard_vals)
        return {
            "name": "G2P Disbursement Envelope Status Summary",
            "view_mode": "form",
            "res_model": "g2p.disbursement.envelope.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_disbursement_envelope_id': self.bridge_envelope_id,
                'default_pbms_request_id': self.pbms_request_id,
            },
        }
