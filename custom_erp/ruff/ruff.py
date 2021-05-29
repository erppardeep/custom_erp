import   frappe
import json
from frappe.client import attach_file
from frappe.integrations.oauth2 import get_token

@frappe.whitelist()
def get_customer_list_for_fse():
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"pppppppppppppppppppppppp ------ user: {frappe.session.user},,,, request  {data}")
	key_list=list(data.keys())
	if 'owner' in key_list:
		record=frappe.db.sql("""select DISTINCT * from `tabCustomer` where owner="{}" """.format(data['owner']), as_dict=1)
		if len(record)!=0:
			res =  {
				"status":"success",
				"message":"search successfully",
				"data":record
			}
		else:
			res =  {"message":"not found"}
	else:
		res = {"status":"failure"}

		resp = frappe._dict(res)
		frappe.local.response(resp)






@frappe.whitelist()
def customer_search():
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"pppppppppppppppppppppppp {data}")
	key_list=list(data.keys())
	if 'customer_name' in key_list:
		data=frappe.db.sql("""select DISTINCT * from `tabCustomer` where name="{}" """.format(data['customer_name']), as_dict=1)
		if len(data)!=0:
			res = {
				"status":"success",
				"message":"Search  successfully",
				"data":data
				}
		else:
			res = {"message":"Customer not Found"
				}

	else:
		res =  {
				"status":"failure",
				"message":"Not found",
				"data":[]
				}
		resp = frappe._dict(res)
		frappe.local.response(resp)



@frappe.whitelist()
def customer_status():
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"pppppppppppppppppppppppp {data}")
	key_list=list(data.keys())
	if 'customer_name' in key_list:
		data=frappe.db.sql("""select workflow_state from `tabCustomer` where name="{}" """.format(data['customer_name']), as_dict=1)

		if len(data)!=0:
			res = {
				"status":"success",
				"message":"Search  successfully",
				"data":data
				}
		else:
			res = {"message":"Customer not Found"
				}

	else:
		res =  {
				"message":"Not found"
				}
	resp = frappe._dict(res)
	frappe.local.response(resp)

@frappe.whitelist()
def create_user():
	frappe.logger().debug(f"**********************")
	#frappe.logger().debug(f"&&&&&&&&&&&&&&&&&&&&&& {frappe.request.data.keys}")
	data = json.loads(frappe.request.data)
	user=frappe.session.user
	frappe.logger().debug(f"user {user}")
	frappe.logger().debug(f"user dataaaaaaaaaaaaaa {data}")
	#frappe.logger().debug(f"rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr {data}")

	customer= frappe.get_doc({
		"doctype":"Customer",
		"customer_name":data['customer_name'],
		"customer_group":data['customer_type'],
		"customer_type":data['user_type'],
		"bank":data['bank'],
		"account_name":data['account_name'],
		"ifsc":data['ifsc'],
		"business_address":data['customer_address'],
		#"mobile_no":data['customer_mobile_no'],
	})

	try:
		customer.flags.ignore_permissions = True
		customer.insert()

	#except  Exception as e:
		#print(e.message)
		#errors=e.message
		#frappe.logger().debug(f"---------------------**************: {errors}")
		#frappe.log_error(frappe.get_traceback())
		#frappe.thow(frappe.get_traceback())
		#return {'message': e.message, 'error': True}

		customer_address=data['customer_address']
		response=customer
		#create_address(customer_address,response.name)
		create_contact(data['customer_mobile_no'],response.name)
	

		response=customer
		customer_address=data['customer_address']
		images=data['images']
		if len(images)==3:
			image1=images[0]
			image2=images[1]
			image3=images[2]
			attach_file(doctype="Customer",docname=response.name,filedata=image1['image'],filename="pan444444444.png",decode_base64="1",docfield="pan_image")
			attach_file(doctype="Customer",docname=response.name,filedata=image2['image'],filename="cheque.jpeg",decode_base64="1",docfield="cancelled_cheque")
			attach_file(doctype="Customer",docname=response.name,filedata=image3['image'],filename="id.jpeg",decode_base64="1",docfield="photo_id")

		elif len(images)==1:
			image1=images[0] 
			if image1['type']=="PAN":
				attach_file(doctype="Customer",docname=response.name,filedata=image1['image'],filename="pan444444444.png",decode_base64="1",docfield="pan_image")
			elif image1['type']=="Cancelled Cheque":
				attach_file(doctype="Customer",docname=response.name,filedata=image2['image'],filename="cheque.jpeg",decode_base64="1",docfield="cancelled_cheque")

			elif  image1['type']=="Photo ID":
				attach_file(doctype="Customer",docname=response.name,filedata=image3['image'],filename="id.jpeg",decode_base64="1",docfield="photo_id")



	except  Exception as e:
		#print(e.message)
		#errors=e.message
		#frappe.logger().debug(f"---------------------**************: {errors}")
		frappe.logger().debug(frappe.get_traceback())
		#frappe.thow(frappe.get_traceback())
		#return {'message': e.message, 'error': True}

	return customer


