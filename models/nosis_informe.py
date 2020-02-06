# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from datetime import date
from openerp.exceptions import UserError, ValidationError
import time
import requests

ENDPOINT_NOSIS = 'https://ws01.nosis.com/rest/variables'
VARIABLES_NOSIS = 'VI_Identificacion,VI_RazonSocial,CI_Vig_PeorSit,CI_Vig_Total_CantBcos,CI_Vig_Total_Monto,CI_Vig_Sit1_Monto,CI_Vig_Sit2_Monto,CI_Vig_Sit3_Monto,CI_Vig_Sit4_Monto,CI_Vig_Sit5_Monto,CI_Vig_Sit6_Monto,CI_Vig_Detalle_PorEntidad,HC_12m_SF_NoPag_Cant,HC_12m_SF_NoPag_Monto,SCO_12m,CDA'

class ExtendsResPartnerNosis(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	nosis_informe_ids = fields.One2many('financiera.nosis.informe', 'partner_id', 'Informes')
	# Validacion de identidad
	nosis_vi_identificacion = fields.Char('Identificacion')
	nosis_vi_razonSocial = fields.Char('Razon Social')

	# Resumen
	nosis_sco_12m = fields.Char('Scoring de Riesgo')
	nosis_cda = fields.Char('Criterio de Aceptacion')
	nosis_cda_evaluar = fields.Integer('Nro de CDA a evaluar')	

	nosis_ci_vig_peorSit = fields.Integer('Peor Situacion Bancaria')
	nosis_ci_vig_total_cantBcos = fields.Integer('Cantidad de bancos y ent. fin. vigentes')
	nosis_ci_vig_total_monto = fields.Integer('Monto en todos los bancos y ent. fin. vigentes')
	nosis_ci_vig_sit1_monto = fields.Integer('Monto en sit. 1')
	nosis_ci_vig_sit2_monto = fields.Integer('Monto en sit. 2')
	nosis_ci_vig_sit3_monto = fields.Integer('Monto en sit. 3')
	nosis_ci_vig_sit4_monto = fields.Integer('Monto en sit. 4')
	nosis_ci_vig_sit5_monto = fields.Integer('Monto en sit. 5')
	nosis_ci_vig_sit6_monto = fields.Integer('Monto en sit. 6')
	# nosis_ci_vig_detalle_porEntidad = fields.Char('Identificacion')
	nosis_ci_12m_sf_noPag_cant = fields.Char('Cantidad Cheques sin fondo no pagados')
	nosis_ci_12m_sf_noPag_monto = fields.Char('Monto Cheques sin fondo no pagados')
	# nosis CDA
	nosis_cda_detalle = fields.Text('CDA Detalle')
	nosis_cda_evaluado = fields.Integer('CDA evaluado')
	nosis_capacidad_pago_mensual = fields.Float('Nosis - Capacidad de pago mensual', digits=(16,2))

	@api.one
	def solicitar_informe_nosis(self, cda=0):
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'documento': self.main_id_number, 
			'vr': VARIABLES_NOSIS,
			'format': 'json',
		}
		if cda != 0:
			params['cda'] = cda
			self.nosis_cda_evaluado = cda
		
		response = requests.get(ENDPOINT_NOSIS, params)
		data = response.json()
		if response.status_code != 200:
			raise ValidationError("Error en la consulta de informe Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			fni_values = {}
			nosis_cda_detalle = "<ul>"
			for variable in data['Contenido']['Datos']['Variables']:
				if variable['Nombre'] == 'VI_Identificacion':
					fni_values['nosis_vi_identificacion'] = variable['Valor']
					self.nosis_vi_identificacion = variable['Valor']

				if variable['Nombre'] == 'VI_RazonSocial':
					fni_values['nosis_vi_razonSocial'] = variable['Valor']
					self.nosis_vi_razonSocial = variable['Valor']

				if variable['Nombre'] == 'SCO_12m':
					fni_values['nosis_sco_12m'] = variable['Valor']
					self.nosis_sco_12m = variable['Valor']

				if variable['Nombre'] == 'CDA':
					fni_values['nosis_cda'] = variable['Valor']
					self.nosis_cda = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_PeorSit':
					fni_values['nosis_ci_vig_peorSit'] = variable['Valor']
					self.nosis_ci_vig_peorSit = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Total_CantBcos':
					fni_values['nosis_ci_vig_total_cantBcos'] = variable['Valor']
					self.nosis_ci_vig_total_cantBcos = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Total_Monto':
					fni_values['nosis_ci_vig_total_monto'] = variable['Valor']
					self.nosis_ci_vig_total_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit1_Monto':
					fni_values['nosis_ci_vig_sit1_monto'] = variable['Valor']
					self.nosis_ci_vig_sit1_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit2_Monto':
					fni_values['nosis_ci_vig_sit2_monto'] = variable['Valor']
					self.nosis_ci_vig_sit2_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit3_Monto':
					fni_values['nosis_ci_vig_sit3_monto'] = variable['Valor']
					self.nosis_ci_vig_sit3_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit4_Monto':
					fni_values['nosis_ci_vig_sit4_monto'] = variable['Valor']
					self.nosis_ci_vig_sit4_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit5_Monto':
					fni_values['nosis_ci_vig_sit5_monto'] = variable['Valor']
					self.nosis_ci_vig_sit5_monto = variable['Valor']

				if variable['Nombre'] == 'CI_Vig_Sit6_Monto':
					fni_values['nosis_ci_vig_sit6_monto'] = variable['Valor']
					self.nosis_ci_vig_sit6_monto = variable['Valor']

				if variable['Nombre'] == 'HC_12m_SF_NoPag_Cant':
					fni_values['nosis_ci_12m_sf_noPag_cant'] = variable['Valor']
					self.nosis_ci_12m_sf_noPag_cant = variable['Valor']

				if variable['Nombre'] == 'HC_12m_SF_NoPag_Monto':
					fni_values['nosis_ci_12m_sf_noPag_monto'] = variable['Valor']
					self.nosis_ci_12m_sf_noPag_monto = variable['Valor']

				if variable['Nombre'] == 'CDA':
					fni_values['nosis_cda'] = variable['Valor']
					self.nosis_cda = variable['Valor']

				if 'CDA_' in variable['Nombre']:
					if variable['Valor'] == 'N/C':
						nosis_cda_detalle += '<li style="background-color: #E0E5E1">'
					if variable['Valor'] == 'Ok':
						nosis_cda_detalle += '<li style="background-color: #33A8FF">'
					if variable['Valor'] == 'No':
						nosis_cda_detalle += '<li style="background-color: #DC3B3E">'
					nosis_cda_detalle += variable['Descripcion']+': '+variable['Valor']+'</li>'

			if len(nosis_cda_detalle) > 5:
				nosis_cda_detalle += '</ul>'
				fni_values['nosis_cda_evaluado'] = cda
				fni_values['nosis_cda_detalle'] = nosis_cda_detalle
				self.nosis_cda_detalle = nosis_cda_detalle
			nuevo_informe_id = self.env['financiera.nosis.informe'].create(fni_values)
			self.nosis_informe_ids = [nuevo_informe_id.id]
		self.nosis_capacidad_pago_mensual = nosis_configuracion_id.get_capacidad_pago_mensual_segun_score(int(self.nosis_sco_12m))
		if self.nosis_cda == 'Aprobado':
			if nosis_configuracion_id.asignar_capacidad_pago_mensual:
				self.capacidad_pago_mensual = self.nosis_capacidad_pago_mensual
		else:
			if nosis_configuracion_id.asignar_capacidad_pago_mensual:
				self.capacidad_pago_mensual = 0

	@api.one
	def button_solicitar_informe_nosis(self):
		self.solicitar_informe_nosis(self.nosis_cda_evaluar)

	@api.one
	def asignar_identidad_nosis(self):
		if self.nosis_vi_identificacion != False:
			self.main_id_number = self.nosis_vi_identificacion
		if self.nosis_vi_razonSocial != False:
			self.name = self.nosis_vi_razonSocial
		self.confirm()

class FinancieraNosisInforme(models.Model):
	_name = 'financiera.nosis.informe'
	
	_order = 'create_date desc'
	partner_id = fields.Many2one('res.partner', 'Cliente')
	# Validacion de identidad
	nosis_vi_identificacion = fields.Char('Identificacion')
	nosis_vi_razonSocial = fields.Char('Razon Social')

	# Resultado
	nosis_sco_12m = fields.Char('Scoring de Riesgo')
	nosis_cda = fields.Char('Criterio de Aceptacion')

	nosis_ci_vig_peorSit = fields.Integer('Peor Situacion Bancaria')
	nosis_ci_vig_total_cantBcos = fields.Integer('Cantidad de bancos y ent. fin. vigentes')
	nosis_ci_vig_total_monto = fields.Integer('Monto en todos los bancos y ent. fin. vigentes')
	nosis_ci_vig_sit1_monto = fields.Integer('Monto en sit. 1')
	nosis_ci_vig_sit2_monto = fields.Integer('Monto en sit. 2')
	nosis_ci_vig_sit3_monto = fields.Integer('Monto en sit. 3')
	nosis_ci_vig_sit4_monto = fields.Integer('Monto en sit. 4')
	nosis_ci_vig_sit5_monto = fields.Integer('Monto en sit. 5')
	nosis_ci_vig_sit6_monto = fields.Integer('Monto en sit. 6')
	# nosis_ci_vig_detalle_porEntidad = fields.Char('Identificacion')
	nosis_ci_12m_sf_noPag_cant = fields.Integer('Cantidad Cheques sin fondo no pagados')
	nosis_ci_12m_sf_noPag_monto = fields.Integer('Monto Cheques sin fondo no pagados')
	# CDA
	nosis_cda_detalle = fields.Text('CDA Detalle')
	nosis_cda_evaluado = fields.Integer('CDA evaluado')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.informe'))

class ExtendsFinancieraPrestamoNosis(models.Model):
	_name = 'financiera.prestamo'
	_inherit = 'financiera.prestamo'

	@api.one
	def enviar_a_revision(self):
		if len(self.company_id.nosis_configuracion_id) > 0:
			nosis_configuracion_id = self.company_id.nosis_configuracion_id
			nosis_active = nosis_configuracion_id.get_active_segun_entidad(self.sucursal_id)
			nosis_cda = nosis_configuracion_id.get_cda_segun_entidad(self.sucursal_id)
			if len(self.comercio_id) > 0:
				nosis_active = nosis_configuracion_id.get_active_segun_entidad(self.comercio_id)
				nosis_cda = nosis_configuracion_id.get_cda_segun_entidad(self.comercio_id)
			if nosis_active:
				self.partner_id.solicitar_informe_nosis(nosis_cda)
		super(ExtendsFinancieraPrestamoNosis, self).enviar_a_revision()
