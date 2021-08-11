# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError

class FinancieraPrestamoVentaCobrarWizard(models.TransientModel):
	_name = 'financiera.nosis.pregunta.wizard'

	pregunta_id = fields.Many2one('financiera.nosis.cuestionario.pregunta', 'Pregunta')
	opcion_ids = fields.One2many(related='pregunta_id.opcion_ids')
	id_respuesta = fields.Integer(related='pregunta_id.id_respuesta')
	texto = fields.Char('Texto', related='pregunta_id.texto')

	@api.multi
	def siguiente_pregunta(self):
		if self.id_respuesta >= 0:
			self.pregunta_id.cuestionario_id.indice_consulta_actual += 1
			return self.pregunta_id.cuestionario_id.button_wizard_siguiente_pregunta()
		else:
			raise UserError("Debe elegir una opcion.")