@frappe.whitelist()
def create_address(customer_address=None,name=None):
	if customer_address:
		customer_address=customer_address[0]
		address= frappe.get_doc({
			"doctype":"Address",
			"address_line1":customer_address['address_line1'],
			"state":customer_address['state'],
			"city":customer_address['city'],
			"pincode":customer_address['pincode'],
			"is_primary_address":1,
		})
		row =address.append("links", {})
		row.link_doctype="Customer"
		row.link_name=name
		address.flags.ignore_permissions = True
		address.insert()

@frappe.whitelist()
def create_contact(customer_mobile_no=None,name=None):
	if customer_mobile_no and name:
		contact= frappe.get_doc({
			"doctype":"Contact",
			"first_name":name,

		})
		row =contact.append("phone_nos", {})
		row.phone=customer_mobile_no
		row.is_primary_mobile_no=1
		row.is_primary_phone=1

		s=contact.append("links", {})
		s.link_doctype="Customer"
		s.link_name=name

		contact.flags.ignore_permissions = True
		contact.insert()



@frappe.whitelist()
def fsc_reassign(old_fse=None,new_fse=None):
	#frappe.logger().debug(f"**********************")
	#data = json.loads(frappe.request.data)
	#frappe.logger().debug(f"pppppppppppppppppppppppp {data}")
	frappe.db.sql(""" SET SQL_SAFE_UPDATES=0 """)
	frappe.db.sql("""UPDATE `tabCustomer` SET owner= "{}" WHERE owner="{}" """.format(new_fse,old_fse))
	frappe.db.sql(""" SET SQL_SAFE_UPDATES=1 """)
	frappe.db.commit()
	res = {"message": "your User reassignment successfully"}
	resp = frappe._dict(res)
	frappe.local.response(resp)





@frappe.whitelist()
def update_customer():
	frappe.logger().debug(f"**********************")
	#frappe.logger().debug(f"&&&&&&&&&&&&&&&&&&&&&& {frappe.request.data.keys}")
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"pppppppppppppppppppppppp {data}")
	#frappe.logger().debug(f"rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr {data}")

	

	try:
		customer=frappe.get_doc('Customer',data['customer_name'])
		if  bool(data['user_type'].strip())==True:
			customer.db_set("customer_type", data['user_type'], update_modified=False)
		if  bool(data['customer_type'].strip())==True:
			customer.db_set("customer_group", data['customer_type'], update_modified=False)

		if  bool(data['customer_mobile_no'].strip())==True:
			customer.db_set("mobile_no", data['customer_mobile_no'], update_modified=False)

		if  bool(data['customer_address'].strip())==True:
			customer.db_set("business_address", data['customer_address'], update_modified=False)

		if  bool(data['bank'].strip())==True:
			customer.db_set("bank", data['bank'], update_modified=False)

		if  bool(data['account_name'].strip())==True:
			customer.db_set("account_name", data['account_name'], update_modified=False)

		if  bool(data['ifsc'].strip())==True:
			customer.db_set("ifsc", data['ifsc'], update_modified=False)

		images=data['images']
		if len(images)==3:
			image1=images[0]
			image2=images[1]
			image3=images[2]
			attach_file(doctype="Customer",docname=customer.name,filedata=image1['image'],filename="pan444444444.png",decode_base64="1",docfield="pan_image")
			attach_file(doctype="Customer",docname=customer.name,filedata=image2['image'],filename="cheque.jpeg",decode_base64="1",docfield="cancelled_cheque")
			attach_file(doctype="Customer",docname=customer.name,filedata=image3['image'],filename="id.jpeg",decode_base64="1",docfield="photo_id")

		elif len(images)==1:
			image1=images[0] 
			if image1['type']=="PAN":
				attach_file(doctype="Customer",docname=customer.name,filedata=image1['image'],filename="pan444444444.png",decode_base64="1",docfield="pan_image")
			elif image1['type']=="Cancelled Cheque":
				attach_file(doctype="Customer",docname=customer.name,filedata=image2['image'],filename="cheque.jpeg",decode_base64="1",docfield="cancelled_cheque")

			elif  image1['type']=="Photo ID":
				attach_file(doctype="Customer",docname=customer.name,filedata=image3['image'],filename="id.jpeg",decode_base64="1",docfield="photo_id")

	except  Exception as e:
		frappe.logger().debug(frappe.get_traceback())

	return "updated successfully"
		


