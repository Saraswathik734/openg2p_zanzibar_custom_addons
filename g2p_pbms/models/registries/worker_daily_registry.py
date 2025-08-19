from odoo import models, fields, api

class G2PWorkerDailyRegistry(models.Model):
    _name = "g2p.worker.daily.registry"
    _description = "Worker Daily Registry"

    unique_id = fields.Integer(string="Unique ID")

    nrc_number = fields.Char(string="NRC Number")
    attendance_date = fields.Date(string="Attendance Date")
    task = fields.Text(string="Task")