# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError
import time
import requests

ENDPOINT_NOSIS = 'https://ws01.nosis.com/rest/variables'

class FinancieraNosisConfiguracion(models.Model):
	_name = 'financiera.nosis.configuracion'

	name = fields.Char('Nombre')
	usuario = fields.Char('Usuario')
	token = fields.Char('Token')
	
	asignar_capacidad_pago_mensual = fields.Boolean('Asignar capacidad de pago mensual automaticamente')
	asignar_partner_tipo = fields.Boolean('Asignar tipo de cliente automaticamente')
	asginar_solo_cda_aprobado = fields.Boolean('Asignar CPM o Tipo de cliente solo a CDA aprobado')
	solicitar_informe_enviar_a_revision = fields.Boolean('Solicitar informe al enviar a revision')
	vr = fields.Integer('Grupo de variables')
	score_ids = fields.One2many('financiera.nosis.score', 'configuracion_id', 'Asignacion de CPM segun CDA')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.configuracion'))
	
	@api.one
	def test_conexion(self):
		params = {
			'usuario': self.usuario,
			'token': self.token,
		}
		response = requests.get(ENDPOINT_NOSIS, params)
		if response.status_code == 400:
			raise UserError("La cuenta esta conectada.")
		else:
			raise UserError("Error de conexion.")

	def get_capacidad_pago_mensual_segun_score(self, score):
		result = 0
		for line in self.score_ids:
			if score >= line.score_inicial and score <= line.score_final:
				result = line.capacidad_pago_mensual
				break
		return result

	def get_partner_tipo_segun_score(self, score):
		result = 0
		for line in self.score_ids:
			if score >= line.score_inicial and score <= line.score_final:
				result = line.partner_tipo_id.id
				break
		return result

class FinancieraNosisScore(models.Model):
	_name = 'financiera.nosis.score'

	configuracion_id = fields.Many2one('financiera.nosis.configuracion', "Configuracion Nosis")
	score_inicial = fields.Integer('Score inicial')
	score_final = fields.Integer('Score final')
	capacidad_pago_mensual = fields.Float('Capcidad de pago mensual asignada', digits=(16,2))
	partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Tipo de cliente')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.score'))

class ExtendsResCompany(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	nosis_configuracion_id = fields.Many2one('financiera.nosis.configuracion', 'Configuracion Nosis')
