# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import UserError, ValidationError


class ExtendsFinancieraPrestamo(models.Model):
	_inherit = 'financiera.prestamo' 
	_name = 'financiera.prestamo'

	@api.one
	def enviar_a_revision(self):
		if len(self.company_id.nosis_configuracion_id) > 0:
			nosis_configuracion_id = self.company_id.nosis_configuracion_id
			if nosis_configuracion_id.solicitar_informe_enviar_a_revision:
				self.partner_id.solicitar_informe_nosis()
		super(ExtendsFinancieraPrestamo, self).enviar_a_revision()
