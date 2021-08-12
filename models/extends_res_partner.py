# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import requests

ENDPOINT_NOSIS_VAR = 'https://ws01.nosis.com/rest/variables'
ENDPOINT_NOSIS_VID = 'https://ws02.nosis.com/rest/validacion'
class ExtendsResPartnerNosis(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	# Deprecated
	nosis_vi_identificacion = fields.Char('Nosis - Identificacion')
	nosis_vi_razonSocial = fields.Char('Nosis - Razon Social')
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
	nosis_ci_12m_sf_noPag_cant = fields.Char('Nosis - Cantidad Cheques sin fondo no pagados')
	nosis_ci_12m_sf_noPag_monto = fields.Char('Nosis - Monto Cheques sin fondo no pagados')
	nosis_cda_detalle = fields.Text('Nosis - CDA Detalle')
	nosis_cda_evaluado = fields.Integer('Nosis - CDA evaluado')
	# fin deprecated

	# Nueva integracion NOSIS
	nosis_informe_ids = fields.One2many('financiera.nosis.informe', 'partner_id', 'Nosis - Informes')
	nosis_variable_ids = fields.One2many('financiera.nosis.informe.variable', 'partner_id', 'Variables')
	nosis_capacidad_pago_mensual = fields.Float('Nosis - CPM', digits=(16,2))
	nosis_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Nosis - Tipo de cliente')
	# Validacion por cuestionario
	nosis_cuestionario_ids = fields.One2many('financiera.nosis.cuestionario', 'partner_id', 'Nosis - Cuestionarios')
	nosis_cuestionario_id = fields.Many2one('financiera.nosis.cuestionario', 'Nosis - Cuestionario actual')

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
		response = requests.get(ENDPOINT_NOSIS_VAR, params)
		data = response.json()
		if response.status_code != 200:
			raise ValidationError("Error en la consulta de informe Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			nuevo_informe_id = self.env['financiera.nosis.informe'].create({})
			self.nosis_informe_ids = [nuevo_informe_id.id]
			self.nosis_variable_ids = [(6, 0, [])]
			direccion = []
			direccion_variables = []
			if nosis_configuracion_id.asignar_direccion_cliente:
				if nosis_configuracion_id.asignar_calle_cliente_variable:
					direccion_variables.append(nosis_configuracion_id.asignar_calle_cliente_variable)
				if nosis_configuracion_id.asignar_nro_cliente_variable:
					direccion_variables.append(nosis_configuracion_id.asignar_nro_cliente_variable)
				if nosis_configuracion_id.asignar_piso_cliente_variable:
					direccion_variables.append(nosis_configuracion_id.asignar_piso_cliente_variable)
				if nosis_configuracion_id.asignar_departamento_cliente_variable:
					direccion_variables.append(nosis_configuracion_id.asignar_departamento_cliente_variable)
			for variable in data['Contenido']['Datos']['Variables']:
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
				if nosis_configuracion_id.asignar_nombre_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_nombre_cliente_variable:
						self.name = variable_valor
				if nosis_configuracion_id.asignar_direccion_cliente:
					if variable_nombre in direccion_variables:
						direccion.append(variable_valor)
				if nosis_configuracion_id.asignar_ciudad_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_ciudad_cliente_variable:
						self.city = variable_valor
				if nosis_configuracion_id.asignar_cp_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_cp_cliente_variable:
						self.zip = variable_valor
				if nosis_configuracion_id.asignar_provincia_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_provincia_cliente_variable:
						self.set_provincia(variable_valor)
				if nosis_configuracion_id.asignar_identificacion_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_identificacion_cliente_variable:
						self.main_id_number = variable_valor
				if nosis_configuracion_id.asignar_genero_cliente:
					if variable_nombre == nosis_configuracion_id.asignar_genero_cliente_variable:
						if variable_valor == 'M':
							self.sexo = 'masculino'
						elif variable_valor == 'F':
							self.sexo = 'femenino'
			if nosis_configuracion_id.asignar_direccion_cliente:
				if len(direccion) > 0:
					self.street = ' '.join(direccion)
			nosis_configuracion_id.id_informe += 1
			if nosis_configuracion_id.ejecutar_cda_al_solicitar_informe:
				nuevo_informe_id.ejecutar_cdas()

	@api.one
	def set_provincia(self, provincia):
		if provincia == 'Capital Federal':
			provincia = 'Ciudad Autónoma de Buenos Aires'
		state_obj = self.pool.get('res.country.state')
		state_ids = state_obj.search(self.env.cr, self.env.uid, [
			('name', '=ilike', provincia)
		])
		if len(state_ids) > 0:
			self.state_id = state_ids[0]
			country_id = state_obj.browse(self.env.cr, self.env.uid, state_ids[0]).country_id
			self.country_id = country_id.id

	@api.one
	def ejecutar_cdas_nosis(self):
		if self.nosis_informe_ids and len(self.nosis_informe_ids) > 0:
			self.nosis_informe_ids[0].ejecutar_cdas()

	@api.one
	def button_solicitar_informe_nosis(self):
		self.solicitar_informe_nosis()

	# funcion de API
	# @api.one
	def obtener_cuestionario_nosis(self):
		desafios = None
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'NroGrupoVID': nosis_configuracion_id.nro_grupo_vid,
			'documento': self.main_id_number,
			'format': 'json',
		}
		response = requests.get(ENDPOINT_NOSIS_VID, params)
		data = response.json()
		if response.status_code != 200:
			raise ValidationError("Error en la obtencion del cuestionario Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			if data['Contenido']['Resultado']['Estado'] != 200:
				raise ValidationError("Nosis: " + data['Contenido']['Resultado']['Novedad'])
			nuevo_cuestionario_id = self.env['financiera.nosis.cuestionario'].create({})
			nosis_configuracion_id.id_cuestionario += 1
			self.nosis_cuestionario_ids = [nuevo_cuestionario_id.id]
			self.nosis_cuestionario_id = nuevo_cuestionario_id.id
			nuevo_cuestionario_id.id_consulta = data['Contenido']['Datos']['IdConsulta']
			desafios = data['Contenido']['Datos']['Cuestionario']['Desafios']
			for desafio in desafios:
				if 'Pregunta' in desafio:
					pregunta = desafio['Pregunta']
					pregunta_id = self.env['financiera.nosis.cuestionario.pregunta'].create({
						'id_pregunta': pregunta['IdPregunta'],
						'texto': pregunta['Texto'],
					})
					nuevo_cuestionario_id.pregunta_ids = [pregunta_id.id]
					i = 0
					for opcion in pregunta['Opciones']:
						opcion_id = self.env['financiera.nosis.cuestionario.pregunta.opcion'].create({
							'id_opcion': i,
							'texto': opcion,
						})
						i += 1
						pregunta_id.opcion_ids = [opcion_id.id]
		return desafios

	@api.one
	def button_obtener_cuestionario_nosis(self):
		self.obtener_cuestionario_nosis()


