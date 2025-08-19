from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PProgramBenefitCodes(models.Model):
    _name = "g2p.program.benefit.codes"
    _description = "Program Benefit Codes"
    _table = "g2p_program_benefit_codes"

    program_id = fields.Many2one(
        'g2p.program.definition',
        string="Program",
        required=True,
        ondelete='cascade',
        help="The program this benefit code is associated with."
    )
    benefit_code_id = fields.Many2one(
        'g2p.benefit.codes',
        string="Benefit Code",
        required=True,
        help="Select the benefit code for this program."
    )
    max_quantity = fields.Float(
        string="Maximum Quantity",
        required=True,
        help="Maximum quantity allowed for this benefit code in the program."
    )

    # Related fields from benefit_code_id
    benefit_mnemonic = fields.Char(
        related='benefit_code_id.benefit_mnemonic',
        string="Benefit Mnemonic",
        store=True,
        readonly=True
    )
    benefit_type = fields.Selection(
        related='benefit_code_id.benefit_type',
        string="Benefit Type",
        store=True,
        readonly=True
    )
    measurement_unit = fields.Char(
        related='benefit_code_id.measurement_unit',
        string="Measurement Unit",
        store=True,
        readonly=True
    )
    benefit_description = fields.Text(
        related='benefit_code_id.benefit_description',
        string="Benefit Description",
        store=True,
        readonly=True
    )

    _sql_constraints = [
        (
            "unique_program_benefit_code",
            "unique(program_id, benefit_code_id)",
            "Each benefit code can only be assigned once per program."
        )
    ]

