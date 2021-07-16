# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import time
import requests

ENDPOINT_NOSIS = 'https://ws01.nosis.com/rest/variables'

class ExtendsResPartnerNosis(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	nosis_informe_ids = fields.One2many('financiera.nosis.informe', 'partner_id', 'Nosis - Informes')
	# Validacion de identidad
	nosis_vi_identificacion = fields.Char('Nosis - Identificacion')
	nosis_vi_razonSocial = fields.Char('Nosis - Razon Social')

	# Resumen
	nosis_sco_vig = fields.Char('Nosis - Scoring de Riesgo')
	nosis_sco_12m = fields.Char('Nosis - Scoring de Riesgo 12m')
	nosis_cda = fields.Char('Nosis - Criterio de Aceptacion')
	nosis_cda_evaluar = fields.Integer('Nosis - Nro de CDA a evaluar')	

	nosis_ci_vig_peorSit = fields.Integer('Nosis - Peor Situacion Bancaria')
	nosis_ci_vig_total_cantBcos = fields.Integer('Nosis - Cant. de bancos y ent. fin. vigentes')
	nosis_ci_vig_total_monto = fields.Integer('Nosis - Monto en bancos y ent. fin. vigentes')
	nosis_ci_vig_sit1_monto = fields.Integer('Monto en sit. 1')
	nosis_ci_vig_sit2_monto = fields.Integer('Monto en sit. 2')
	nosis_ci_vig_sit3_monto = fields.Integer('Monto en sit. 3')
	nosis_ci_vig_sit4_monto = fields.Integer('Monto en sit. 4')
	nosis_ci_vig_sit5_monto = fields.Integer('Monto en sit. 5')
	nosis_ci_vig_sit6_monto = fields.Integer('Monto en sit. 6')
	# nosis_ci_vig_detalle_porEntidad = fields.Char('Identificacion')
	nosis_ci_12m_sf_noPag_cant = fields.Char('Nosis - Cantidad Cheques sin fondo no pagados')
	nosis_ci_12m_sf_noPag_monto = fields.Char('Nosis - Monto Cheques sin fondo no pagados')
	# nosis CDA
	nosis_cda_detalle = fields.Text('Nosis - CDA Detalle')
	nosis_cda_evaluado = fields.Integer('Nosis - CDA evaluado')
	nosis_variable_ids = fields.One2many('financiera.nosis.informe.variable', 'partner_id', 'Variables')
	nosis_capacidad_pago_mensual = fields.Float('Nosis - CPM', digits=(16,2))
	nosis_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Nosis - Tipo de cliente')


	@api.one
	def solicitar_informe_nosis(self):
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'documento': self.main_id_number, 
			'vr': nosis_configuracion_id.vr,
			'format': 'json',
		}
		response = requests.get(ENDPOINT_NOSIS, params)
		data = response.json()
		if response.status_code != 200:
			raise ValidationError("Error en la consulta de informe Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			nuevo_informe_id = self.env['financiera.nosis.informe'].create({})
			self.nosis_informe_ids = [nuevo_informe_id.id]
			self.nosis_variable_ids = [(6, 0, [])]
			for variable in data['Contenido']['Datos']['Variables']:
				print("variable keys: ", variable.keys())
				variable_nombre = variable['Nombre']
				variable_valor = variable['Valor']
				variable_fecha = None
				if 'FechaAct' in variable:
					variable_fecha = variable['FechaAct']
				variable_descripcion = variable['Descripcion']
				variable_tipo = variable['Tipo']
				variable_id = self.env['financiera.nosis.informe.variable'].create({
					'partner_id': self.id,
					'name': variable_nombre,
					'valor': variable_valor,
					'fecha': variable_fecha,
					'descripcion': variable_descripcion,
					'tipo': variable_tipo,
				})
				nuevo_informe_id.variable_ids = [variable_id.id]

	@api.one
	def asignar_cpm_y_tipo_cliente_nosis(self):
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		self.capacidad_pago_mensual = 0
		self.partner_tipo_id = None
		for line in nosis_configuracion_id.score_ids:
			if self.nosis_vi_identificacion and self.nosis_sco_vig:
				score = int(self.nosis_sco_vig)
				cda_check = line.cda_resultado == 'no_controlar'
				cda_check = cda_check or (line.cda_resultado == 'aprobado' and self.nosis_cda == 'Aprobado')
				cda_check = cda_check or (line.cda_resultado == 'aprobado_bueno' and (self.nosis_cda == 'Aprobado' or self.nosis_cda == 'Bueno'))
				if cda_check:
					score_inicial_check = line.score_inicial == -1 or score >= line.score_inicial
					score_final_check = line.score_final == -1 or score <= line.score_final
					score_check = score_inicial_check and score_final_check
					if score_check:
						monto_deuda_inicial_check = line.nosis_ci_vig_total_monto_inicial == -1 or self.nosis_ci_vig_total_monto >= line.nosis_ci_vig_total_monto_inicial
						monto_deuda_final_check = line.nosis_ci_vig_total_monto_final == -1 or self.nosis_ci_vig_total_monto <= line.nosis_ci_vig_total_monto_final
						monto_deuda_check = monto_deuda_inicial_check and monto_deuda_final_check
						if monto_deuda_check:
							if nosis_configuracion_id.asignar_capacidad_pago_mensual:
								self.nosis_capacidad_pago_mensual = line.capacidad_pago_mensual
								self.capacidad_pago_mensual = self.nosis_capacidad_pago_mensual
							if nosis_configuracion_id.asignar_partner_tipo:
								self.nosis_partner_tipo_id = line.partner_tipo_id.id
								self.partner_tipo_id = self.nosis_partner_tipo_id.id
							break

	@api.one
	def button_solicitar_informe_nosis(self):
		self.solicitar_informe_nosis()

	@api.one
	def asignar_identidad_nosis(self):
		if self.nosis_vi_identificacion != False:
			self.main_id_number = self.nosis_vi_identificacion
		if self.nosis_vi_razonSocial != False:
			self.name = self.nosis_vi_razonSocial
		self.confirm()

