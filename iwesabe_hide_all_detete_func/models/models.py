# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False,
                        submenu=False):
        res = super(Base, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=False)
        # print('gggggg')
        doc = etree.XML(res['arch'])
        if view_type == 'kanban':
            nodes = doc.xpath("//kanban")
            for node in nodes:
                node.set('delete', '0')
            res['arch'] = etree.tostring(doc)
        if view_type == 'tree':
            nodes = doc.xpath("//tree")
            for node in nodes:
                node.set('delete', '0')
            res['arch'] = etree.tostring(doc)
        if view_type == 'form':
            nodes = doc.xpath("//form")
            for node in nodes:
                node.set('delete', '0')
            res['arch'] = etree.tostring(doc)
        return res
