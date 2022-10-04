# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import requests

ENDPOINT_NOSIS_VAR = 'https://ws01.nosis.com/rest/variables'
ENDPOINT_NOSIS_VID = 'https://ws02.nosis.com/rest/validacion'
class ExtendsResPartnerNosis(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	# Nueva integracion NOSIS
	nosis_contratado = fields.Boolean('Nosis', compute='_compute_nosis_contrtado')
	nosis_informe_ids = fields.One2many('financiera.nosis.informe', 'partner_id', 'Nosis - Informes')
	nosis_variable_ids = fields.One2many('financiera.nosis.informe.variable', 'partner_id', 'Variables')
	nosis_variable_1 = fields.Char('Variable 1')
	nosis_variable_2 = fields.Char('Variable 2')
	nosis_variable_3 = fields.Char('Variable 3')
	nosis_variable_4 = fields.Char('Variable 4')
	nosis_variable_5 = fields.Char('Variable 5')
	nosis_capacidad_pago_mensual = fields.Float('Nosis - CPM', digits=(16,2))
	nosis_partner_tipo_id = fields.Many2one('financiera.partner.tipo', 'Nosis - Tipo de cliente')
	# Validacion por cuestionario
	nosis_cuestionario_ids = fields.One2many('financiera.nosis.cuestionario', 'partner_id', 'Nosis - Cuestionarios')
	nosis_cuestionario_id = fields.Many2one('financiera.nosis.cuestionario', 'Nosis - Cuestionario actual')

	@api.one
	def _compute_nosis_contrtado(self):
		self.nosis_contratado = True if self.company_id.nosis_configuracion_id else False

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
			list_values = []
			for variable in data['Contenido']['Datos']['Variables']:
				variable_nombre = variable['Nombre']
				variable_valor = variable['Valor']
				variable_fecha = None
				if 'FechaAct' in variable:
					variable_fecha = variable['FechaAct']
				variable_descripcion = variable['Descripcion']
				variable_tipo = variable['Tipo']
				variable_values = {
					'partner_id': self.id,
					'name': variable_nombre,
					'valor': variable_valor,
					'fecha': variable_fecha,
					'descripcion': variable_descripcion,
					'tipo': variable_tipo,
				}
				list_values.append((0,0, variable_values))
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
			nuevo_informe_id.write({'variable_ids': list_values})
			self.asignar_variables_nosis()
			if nosis_configuracion_id.asignar_direccion_cliente:
				if len(direccion) > 0:
					self.street = ' '.join(direccion)
			nosis_configuracion_id.id_informe += 1
			if nosis_configuracion_id.ejecutar_cda_al_solicitar_informe:
				nuevo_informe_id.ejecutar_cdas()

	@api.one
	def asignar_variables_nosis(self):
		variable_1 = False
		variable_2 = False
		variable_3 = False
		variable_4 = False
		variable_5 = False
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		for var_id in self.nosis_variable_ids:
			if var_id.name == nosis_configuracion_id.nosis_variable_1:
				variable_1 = var_id.name + ": " + str(var_id.valor)
			if var_id.name == nosis_configuracion_id.nosis_variable_2:
				variable_2 = var_id.name + ": " + str(var_id.valor)
			if var_id.name == nosis_configuracion_id.nosis_variable_3:
				variable_3 = var_id.name + ": " + str(var_id.valor)
			if var_id.name == nosis_configuracion_id.nosis_variable_4:
				variable_4 = var_id.name + ": " + str(var_id.valor)
			if var_id.name == nosis_configuracion_id.nosis_variable_5:
				variable_5 = var_id.name + ": " + str(var_id.valor)
		self.write({
			'nosis_variable_1': variable_1,
			'nosis_variable_2': variable_2,
			'nosis_variable_3': variable_3,
			'nosis_variable_4': variable_4,
			'nosis_variable_5': variable_5,
		})

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

	def obtener_cuestionario_nosis(self):
		ret = False
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		grupoVid = nosis_configuracion_id.nro_grupo_vid
		if len(self.nosis_cuestionario_id) > 0:
			grupoVid = nosis_configuracion_id.nro_grupo_vid2
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'NroGrupoVID': grupoVid,
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
			ret = nuevo_cuestionario_id.id
		return ret

	@api.one
	def button_obtener_cuestionario_nosis(self):
		self.obtener_cuestionario_nosis()

	@api.multi
	def nosis_report(self):
		self.ensure_one()
		return self.env['report'].get_action(self, 'financiera_nosis.nosis_report_view')