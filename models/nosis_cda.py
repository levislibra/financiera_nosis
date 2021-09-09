# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError

class FinancieraNosisCda(models.Model):
	_name = 'financiera.nosis.cda'

	_order = 'orden asc'
	name = fields.Char('Nombre')
	activo = fields.Boolean('Activo')
	orden = fields.Integer('Orden de ejecucion')
	otorgar_cpm_base = fields.Float('Nosis - CPM Base', digits=(16,2))
	otorgar_cpm_maximo = fields.Float('Nosis - CPM Maximo', digits=(16,2))
	otorgar_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Tipo de cliente')
	regla_ids = fields.One2many('financiera.nosis.cda.regla', 'nosis_cda_id', 'Reglas')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.configuracion'))
	
	def ejecutar(self, informe_id):
		ret = {'resultado': 'rechazado', 'cpm': 0, 'partner_tipo_id': None}
		cda_resultado_id = self.env['financiera.nosis.cda.resultado'].create({
			'name': self.name,
			'informe_id': informe_id,
			'otorgar_cpm': self.otorgar_cpm_base,
			'otorgar_cpm_maximo': self.otorgar_cpm_maximo,
			'otorgar_partner_tipo_id': self.otorgar_partner_tipo_id.id,
		})
		resultado = 'aprobado'
		for regla_id in self.regla_ids:
			regla_resultado_id = regla_id.copy()
			regla_resultado_id.nosis_cda_id = None
			regla_resultado_id.nosis_cda_resultado_id = cda_resultado_id.id
			regla_resultado_id.ejecutar(informe_id)
			if not regla_resultado_id.no_rechazar and regla_resultado_id.resultado == 'rechazado':
				resultado = 'rechazado'
			cda_resultado_id.regla_ids = [regla_resultado_id.id]
		cda_resultado_id.resultado = resultado
		if resultado == 'aprobado':
			otorgar_cpm = min(cda_resultado_id.otorgar_cpm, cda_resultado_id.otorgar_cpm_maximo)
			cda_resultado_id.otorgar_cpm = otorgar_cpm
			ret = {
				'resultado': 'aprobado',
				'cpm': otorgar_cpm,
				'partner_tipo_id': cda_resultado_id.otorgar_partner_tipo_id.id
			}
		return ret

class FinancieraNosisCdaResultado(models.Model):
	_name = 'financiera.nosis.cda.resultado'

	_order = 'id desc'
	name = fields.Char('Nombre')
	informe_id = fields.Many2one('financiera.nosis.informe', 'Informe')
	regla_ids = fields.One2many('financiera.nosis.cda.regla', 'nosis_cda_resultado_id', 'Reglas')
	otorgar_cpm = fields.Float('Nosis - CPM', digits=(16,2))
	otorgar_cpm_maximo = fields.Float('Nosis - CPM Maximo', digits=(16,2))
	otorgar_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Tipo de cliente')
	resultado = fields.Selection([('rechazado', 'Rechazado'), ('aprobado', 'Aprobado')], 'Resultado')

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
	no_rechazar = fields.Boolean('No rechazar Regla')
	cpm_multiplicar = fields.Float('CPM - Multiplicar base por', default=1.00)
	cpm_sumar = fields.Float('CPM - Sumar base')
	cpm_multiplicar_valor = fields.Float('CPM - Multiplicar valor por y sumar a base', default=0.00)
	# De resultado
	informe_valor	= fields.Char('Valor informe')
	resultado = fields.Selection([('rechazado', 'Rechazado'), ('aprobado', 'Aprobado')], 'Resultado')
	detalle = fields.Char('Detalle')

	@api.multi
	def ejecutar(self, informe_id):
		self.ensure_one()
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
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'no_contiene':
				if self.valor.upper() not in variable_id.valor.upper():
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'es_igual_a':
				if self.valor.upper() == variable_id.valor.upper():
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'no_es_igual_a':
				if self.valor.upper() != variable_id.valor.upper():
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'esta_establecida':
				if variable_id.valor:
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'no_esta_establecida':
				if not variable_id.valor:
					self.resultado = 'aprobado'
				else:
					self.resultado = 'rechazado'
			elif self.operador == 'mayor_que':
				if self.valor and self.valor.isdigit() and variable_id.valor and variable_id.valor.isdigit():
					if int(variable_id.valor) > int(self.valor):
						self.resultado = 'aprobado'
					else:
						self.resultado = 'rechazado'
				else:
					self.resultado = 'rechazado'
					self.detalle = 'Algun valor no es Int.'
			elif self.operador == 'menor_que':
				if self.valor and self.valor.isdigit() and variable_id.valor and variable_id.valor.isdigit():
					if int(variable_id.valor) < int(self.valor):
						self.resultado = 'aprobado'
					else:
						self.resultado = 'rechazado'
				else:
					self.resultado = 'rechazado'
					self.detalle = 'Algun valor no es Int.'
			elif self.operador == 'mayor_o_igual_que':
				if self.valor and self.valor.isdigit() and variable_id.valor and variable_id.valor.isdigit():
					if int(variable_id.valor) >= int(self.valor):
						self.resultado = 'aprobado'
					else:
						self.resultado = 'rechazado'
				else:
					self.resultado = 'rechazado'
					self.detalle = 'Algun valor no es Int.'
			elif self.operador == 'menor_o_igual_que':
				if self.valor and self.valor.isdigit() and variable_id.valor and variable_id.valor.isdigit():
					if int(variable_id.valor) <= int(self.valor):
						self.resultado = 'aprobado'
					else:
						self.resultado = 'rechazado'
				else:
					self.resultado = 'rechazado'
					self.detalle = 'Algun valor no es Int.'
			if self.resultado == 'aprobado':
				self.nosis_cda_resultado_id.otorgar_cpm *= self.cpm_multiplicar
				self.nosis_cda_resultado_id.otorgar_cpm += self.cpm_sumar
				if variable_id.valor and variable_id.valor.isdigit():
					self.nosis_cda_resultado_id.otorgar_cpm += int(variable_id.valor) * self.cpm_multiplicar_valor
