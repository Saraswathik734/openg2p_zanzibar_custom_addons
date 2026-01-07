from odoo import models, fields, api

class ResPartnerRelatives(models.Model):
    _inherit = 'res.partner'

    nominee_image = fields.Image(
        string="Relative / Nominee Photo",
        max_width=1024,
        max_height=1024,
        store=True
    )
    zan_image = fields.Image(
        string="Zan ID Photo",
        max_width=1024,
        max_height=1024,
        store=True
    )




    