# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
import qrcode
from odoo import http, api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime , timedelta
from io import BytesIO
import base64
import xlwt



class Lims_sample(models.Model):
	_inherit = 'lims.sample.main'

	def _get_default_session(self):
		employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		if len(employee):
			pos = self.env['pos.config'].search([('employee_ids','child_of',employee.id)],limit=1)
			session = self.env['pos.session'].search([('config_id','=',pos.id),('state','=','opened')],limit=1) if pos else False
			res = session.id if session else False
			return res

	invoicing_type = fields.Selection(selection_add=[('pos','POS Order')],default='pos')
	pos_order_id = fields.Many2one('pos.order','POS')
	session = fields.Many2one('pos.session',string='Session',default=_get_default_session)


	def action_confirm(self):
		if self.pos_order_id:
			self.state = 'confirm'
			self.qrcode = self.generate_qr_code(self.id)
			return self.state
		else:
			return super(Lims_sample, self).action_confirm()

	def _create_pos_order(self):
		if len(self.sample_line):
			order_line_vals = []
			vals = {'partner_id':self.partner_id.id,
					'date_order':self.date,
					'note':self.name,
					'company_id':self.company_id.id,
					'session_id': self.session.id,
					'fiscal_position_id': self.partner_id.property_account_position_id.id
						}
			for item in self.sample_line:
				for parameter in item.product_ids:
					order_line_vals.append((0,0,{
								   'product_id':parameter.id,
								   'full_product_name':parameter.description_sale or parameter.name,
								   'qty':item.quantity,
								   'price_subtotal':item.quantity*parameter.lst_price,
								   'price_subtotal_incl':0.0,
								   'price_unit':parameter.lst_price,
								   }))
			currency = self.env.company.currency_id
			vals.update({'lines':order_line_vals,
						  'amount_tax':0.0,
						  'amount_total':0.0,
						  'amount_paid':0.0,
						  'amount_return':0.0})
			# 
			pos_order = self.env['pos.order'].create(vals)
			for line in pos_order.lines:
				line._compute_amount_line_all()
			pos_order.sudo()._onchange_amount_all()
			self.pos_order_id = pos_order.id
			return self.action_view_pos_order()

		else:
				raise UserError(_(
					'Please fill your request line, then clic generate quotation'
				) )




	def generate_sale_order(self):
		res = super(Lims_sample, self).generate_sale_order()
		if self.invoicing_type == 'pos':
			res = self._create_pos_order()
		return  res


	def action_view_pos_order(self):
		sale_id = self.mapped('pos_order_id')
		action = self.env["ir.actions.actions"]._for_xml_id("point_of_sale.action_pos_order_filtered")
		if len(sale_id):
			form_view = [(self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')]
			if 'views' in action:
				action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
			else:
				action['views'] = form_view
			action['res_id'] = sale_id.id
		else:
			action = {'type': 'ir.actions.act_window_close'}

		context = {
			'default_company_id': self.env.company.id,
		}
		if len(self) == 1:
			context.update({
				'default_partner_id': self.partner_id.id,
				'default_note': self.name,
				'default_user_id': self.user_id.id,
			})
		action['context'] = context
		return action