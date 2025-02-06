from odoo import models, fields, api

from .registry import G2PRegistry


class G2PStudentRegistry(models.Model):
    _name = "g2p.student.registry"
    _description = "Student Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name", required=True)
    institution_name = fields.Char(string="Institution Name")
    date_of_birth = fields.Date(string="Date of Birth")
