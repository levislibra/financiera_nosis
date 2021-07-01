# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import UserError, ValidationError


class ExtendsFinancieraPrestamo(models.Model):
	_inherit = 'financiera.prestamo' 
	_name = 'financiera.prestamo'

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
	nosis_capacidad_pago_mensual = fields.Float('Nosis - CPM', digits=(16,2))
	nosis_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Nosis - Tipo de cliente')

	def pass_var_partner_to_prestamo(self):
		if self.partner_id.nosis_vi_identificacion:
			self.nosis_vi_identificacion = self.partner_id.nosis_vi_identificacion
			self.nosis_vi_razonSocial = self.partner_id.nosis_vi_razonSocial

			self.nosis_sco_vig = self.partner_id.nosis_sco_vig
			self.nosis_sco_12m = self.partner_id.nosis_sco_12m
			self.nosis_cda = self.partner_id.nosis_cda
			self.nosis_cda_evaluar = self.partner_id.nosis_cda_evaluar

			self.nosis_ci_vig_peorSit = self.partner_id.nosis_ci_vig_peorSit
			self.nosis_ci_vig_total_cantBcos = self.partner_id.nosis_ci_vig_total_cantBcos
			self.nosis_ci_vig_total_monto = self.partner_id.nosis_ci_vig_total_monto
			self.nosis_ci_vig_sit1_monto = self.partner_id.nosis_ci_vig_sit1_monto
			self.nosis_ci_vig_sit2_monto = self.partner_id.nosis_ci_vig_sit2_monto
			self.nosis_ci_vig_sit3_monto = self.partner_id.nosis_ci_vig_sit3_monto
			self.nosis_ci_vig_sit4_monto = self.partner_id.nosis_ci_vig_sit4_monto
			self.nosis_ci_vig_sit5_monto = self.partner_id.nosis_ci_vig_sit5_monto
			self.nosis_ci_vig_sit6_monto = self.partner_id.nosis_ci_vig_sit6_monto

			self.nosis_ci_12m_sf_noPag_cant = self.partner_id.nosis_ci_12m_sf_noPag_cant
			self.nosis_ci_12m_sf_noPag_monto = self.partner_id.nosis_ci_12m_sf_noPag_monto

			self.nosis_cda_detalle = self.partner_id.nosis_cda_detalle
			self.nosis_cda_evaluado = self.partner_id.nosis_cda_evaluado
			self.nosis_capacidad_pago_mensual = self.partner_id.nosis_capacidad_pago_mensual
			self.nosis_partner_tipo_id = self.partner_id.nosis_partner_tipo_id

	@api.model
	def _cron_actualizar_var_nosis_prestamo(self):
		cr = self.env.cr
		uid = self.env.uid
		prestamo_obj = self.pool.get('financiera.prestamo')
		prestamo_ids = prestamo_obj.search(cr, uid, [
			('nosis_vi_identificacion', '=', False),
			('partner_id.nosis_vi_identificacion', '!=', False)])
		for _id in prestamo_ids:
			prestamo_id = prestamo_obj.browse(cr, uid, _id)
			prestamo_id.pass_var_partner_to_prestamo()

	@api.one
	def enviar_a_acreditacion_pendiente(self):
		super(ExtendsFinancieraPrestamo, self).enviar_a_acreditacion_pendiente()
		self.pass_var_partner_to_prestamo()