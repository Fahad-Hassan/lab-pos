from odoo import api, fields, models, _
from odoo.tools import formatLang
from odoo.exceptions import ValidationError
from datetime import datetime , timedelta
import itertools
from itertools import groupby
import logging


_logger = logging.getLogger(__name__)


class PosPayment(models.Model):
    """ Used to register payments made in a pos.order.

    See `payment_ids` field of pos.order model.
    The main characteristics of pos.payment can be read from
    `payment_method_id`.
    """

    _inherit = "pos.payment"


    @api.model
    def create(self, vals):
        products_list = []      
        lines_ids = []
        result = super(PosPayment, self).create(vals)
        for p in result.pos_order_id.lines.mapped('product_id'):
            products_list.append((p.id,
                        p.default_sample_type.id))
        products_list = sorted(products_list, key=lambda x: x[1])
        for k, lines in itertools.groupby(products_list, key=lambda x: x[1]):
            
            product_ids = []
            for item in lines:
                product_ids.append(item[0])

            # _logger.info("oops:"+str(list(product_ids)))
            lines_ids.append((0,0,{
                    'sample': k,
                    'product_ids':[(6, 0, product_ids)],
                    'quantity':1,

                    }))
        order_id = vals['pos_order_id']
        order = self.env['pos.order'].search([('id','=',order_id)])
        values = {'invoicing_type':'pos',
                  'partner_id':order.partner_id.id,
                  'date':fields.datetime.now(),
                  #'planned_date':self.date,
                  'session':order.session_id.id,
                  'pos_order_id':order.id,
                  'company_id':self.env.company.id,
                  'origin':order.name,
                  'user_id':self.env.user.id,
                  'translation_template':self.env.company.translation_template.id,
                  'sample_line':lines_ids}

        request_id = self.env['lims.sample.main'].create(values)
        request_id.onchange_date()
        request_id.action_confirm()
        request_id.action_report_print_all_label()
        return result