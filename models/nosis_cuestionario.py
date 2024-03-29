# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import requests

ENDPOINT_NOSIS_VID = 'https://ws02.nosis.com/rest/evaluacion'

class FinancieraNosisCuestionario(models.Model):
	_name = 'financiera.nosis.cuestionario'
	
	_order = 'id desc'
	name = fields.Char('Nombre')
	partner_id = fields.Many2one('res.partner', 'Cliente')
	id_consulta = fields.Char('ID consulta')
	indice_consulta_actual = fields.Integer('Indice consulta actual')
	pregunta_ids = fields.One2many('financiera.nosis.cuestionario.pregunta', 'cuestionario_id', 'Preguntas')
	respuestas_test = fields.Char('Respuestas test')
	cuestionario = fields.Char('Respuestas', compute='_compute_cuestionario')
	state = fields.Selection([('pendiente', 'Pendiente'), ('rechazado', 'Rechazado'), ('aprobado', 'Aprobado')], string='Estado', default='pendiente')
	porcentaje = fields.Integer('Porcentaje')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.cuestionario'))
	
	@api.model
	def create(self, values):
		rec = super(FinancieraNosisCuestionario, self).create(values)
		id_cuestionario = self.env.user.company_id.nosis_configuracion_id.id_cuestionario
		rec.update({
			'name': 'NOSIS/CUESTIONARIO/' + str(id_cuestionario).zfill(8),
		})
		return rec

	@api.one
	def _compute_cuestionario(self):
		cuestionario = None
		for pregunta in self.pregunta_ids:
			if pregunta.id_respuesta >= 0:
				if cuestionario == None:
					cuestionario = str(pregunta.id_pregunta) + '-' + str(pregunta.id_respuesta)
				else:
					cuestionario += ',' + str(pregunta.id_pregunta) + '-' + str(pregunta.id_respuesta)
		self.cuestionario = cuestionario

	def get_cuestionario_to_dict(self):
		cuestionario_dict = {
			'id': self.id,
			'indice_consulta_actual': self.indice_consulta_actual,
			'cuestionario': self.cuestionario,
			'state': self.state,
			'porcentaje': self.porcentaje,
		}
		pregunta_list_dict = []
		for pregunta_id in self.pregunta_ids:
			pregunta_dict = {
				'id_pregunta': pregunta_id.id_pregunta,
				'id_respuesta': pregunta_id.id_respuesta,
				'texto': pregunta_id.texto,
			}
			opcion_list_dict = []
			for opcion_id in pregunta_id.opcion_ids:
				opcion_dict = {
					'id_opcion': opcion_id.id_opcion,
					'texto': opcion_id.texto,
					'respuesta': opcion_id.respuesta,
				}
				opcion_list_dict.append(opcion_dict)
			pregunta_dict['opcion_ids'] = opcion_list_dict
			pregunta_list_dict.append(pregunta_dict)
		cuestionario_dict['pregunta_ids'] = pregunta_list_dict
		return cuestionario_dict
	
	@api.one
	def button_get_cuestionario_to_dict(self):
		self.get_cuestionario_to_dict()

	@api.one
	def set_respuestas(self, cuestionario):
		if not (cuestionario and len(cuestionario.split(',')) == len(self.pregunta_ids)):
			raise ValidationError('Parece que no se respondio a todas las preguntas.')
		for respuesta in cuestionario.split(','):
			respuesta = respuesta.split('-')
			id_pregunta = int(respuesta[0])
			id_respuesta = int(respuesta[1])
			for pregunta_id in self.pregunta_ids:
				if pregunta_id.id_pregunta == id_pregunta:
					opcion_id = pregunta_id.opcion_ids[id_respuesta]
					opcion_id.set_opcion_correcta()
					break

	@api.one
	def button_set_respuestas(self):
		self.set_respuestas(self.respuestas_test)

	def evaluar_cuestionario_nosis(self, confirm_partner=False, validar_partner=False):
		if not (self.cuestionario and len(self.cuestionario.split(',')) == len(self.pregunta_ids)):
			raise ValidationError('Parece que no se respondio a todas las preguntas.')
		nosis_configuracion_id = self.company_id.nosis_configuracion_id
		params = {
			'usuario': nosis_configuracion_id.usuario,
			'token': nosis_configuracion_id.token,
			'IdConsulta': self.id_consulta,
			'cuestionario': self.cuestionario,
			'format': 'json',
		}
		response = requests.get(ENDPOINT_NOSIS_VID, params)
		data = response.json()
		if response.status_code != 200:
			raise ValidationError("Error en la obtencion del cuestionario Nosis: "+data['Contenido']['Resultado']['Novedad'])
		else:
			if data['Contenido']['Resultado']['Estado'] != 200:
				raise ValidationError("Nosis: " + data['Contenido']['Resultado']['Novedad'])
			if self.state == 'pendiente':
				self.porcentaje = data['Contenido']['Datos']['Cuestionario']['Porcentaje']
			self.state = data['Contenido']['Datos']['Cuestionario']['Estado'].lower()
			if confirm_partner:
				self.partner_id.confirm()
			if validar_partner and self.state == 'aprobado':
				self.partner_id.state = 'validated'
		return self.state

	@api.one
	def button_evaluar_cuestionario_nosis(self):
		self.evaluar_cuestionario_nosis()

	@api.multi
	def button_wizard_siguiente_pregunta(self):
		if self.pregunta_ids and len(self.pregunta_ids) > 0 and self.indice_consulta_actual < len(self.pregunta_ids):
			params = {
				'pregunta_id': self.pregunta_ids[self.indice_consulta_actual].id,
			}
			view_id = self.env['financiera.nosis.pregunta.wizard']
			new = view_id.create(params)
			return {
				'type': 'ir.actions.act_window',
				'name': 'Desafio',
				'res_model': 'financiera.nosis.pregunta.wizard',
				'view_type': 'form',
				'view_mode': 'form',
				'res_id': new.id,
				'view_id': self.env.ref('financiera_nosis.nosis_pregunta_wizard', False).id,
				'target': 'new',
			}
		else:
			raise UserError("Ya respondio a todas las preguntas.")

class FinancieraNosisCuestionarioPregunta(models.Model):
	_name = 'financiera.nosis.cuestionario.pregunta'
	
	cuestionario_id = fields.Many2one('financiera.nosis.cuestionario', 'Nosis cuestionario')
	opcion_ids = fields.One2many('financiera.nosis.cuestionario.pregunta.opcion', 'pregunta_id', 'Opciones')
	id_pregunta = fields.Integer('ID')
	id_respuesta = fields.Integer('ID Respuesta', default=-1)
	texto = fields.Char('Texto')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.cuestionario.pregunta'))
			
class FinancieraNosisCuestionarioPreguntaOpcion(models.Model):
	_name = 'financiera.nosis.cuestionario.pregunta.opcion'
	
	pregunta_id = fields.Many2one('financiera.nosis.cuestionario.pregunta', 'Pregunta')
	id_opcion = fields.Integer('ID')
	texto = fields.Char('Texto')
	respuesta = fields.Boolean('Respuesta')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.nosis.cuestionario.pregunta.opcion'))

	@api.one
	def set_opcion_correcta(self):
		if self.pregunta_id.id_respuesta >= 0:
			self.pregunta_id.opcion_ids[self.pregunta_id.id_respuesta].respuesta = False
		self.respuesta = True
		self.pregunta_id.id_respuesta = self.id_opcion

	@api.multi
	def wizard_set_opcion_correcta(self):
		self.set_opcion_correcta()
		return self.pregunta_id.cuestionario_id.button_wizard_siguiente_pregunta()
