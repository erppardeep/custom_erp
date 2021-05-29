from __future__ import unicode_literals
import hashlib
import frappe
import requests
import frappe, re
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from erpnext.stock.doctype.serial_no.serial_no import auto_fetch_serial_number
import  ast
import json

@frappe.whitelist()
def get_warehouse_filter(doctype, txt, searchfield, page_len, start, filters):
	if not filters: filters={}
	return frappe.db.sql("""select name from `tabWarehouse` where warehouse_type="{}"   """.format(filters.get("warehouse")))
    
@frappe.whitelist()
def autoname(doc,method):
	#doc.name = make_autoname(doc.item +'-'+ doc.warehouse)
	doc.name=doc.item +'/'+ doc.warehouse+'/' +doc.warehouse_type


@frappe.whitelist()
def id_fetch(product_store=None):
	if product_store:
		return frappe.db.sql("""select * from `tabProduct Store` where name="{}"   """.format(product_store),as_dict=1)



@frappe.whitelist()
def create_delivery_note():
	#frappe.logger().debug(f"checklist: {so_list}")
	#so_list=ast.literal_eval(so_list)\
	import json
	frappe.logger().debug(f"------------- in frappe creta deliver note")
	data = json.loads(frappe.request.data)
	#data =  json.load( frappe.request.data)
	frappe.logger().debug(f"---------------------**************: {data}")
	#return  so_list
	from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
	so = frappe.get_doc(make_delivery_note(data['so_name']))
	try:
		so_obj=so.insert()
	except  Exception as e:
		#so_obj.cancel()
		if hasattr(e, 'message'):
			return {'message': e.message, 'error': True}
		else:
			return {'message': e, 'error': True}


	#s_no=ast.literal_eval(so_list[''])
	s_no=data['serial_no']
	data=[]
	for  i in  s_no:
		n=i[0]
		try:
			code=frappe.db.sql("""select item_code from `tabSerial No` where name="{}"  """.format(n),as_dict=1)
			s={}
			s[code[0]['item_code']]=i
			data.append(s)
		except Exception as e:
			#so_obj.cancel()
			if hasattr(e, 'message'):
				return {'message': e.message, 'error': True}
			else:
				return {'message': e, 'error': True}


	for  i in  data:
		for k,v in  i.items():
			va='\n'.join(v)
			for m in   so_obj.items:
				if m.item_code ==k:
					print('ss')
					m.serial_no=va

	try:
		so.submit()
	except Exception  as e:
		so.cancel()
		if hasattr(e, 'message'):
			return {'message': e.message, 'error': True}
		else:
			return {'message': e, 'error': True}
	json={
		"status": "Success",
		"message": "Delivery Note created successfully",
		"delivery_note":so_obj.name
	}
	return  json




#create create stock entry for Wastage Stock
@frappe.whitelist(allow_guest=True)
def create_se_wastage_stock(unused=None):
	import json
	frappe.logger().debug(f"------------- in frappe creta deliver note")
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"---------------------**************: {data}")
	if unused==None:
		serial_no=data['serial_no']
		se= frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type":"Wastage Stock",
		})
	else:
		serial_no=unused['serial_no']
		se= frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type":"Unused Serial Number",
		})


	#row =se.append("items", {})
	for i in serial_no:
		row =se.append("items", {})
		n=i[0]
		s_list=i
		iw=frappe.db.sql("""select item_code,warehouse from `tabSerial No` where name="{}"  """.format(n),as_dict=1)
		row.item_code=iw[0]['item_code']
		row.s_warehouse=iw[0]['warehouse']
		row.qty=len(i)
		row.serial_no='\n'.join(i)

	se.flags.ignore_permissions = True
	try:
		se_obj=se.insert()
		#se.submit()
	except Exception  as e:
		#se.cancel()
		if hasattr(e, 'message'):
			return {'message': e.message, 'error': True}
		else:
			return {'message': e, 'error': True}
	try:
		se.submit()
	except Exception  as e:
		se.cancel()
		if hasattr(e, 'message'):
			return {'message': e.message, 'error': True}
		else:
			return {'message': e, 'error': True}


	json={
		"status": "Success",
		"message": "Stock Entry created successfully",
		"stock_entry":se_obj.name
	}

	return  json


@frappe.whitelist(allow_guest=True)
def  update_weight_st():
	data = json.loads(frappe.request.data)
	d=data['data'][0]['serial_numbers']
	f_serial_no=[]
	f_so=[]
	f_so.append(f_serial_no)
	f_dict={}
	f_dict['serial_no']=f_so
	for i in  d:
		if i['status']==True:
			s_no= frappe.get_doc("Serial No",i['serial_no'])
			s_no.db_set("net_weight",i['weight'], update_modified=False)
		else:
			f_serial_no.append(i['serial_no'])
	
	if len(f_serial_no)!=0:
		ws=create_se_wastage_stock(f_dict)

	output={
                "status": "Success",
                "message": "Updated Net Weight and Stock Entry",
                #"stock_entry":ws,

		}
	
	return  output

			
					
@frappe.whitelist(allow_guest=True)
def create_issue():
	data = json.loads(frappe.request.data)
	mobile_no=data['mobile_no']
	email_id=frappe.db.sql("""select email_id,mobile_no,name  from `tabCustomer` where mobile_no="{}"  """.format(mobile_no),as_dict=1)
	if len(email_id)==0:
		return  "Customer have no emial_id and mobile_no"
	issue= frappe.get_doc({
		"doctype": "Issue",
		"agreement_status":"Ongoing",
		"company":"Anirit",
		"customer":email_id[0]['name'],
		"issue_type":data['type'],
		"status":"Open",
		"subject":data['subject'],
		"raised_by":email_id[0]['email_id'],
		"priority":"Medium",
		"description":data['description'],
		"sales_order":data['sales_order_id']
	})

	issue.flags.ignore_permissions = True
	issue.insert()
	result={
                "status": "Success",
                "message": "Issue  created successfully",
		}
	
	return result
