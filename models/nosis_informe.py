# -*- coding: utf-8 -*-

from openerp import models, fields, api

class FinancieraNosisInforme(models.Model):
	_name = 'financiera.nosis.informe'
	
	_order = 'create_date desc'
	partner_id = fields.Many2one('res.partner', 'Cliente')
	# Validacion de identidad
	nosis_vi_identificacion = fields.Char('Identificacion')
	nosis_vi_razonSocial = fields.Char('Razon Social')
	# Resultado
	nosis_sco_vig = fields.Char('Scoring de Riesgo')
	nosis_sco_12m = fields.Char('Scoring de Riesgo 12m')
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
	# Nueva integracion
	variable_ids = fields.One2many('financiera.nosis.informe.variable', 'informe_id', 'Variables')
	cda_resultado_ids = fields.One2many('financiera.nosis.cda.resultado', 'informe_id', 'Resultados')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.informe'))
	
	@api.one
	def ejecutar_cdas(self):
		cda_obj = self.pool.get('financiera.nosis.cda')
		cda_ids = cda_obj.search(self.env.cr, self.env.uid, [
			('activo', '=', True),
			('company_id', '=', self.company_id.id),
		])
		for _id in cda_ids:
			cda_id = cda_obj.browse(self.env.cr, self.env.uid, _id)
			cda_id.ejecutar(self.id)
class FinancieraNosisInformeVariable(models.Model):
	_name = 'financiera.nosis.informe.variable'
	
	informe_id = fields.Many2one('financiera.nosis.informe', 'Informe')
	partner_id = fields.Many2one('res.partner', 'Cliente')
	name = fields.Char('Nombre')
	valor = fields.Char('Valor')
	fecha = fields.Date('Fecha')
	descripcion = fields.Char('Descripcion')
	tipo = fields.Char('Tipo')
	