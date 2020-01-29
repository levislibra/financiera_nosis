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

class ExtendsResPartnerRol(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	nosis_informe_ids = fields.One2many('financiera.nosis.informe', 'partner_id', 'Informes')
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
	nosis_ci_12m_sf_noPag_cant = fields.Char('Cantidad Cheques sin fondo no pagados')
	nosis_ci_12m_sf_noPag_monto = fields.Char('Monto Cheques sin fondo no pagados')

	@api.one
	def solicitar_informe_nosis(self, cda=None):
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'documento': self.main_id_number, 
			'vr': VARIABLES_NOSIS,
			'format': 'json',
		}
		# if cda == None:
		# 	cda = nosis_configuracion_id.get_nosis_cda_segun_entidad(self.nosis_entidad_id)[0]
		# if cda != None:
		# 	params['cda'] = cda
		
		response = requests.get(ENDPOINT_NOSIS, params)
		data = response.json()
		if response.status_code != 200:
			print("CODE != 200")
			print("RESPONSE", response)
			raise ValidationError("Error en la consulta de informe Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			fni_values = {}
			for variable in data['Contenido']['Datos']['Variables']:
				print("VARIABLE: ", variable)
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

			nuevo_informe_id = self.env['financiera.nosis.informe'].create(fni_values)
			self.nosis_informe_ids = [nuevo_informe_id.id]

	@api.one
	def asignar_identidad_nosis(self):
		if self.nosis_vi_identificacion != False:
			self.main_id_number = self.nosis_vi_identificacion
		if self.nosis_vi_razonSocial != False:
			self.name = self.nosis_vi_razonSocial

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



# class ExtendsFinancieraPrestamo(models.Model):
# 	_name = 'financiera.prestamo'
# 	_inherit = 'financiera.prestamo'

# 	@api.one
# 	def enviar_a_revision(self):
# 		if len(self.company_id.rol_configuracion_id) > 0:
# 			rol_configuracion_id = self.company_id.rol_configuracion_id
# 			rol_active = rol_configuracion_id.get_rol_active_segun_entidad(self.sucursal_id)[0]
# 			rol_modelo = rol_configuracion_id.get_rol_modelo_segun_entidad(self.sucursal_id)[0]
# 			if len(self.comercio_id) > 0:
# 				rol_active = rol_configuracion_id.get_rol_active_segun_entidad(self.comercio_id)[0]
# 				rol_modelo = rol_configuracion_id.get_rol_modelo_segun_entidad(self.comercio_id)[0]
# 			if rol_active:
# 				dias_vovler_a_consultar = rol_configuracion_id.dias_vovler_a_consultar
# 				consultar_distinto_modelo = rol_configuracion_id.consultar_distinto_modelo
# 				rol_dias = False
# 				if self.partner_id.rol_fecha_informe != False and dias_vovler_a_consultar > 0:
# 					fecha_inicial = datetime.strptime(str(self.partner_id.rol_fecha_informe), '%Y-%m-%d %H:%M:%S')
# 					fecha_final = datetime.now()
# 					diferencia = fecha_final - fecha_inicial
# 					if diferencia.days >= dias_vovler_a_consultar:
# 						rol_dias = True
# 				else:
# 					rol_dias = True
				
# 				rol_distinto_modelo = consultar_distinto_modelo and (rol_modelo != self.partner_id.rol_experto_codigo)
# 				if rol_dias or rol_distinto_modelo:
# 					self.partner_id.solicitar_informe(rol_modelo)
# 				else:
# 					self.partner_id.consultar_informe()
# 		super(ExtendsFinancieraPrestamo, self).enviar_a_revision()
