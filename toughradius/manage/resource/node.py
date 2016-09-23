#!/usr/bin/env python
#coding=utf-8

import cyclone.auth
import cyclone.escape
import cyclone.web

from toughradius.manage import models
from toughradius.manage.base import BaseHandler
from toughradius.manage.resource import node_forms
from toughlib.permit import permit
from toughlib import utils
from toughradius.manage.settings import * 

@permit.route(r"/admin/node", u"区域节点管理",MenuRes, order=1.0000, is_menu=True)
class NodeListHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        nodes = self.db.query(models.TrNode)
        return self.render('node_list.html',nodes=nodes)

@permit.route(r"/admin/node/add", u"新增区域", MenuRes, order=1.0001)
class NodeAddHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        form = node_forms.node_add_form()
        self.render("base_form.html", form=form)

    @cyclone.web.authenticated
    def post(self):
        form = node_forms.node_add_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)

        node = models.TrNode()
        node.node_name = form.d.node_name
        node.node_desc = form.d.node_desc
        self.db.add(node)

        self.add_oplog(u'新增区域信息:%s' % utils.safeunicode(form.d.node_name))

        self.db.commit()

        self.redirect("/admin/node",permanent=False)

@permit.route(r"/admin/node/update", u"修改区域", MenuRes, order=1.0002)
class NodeUpdateHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        node_id = self.get_argument("node_id")
        form = node_forms.node_update_form()
        node = self.db.query(models.TrNode).get(node_id)
        form.fill(node)
        self.render("base_form.html", form=form)

    @cyclone.web.authenticated
    def post(self):
        form = node_forms.node_update_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)
        node = self.db.query(models.TrNode).get(form.d.id)
        node.node_name = form.d.node_name
        node.node_desc = form.d.node_desc

        self.add_oplog(u'修改区域信息:%s' % utils.safeunicode(form.d.node_name))

        self.db.commit()

        self.redirect("/admin/node",permanent=False)


@permit.route(r"/admin/node/delete", u"删除区域", MenuRes, order=1.0003)
class NodeDeleteHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        node_id = self.get_argument("node_id")
        if self.db.query(models.TrCustomer.customer_id).filter_by(node_id=node_id).count() > 0:
            return render("error", msg=u"该节点下有用户，不允许删除")
            
        self.db.query(models.TrNode).filter_by(id=node_id).delete()

        self.add_oplog(u'删除区域信息:%s' % node_id)

        self.db.commit()

        self.redirect("/admin/node",permanent=False)




