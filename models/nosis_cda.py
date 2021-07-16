# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError

class FinancieraNosisCda(models.Model):
	_name = 'financiera.nosis.cda'

	_order = 'id desc'
	name = fields.Char('Nombre')
	activo = fields.Boolean('Activo')
	orden = fields.Integer('Orden de ejecucion')
	regla_ids = fields.One2many('financiera.nosis.cda.regla', 'nosis_cda_id', 'Reglas')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.configuracion'))
	
	def ejecutar(self, informe_id):
		cda_resultado_id = self.env['financiera.nosis.cda.resultado'].create({
			'name': self.name,
			'informe_id': informe_id,
		})
		for regla_id in self.regla_ids:
			regla_resultado_id = regla_id.copy()
			regla_resultado_id.nosis_cda_id = None
			regla_resultado_id.ejecutar(informe_id)
			cda_resultado_id.regla_ids = [regla_resultado_id.id]

class FinancieraNosisCdaResultado(models.Model):
	_name = 'financiera.nosis.cda.resultado'

	order = 'id desc'
	name = fields.Char('Nombre')
	informe_id = fields.Many2one('financiera.nosis.informe', 'Informe')
	regla_ids = fields.One2many('financiera.nosis.cda.regla', 'nosis_cda_resultado_id', 'Reglas')

class FinancieraNosisCdaRegla(models.Model):
	_name = 'financiera.nosis.cda.regla'

	nosis_cda_id = fields.Many2one('financiera.nosis.cda', 'CDA Evaluacion')
	nosis_cda_resultado_id = fields.Many2one('financiera.nosis.cda.resultado', 'CDA Resultado')
	variable = fields.Char('Variable')
	operador = fields.Selection([
		('contiene', 'contiene'),
		('no_contiene', 'no contiene'),
		('es_igual_a', 'es igual a'),
		('no_es_igual_a', 'no es igual a'),
		('esta_establecida', 'esta establecida(o)'),
		('no_esta_establecida', 'no esta establecida(o)'),
		('mayor_que', 'mayor que'),
		('menor_que', 'menor que'),
		('mayor_o_igual_que', 'mayor o igual que'),
		('menor_o_igual_que', 'menor o igual que')
	], 'Condicion')
	valor = fields.Char('Valor')
	informe_valor	= fields.Char('Valor informe')
	resultado = fields.Char('Resultado', help='Aprobado o Rechazado')

	@api.one
	def ejecutar(self, informe_id):
		variable_obj = self.pool.get('financiera.nosis.informe.variable')
		variable_ids = variable_obj.search(self.env.cr, self.env.uid, [
			('informe_id', '=', informe_id),
			('name', '=', self.variable),
		])
		if len(variable_ids) > 0:
			variable_id = variable_obj.browse(self.env.cr, self.env.uid, variable_ids[0])
			self.informe_valor = variable_id.valor
			if self.operador == 'contiene':
				if self.valor.upper() in variable_id.valor.upper():
					self.resultado = 'Aprobado'
				else:
					self.resultado = 'Rechazado'
			if self.operador == 'no_contiene':
				if self.valor.upper() not in variable_id.valor.upper():
					self.resultado = 'Aprobado'
				else:
					self.resultado = 'Rechazado'
