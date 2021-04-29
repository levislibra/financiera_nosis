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
	fecha_desde = fields.Date("Actualizar informes desde")
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

	@api.one
	def actualizar_cda_partners(self):
		if self.fecha_desde == False:
			raise ValidationError("Debe definir la fecha desde")
		informe_obj = self.pool.get('financiera.nosis.informe')
		informe_ids = informe_obj.search(self.env.cr, self.env.uid, [
			('create_date', '>=', self.fecha_desde),
			('company_id', '=', self.company_id.id)])
		for _id in informe_ids:
			informe_id = self.env['financiera.nosis.informe'].browse(_id)
			partner_id = informe_id.partner_id
			partner_id.asignar_cpm_y_tipo_cliente_nosis()
			print("actualizamos:", partner_id.name)
			print("actualizamos:", informe_id.create_date)
		self.fecha_desde = False

class FinancieraNosisScore(models.Model):
	_name = 'financiera.nosis.score'

	_order = 'orden asc'
	configuracion_id = fields.Many2one('financiera.nosis.configuracion', "Configuracion Nosis")
	orden = fields.Integer('Orden', help='Orden de ejecucion. De 1 a 999, siendo 1 de mayor prioridad.')
	cda_resultado = fields.Selection([
		('no_controlar','No controlar'),
		('aprobado','Aprobado'),
		('aprobado_bueno','Aprobado y Bueno')], "CDA", default='no_controlar')
	score_inicial = fields.Integer('Score inicial', default=-1)
	score_final = fields.Integer('Score final', default=-1)
	nosis_ci_vig_total_monto_inicial = fields.Integer('Monto en bancos y ent. fin. inicial', default=-1)
	nosis_ci_vig_total_monto_final = fields.Integer('Monto en bancos y ent. fin. final', default=-1)
	capacidad_pago_mensual = fields.Float('Capcidad de pago mensual asignada', digits=(16,2))
	partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Tipo de cliente')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.score'))

class ExtendsResCompany(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	nosis_configuracion_id = fields.Many2one('financiera.nosis.configuracion', 'Configuracion Nosis')
