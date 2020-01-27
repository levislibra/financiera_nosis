# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class financiera_nosis(models.Model):
#     _name = 'financiera_nosis.financiera_nosis'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100