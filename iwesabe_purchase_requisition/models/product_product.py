# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = 'product.product'


    def name_get(self):
        result = []

        for this in self:
            name_result = super(ProductProduct, this).name_get()
            return_val_split = name_result[0][1].split()
            for element in return_val_split:
                if element == "[%s]" % this.default_code:
                    return_val_split.remove(element)
                result.append((this.id, ' '.join(return_val_split)))
        return result