@frappe.whitelist()
def notification_log(for_user=None):
	session_user = frappe.session.user
	unread_notification_count = frappe.db.sql("""select count(*) from `tabNotification Log` where for_user="{}" AND `read` != 1 """.format(session_user))
	records =  frappe.db.sql("""select `name`, `creation`, `read`, `subject` from `tabNotification Log` where for_user="{}" """.format(session_user), as_dict=1)
	res = {"status":"success","unread_notification_count": unread_notification_count[0][0],"data":records}
	res = frappe._dict(res)
	frappe.local.response = res



@frappe.whitelist(allow_guest=True)
def custom_login(username=None,password=None):
	#s=[('grant_type', 'password'), ('username', 'administrator'), ('password', 'admin'), ('scope', 'all'), ('client_id', '0399ec04da')]
	response=get_token()
	return response


@frappe.whitelist(allow_guest=True)
def custom_refresh_token(refresh_token=None):
	#s=[('grant_type', 'password'), ('username', 'administrator'), ('password', 'admin'), ('scope', 'all'), ('client_id', '0399ec04da')]
	response=get_token()
	return response


@frappe.whitelist(allow_guest=True)
def create_fse_request():
	frappe.logger().debug(f"**********************")
	data = json.loads(frappe.request.data)
	frappe.logger().debug(f"pppppppppppppppppppppppp {data}")
	try:
		fscre= frappe.get_doc({
			"doctype":"FseRequest",
			"customer":data['customer'],
			"requester":data['requester'],
			"request_reason":data['request_reason'],
			})

		fscre.flags.ignore_permissions = True
		fscre.insert()
	except  Exception as e:
		frappe.logger().debug(frappe.get_traceback())
	res = {"message": "Created successfully"}	
	resp = frappe._dict(res)
	frappe.local.response(resp)



@frappe.whitelist(allow_guest=True)
def unrevoke_token(reuse_token=None):
	
	try:
		docs=frappe.get_doc('OAuth Bearer Token',reuse_token)
		docs.db_set("status","Active", update_modified=False)
		frappe.db.commit()

	except  Exception as e:
		frappe.logger().debug(frappe.get_traceback())

	res = {
			"message":"updated successfully",
			"status":"success"
			}
	resp = frappe._dict(res)
	frappe.local.response(resp)



@frappe.whitelist(allow_guest=True)
def set_role_field(doc,method):
	#return frappe.throw('hellllllllllllll')
	#print('aaaaaaaaaaaa')
	role=frappe.db.sql(""" select role from `tabHas Role` where role in ('Field Sales Executive','Finance','Blogger') and parent in (select name from `tabUser` where name="{}")  """.format(doc.name),as_dict=1)
	frappe.logger().debug(f"rolessssss {role}")
	print('roleeeeeeee',role)
	roles=[]
	for i in role:
		roles.append(i['role'])

	adds="\n".join(roles)
	doc.roles_all=adds
	docs=frappe.get_doc('User',doc.name)
	docs.db_set("roles_all",adds, update_modified=False)
	frappe.db.commit()
