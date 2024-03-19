from flask import request, jsonify
from flask_restx import Resource, Namespace, fields,reqparse
from .models import EppsHrEmpMst
from .serializer import EppsModuleMstSchema,EppsMiscMstSchema,EppsLocationMstSchema,EppsMmGroupMstSchema,EppsFinyrMstSchema,EppsDivisionMstSchema, EmployeeSerializer,EppsEcodeMstSchema,EppsDeptMstSerializer,EppsCityMstSerializer,EppsCurrencyMstSerializer,EppsSdCustomerMstSchema
from .models import db
from .models import EppsMmSubSubGroupMst, EppsMmSubGroupMst,EppsStageMst,EppsRoleMst,EppsRoleProgLnk,EppsProgMst,EppsMiscMst,EppsModuleMst,EppsMmItemMst,EppsMmGroupMst,EppsFinyrMst,EppsHrEmpMst,EppsDivisionMst,VAuditTrailYn,EppsDeptMst,EppsLocationMst, EppsHrProjectResLnk,EppsBusinessZoneMst,EppsEcodeMst,EppsCityMst,EppsSdCustomerMst,EppsCompanyMst,EppsCurrencyMst
from datetime import datetime
from flask import Flask
from flask_jwt_extended import create_access_token, jwt_required,create_refresh_token

import bcrypt

ns = Namespace("employee", description="Employee Master API Details")

@ns.route("/v1/divisions")

class EppsHrEmpMstView(Resource):
    @jwt_required()
    @ns.doc(description='Endpoint to get employee details', params={
        'companyCode': 'Company Code',
        'divisionCode': 'Division Code',
        'employeeCode': 'provide Employee Code',
        'emailid': 'provide Email Id',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'employeeType': 'provide employee Type',
        'reportingEmpCode': 'provide Reporting employee code',
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        employee_code = request.args.get('employeeCode')
        emailid = request.args.get('emailid')
        is_active = request.args.get('isActive', None)
        employeeType = request.args.get('employeeType')
        reportingEmpCode = request.args.get('reportingEmpCode')



        total_records = EppsHrEmpMst.query.count()

        offset = (page - 1) * per_page

        query = EppsHrEmpMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if employee_code:
            query = query.filter_by(emp_cd=employee_code)
        if emailid:
            query = query.filter_by(emp_mail_id=emailid)
        if is_active is not None:
            query = query.filter(EppsHrEmpMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
        if employeeType:
            query = query.filter_by(emp_type=employeeType)
        if reportingEmpCode:
            emp_codes = [res.emp_cd for res in EppsHrProjectResLnk.query.filter_by(reporting_empcd=reportingEmpCode).all()]
            query = query.filter(EppsHrEmpMst.emp_cd.in_(emp_codes))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'company_code': link.comp_cd,
                'division_code': link.div_cd,
                'emp_cd' : link.emp_cd,
                'emp_title' : link.emp_title,
                'emp_first_name' : link.emp_first_name,
                'emp_middle_name' : link.emp_middle_name,
                'emp_last_name': link.emp_last_name,
                'emp_category': link.emp_category,
                'emp_desig' : link.emp_desig,
                'emp_qualification' : link.emp_qualification,
                'isActive':link.active_yn,
                'emailId':link.emp_mail_id,
                'emp_password':link.emp_password
            })

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns.route("/v1/<int:divisionCode>/<string:employeeCode>")
class EppsHrEmpMstViewByDivision(Resource):
    @jwt_required()
    @ns.doc(description='Endpoint to get employee details',
            params={'companyCode': 'Company Code', 'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
                    'auditTrailYn': 'AuditTrailYn Flag (0/1)', 'employeeType': 'Employee Type',
                    'reporting2EmpCode': 'Reporting Employee Code','divisionCode': 'Division Code','employeeCode': 'provide employee code'})
    # @ns.expect(filter_model)
    def get(self, divisionCode,employeeCode):
        try:
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_type = request.args.get('employeeType')
            is_active = request.args.get('isActive')
            reporting2EmpCode =  request.args.get('reporting2EmpCode')

            query = EppsHrEmpMst.query.filter_by(div_cd=divisionCode)
            query = EppsHrEmpMst.query.filter_by(emp_cd=employeeCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if is_active is not None:
                query = query.filter(EppsHrEmpMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if reporting2EmpCode is not None:
                query = query.filter_by(comp_cd=reporting2EmpCode)

            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EmployeeSerializer(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_employee_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })

        except Exception as e:
            print("Error:", str(e))
            return {'message': 'Internal Server Error'}, 500

@ns.route("/v1/<int:divisionCode>")
class EppsHrEmpMstViewByDivision(Resource):
    @jwt_required()
    @ns.doc(description='Endpoint to get employee details',
            params={'companyCode': 'Company Code', 'employeeCode': 'Employee Code','isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
                    'auditTrailYn': 'AuditTrailYn Flag (0/1)', 'employeeType': 'Employee Type',
                    'reporting2EmpCode': 'Reporting Employee Code', 'partnerCode': 'Partner Code',
                    'locationCodes': 'Location Codes', 'rootBtCode': 'Root Business Code',
                    'rootRoleCode': 'Root Role Code', 'isForBtEmp': 'Is for Business Employee',
                    'loginEmpCode': 'Login Employee Code', 'rolesReqFlag': 'Roles Required Flag (0/1)',
                    'isGchinfo': 'GCH Info Flag (0/1)', 'parentEmployee': 'Parent Employee',
                    'paginationSearchVO': 'Pagination Search VO', 'divisionCode': 'Division Code'})
    # @ns.expect(filter_model)
    def get(self, divisionCode):
        try:
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')
            employee_type = request.args.get('employeeType')
            partner_code = request.args.get('partnerCode')
            location_code = request.args.get('locationCodes')
            root_role_code = request.args.get('rootRoleCode')
          

            query = EppsHrEmpMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsHrEmpMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if partner_code is not None:
                query = query.filter_by(partner_cd=partner_code)
            if location_code is not None:
                query = query.filter_by(partner_loc_cd=location_code)
            if root_role_code is not None:
                query = query.filter_by(role_cd=root_role_code)
            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EmployeeSerializer(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_employee_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })

        except Exception as e:
            print("Error:", str(e))
            return {'message': 'Internal Server Error'}, 500

@ns.route("/v1/info")
class EppsHrEmpMstView(Resource):
    @jwt_required()
    @ns.doc(description='Endpoint to get employee details', params={
        'companyCode': 'Company Code',
        'divisionCode': 'Division Code',
        'employeeCode': 'provide Employee Code',
        'emailid': 'provide Email Id',
        'roleCode': 'provide role code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        employee_code = request.args.get('employeeCode')
        emailid = request.args.get('emailid')
        roleCode = request .args.get('roleCode')
        is_active = request.args.get('isActive', None)



        total_records = EppsHrEmpMst.query.count()

        offset = (page - 1) * per_page

        query = EppsHrEmpMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if employee_code:
            query = query.filter_by(emp_cd=employee_code)
        if emailid:
            query = query.filter_by(emp_mail_id=emailid)
        if roleCode:
            query = query.filter_by(role_cd=roleCode)
        if is_active is not None:
            query = query.filter(EppsHrEmpMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
        
        business_zone_mst_pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in business_zone_mst_pagination:
            result.append({
                'company_code': link.comp_cd,
                'division_code': link.div_cd,
                'emp_cd' : link.emp_cd,
                'emp_title' : link.emp_title,
                'emp_first_name' : link.emp_first_name,
                'emp_middle_name' : link.emp_middle_name,
                'emp_last_name': link.emp_last_name,
                'emp_category': link.emp_category,
                'emp_desig' : link.emp_desig,
                'emp_qualification' : link.emp_qualification,
                'isActive':link.active_yn,
                'emailId':link.emp_mail_id,
                'role_code': link.role_cd
            })

        return jsonify({
            'hr/employee/mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns.route("/v1/validate/email")
class EppsHrEmpMstView(Resource):
    @jwt_required()
    @ns.doc(description='Endpoint to get employee details', params={
        'companyCode': 'Company Code',
        'divisionCode': 'Division Code',
        'emailid': 'provide Email Id',
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        emailid = request.args.get('emailid')



        total_records = EppsHrEmpMst.query.count()

        offset = (page - 1) * per_page

        query = EppsHrEmpMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if emailid:
            query = query.filter_by(emp_mail_id=emailid)
        
        business_zone_mst_pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in business_zone_mst_pagination:
            result.append({
                'company_code': link.comp_cd,
                'division_code': link.div_cd,
                'emp_cd' : link.emp_cd,
                'emp_title' : link.emp_title,
                'emp_first_name' : link.emp_first_name,
                'emp_middle_name' : link.emp_middle_name,
                'emp_last_name': link.emp_last_name,
                'emp_category': link.emp_category,
                'emp_desig' : link.emp_desig,
                'emp_qualification' : link.emp_qualification,
                'isActive':link.active_yn,
                'emailId':link.emp_mail_id,
                'role_code': link.role_cd
            })

        return jsonify({
            'hr/employee/mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
# from .dto import employee_dto
employee_dto = ns.model('EmployeeDTO', {
    'companyCode': fields.Integer(default=1),
    'divisionCode': fields.Integer(),
    'employeeCode': fields.String(),
    'employeeTitle': fields.String(),
    'emp_first_name': fields.String(),
    'emp_mail_id' : fields.String(),
    'dept_cd': fields.Integer(),
    'emp_password': fields.String(),
    'created_by': fields.String(),
    'created_dt': fields.String(),
    'emp_type': fields.String(),
    'auto_created': fields.Integer()
})

@ns.route("/v1/")
class EmployeeCreate(Resource):
    @jwt_required()
    @ns.expect(employee_dto, validate=True)
    @ns.doc(description='Resource to Create Employee Details')
    def post(self):
        try:
            request_data = request.get_json()

            # Set default values for comp_cd and process other request_data
            comp_cd = request_data.get('companyCode', 1)
            division_code = request_data.get('divisionCode')
            employee_code = request_data.get('employeeCode')
            employee_title = request_data.get('employeeTitle')
            emp_first_name = request_data.get('emp_first_name')
            dept_cd = request_data.get('dept_cd')
            emp_mail_id = request_data.get('emp_mail_id')
            emp_password = request_data.get('emp_password')
            created_by = request_data.get('created_by')
            created_dt_str = request_data.get('created_dt')  # Assuming it's a string for simplicity
            emp_type = request_data.get('emp_type')
            auto_created = request_data.get('auto_created')

            # Convert created_dt to a datetime object if provided, else use current time
            created_dt = datetime.strptime(created_dt_str, '%Y-%m-%d') if created_dt_str else datetime.utcnow()
            # Generate a unique salt for each user
            salt = bcrypt.gensalt()

            # Hash the password using bcrypt and concatenate salt with the hashed password
            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(emp_password.encode(), bcrypt.gensalt()).decode()

            # Create a new employee record
            new_employee = EppsHrEmpMst(
                comp_cd=comp_cd,
                div_cd=division_code,
                emp_cd=employee_code,
                emp_title=employee_title,
                emp_first_name=emp_first_name,
                dept_cd=dept_cd,
                emp_mail_id=emp_mail_id,
                emp_password=hashed_password,  # Use hashed password without salt
                created_by=created_by,
                created_dt=created_dt,
                emp_type=emp_type,
                auto_created=auto_created
            )


            # Add the new employee record to the database
            db.session.add(new_employee)
            db.session.commit()

            # Return success response
            return {'message': 'Record Created Successfully'}, 200
        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500



employe2_dto = ns.model('Employee2DTO', {
    'empMailId': fields.String(),
    'empPassword': fields.String(),
})

import bcrypt
import jwt
from flask import request
from datetime import datetime, timedelta


SECRET_KEY = 'SECRET_KEY$123'

ns_token = Namespace("token", description="Token")


# Define Swagger authorization
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

@ns_token.route("/v1/")
class Employeetoken(Resource):
    @ns_token.expect(employe2_dto, validate=True)
    @ns_token.doc(description='Resource to Verify Employee Credentials and Generate Token', security='Bearer Auth')
    def post(self):
        try:
            request_data = request.get_json()
            emp_mail_id = request_data.get("empMailId")
            emp_password = request_data.get('empPassword')
            emp_type = request_data.get('empType')

            # Query the database to check if the employee with the given email exists
            employee = EppsHrEmpMst.query.filter_by(emp_mail_id=emp_mail_id).first()

            if employee:
                # Verify the password
                if bcrypt.checkpw(emp_password.encode(), employee.emp_password.encode()):
                    # Generate access token using emp_cd, emp_mail_id, and emp_password
                    token_payload = {
                        'emp_cd': employee.emp_cd,
                        'emp_mail_id': emp_mail_id,
                        'emp_type': emp_type
                    }
                    access_token = create_access_token(identity=token_payload)
                    refresh_token = create_refresh_token(identity=token_payload)

                    # Return success response with access and refresh tokens
                    return {'message': 'Credentials verified', 'access_token': access_token, 'refresh_token': refresh_token}, 200
                else:
                    return {'error': 'Invalid password'}, 401
            else:
                return {'error': 'Employee not found'}, 404
        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500



@ns.route("/v1")
class EmployeeUpdate(Resource):
    @jwt_required()
    @ns.expect(employee_dto, validate=True)
    @ns.doc(description='Resource to Update Employee Details')
    def put(self):
        try:
            request_data = request.get_json()

            # Retrieve the existing employee record based on the employee_code from the request_data
            employee_code = request_data.get('employeeCode')
            existing_employee = EppsHrEmpMst.query.filter_by(emp_cd=employee_code).first()

            if existing_employee:
                # Update employee details based on the request_data
                existing_employee.div_cd = request_data.get('divisionCode', existing_employee.div_cd)
                existing_employee.emp_first_name = request_data.get('emp_first_name', existing_employee.emp_first_name)
                existing_employee.dept_cd = request_data.get('dept_cd', existing_employee.dept_cd)

                # Update password if provided in the request
                emp_password = request_data.get('emp_password')
                if emp_password:
                    # Generate a unique salt for each user
                    salt = bcrypt.gensalt()
                    # Hash the password using bcrypt and concatenate salt with the hashed password
                    hashed_password_with_salt = bcrypt.hashpw(emp_password.encode(), salt).decode()
                    existing_employee.emp_password = hashed_password_with_salt

                # Update other fields as needed
                existing_employee.emp_type = request_data.get('emp_type', existing_employee.emp_type)
                existing_employee.auto_created = request_data.get('auto_created', existing_employee.auto_created)

                # Commit the changes to the database
                db.session.commit()

                # Return success response
                return {'message': 'Record Updated Successfully'}, 200
            else:
                # Return an error response if the employee with the given code is not found
                return {'error': 'Employee not found'}, 404

        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500

@ns.route("/v1/change/password/<int:division_code>/<string:employee_code>/<string:new_password>")
class EmployeeChangePassword(Resource):
    @jwt_required()
    @ns.doc(description='Resource to Change Employee Password')
    def put(self, division_code, employee_code, new_password):
        try:
            # Retrieve the existing employee record based on the division_code and employee_code
            existing_employee = EppsHrEmpMst.query.filter_by(div_cd=division_code, emp_cd=employee_code).first()

            if existing_employee:
                # Generate a unique salt for each user
                salt = bcrypt.gensalt()
                # Hash the new password using bcrypt and concatenate salt with the hashed password
                hashed_password_with_salt = bcrypt.hashpw(new_password.encode(), salt).decode()
                existing_employee.emp_password = hashed_password_with_salt

                # Commit the changes to the database
                db.session.commit()

                # Return success response
                return {'message': 'Password Updated Successfully'}, 200
            else:
                # Return an error response if the employee with the given codes is not found
                return {'error': 'Employee not found'}, 404

        except Exception as e:
            return {'error': str(e)}, 500
        
ns_business = Namespace("business", description="Business Zone API Details")

@ns_business.route("/zone/tree/v1")
class EppsBusinessZoneMstViews(Resource):
    @jwt_required()
    @ns_business.doc(description='Endpoint to get employee details', params={
        'companyCode': 'Company Code',
        'divisionCode': 'Division Code',
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')

        total_records = EppsBusinessZoneMst.query.count()

        offset = (page - 1) * per_page

        query = EppsBusinessZoneMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'company_code': link.comp_cd,
                'division_code': link.div_cd,
                'bus_zone_cd':link.bus_zone_cd,
                'bus_zone_disp_name' :link.bus_zone_disp_name,
                'bus_zone_long_name':link.bus_zone_long_name,
                'parent_bus_zone_cd' : link.parent_bus_zone_cd,
                'bus_level_flag': link.bus_level_flag,
                'address_details': link.address_details,
                'city_cd': link.city_cd,
                'state_cd': link.state_cd,
                'country_cd': link.country_cd,
                'created_dt' : link.created_dt,
                'created_by': link.created_by,
                'updated_dt': link.updated_dt,
                'updated_by': link.updated_by,
                'terminal_id' : link.terminal_id,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd' : link.updator_role_cd,
                'isActive': link.active_yn
            })

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })


@ns_business.route("/zone/v1")
class EppsBusinessZoneMst2Views(Resource):
    @jwt_required()
    @ns_business.doc(description='Endpoint to get employee details', params={
        'companyCode': 'Company Code',
        'divisionCode': 'Division Code',
        'businessZoneCode': 'business Zone Code',
        'businessZoneType':'business Zone Type',
        'parentBusinessZoneCode':'parent business Zone Code',
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        business_zone_code = request.args.get('businessZoneCode')
        business_zone_type = request.args.get('businessZoneType')
        parent_business_zone_code = request.args.get('parentBusinessZoneCode')


        total_records = EppsBusinessZoneMst.query.count()

        offset = (page - 1) * per_page

        query = EppsBusinessZoneMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if business_zone_code:
            query = query.filter_by(bus_zone_cd=business_zone_code)
        if business_zone_type:
            query = query.filter_by(div_cd=business_zone_type)
        if parent_business_zone_code:
            query = query.filter_by(parent_bus_zone_cd=parent_business_zone_code)

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'company_code': link.comp_cd,
                'division_code': link.div_cd,
                'bus_zone_cd':link.bus_zone_cd,
                'bus_zone_disp_name' :link.bus_zone_disp_name,
                'bus_zone_long_name':link.bus_zone_long_name,
                'parent_bus_zone_cd' : link.parent_bus_zone_cd,
                'bus_level_flag': link.bus_level_flag,
                'address_details': link.address_details,
                'city_cd': link.city_cd,
                'state_cd': link.state_cd,
                'country_cd': link.country_cd,
                'created_dt' : link.created_dt,
                'created_by': link.created_by,
                'updated_dt': link.updated_dt,
                'updated_by': link.updated_by,
                'terminal_id' : link.terminal_id,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd' : link.updator_role_cd,
                'isActive': link.active_yn
            })

        return jsonify({
            'business-zone-mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

ns_ecode = Namespace('ecode', description="City Master API Details")
@ns_ecode.route("/category/v1", methods=["GET"])
class ECodeCategoryLink(Resource):
    @jwt_required()
    @ns_ecode.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'Company Code', 'type': 'integer','default':1},
    'divisionCode': {'description': 'Division Code', 'type': 'integer'},
    'ecode': {'description': 'provide ecode ', 'type': 'string'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        ecode = request.args.get('ecode')
        is_active = request.args.get('isActive')
        
        total_records = EppsEcodeMst.query.count()

        offset = (page - 1) * per_page

        query = EppsEcodeMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if ecode:
            query = query.filter_by(ecode=ecode)
        if is_active is not None:
            query = query.filter(EppsEcodeMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = EppsEcodeMstSchema(many=True).dump(pagination)

        return jsonify({
            'ecode_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

ns_city = Namespace('city', description="City Master API Details")
@ns_city.route("/v1", methods=["GET"])
class EppsCityMstViews(Resource):
    @jwt_required()
    @ns_city.doc(description='Resource To Read E-Code Category Link Data', params={
    'countryCode': {'description': 'country Code', 'type': 'integer'},
    'stateCode': {'description': 'state Code', 'type': 'integer'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'componyCode': {'description': 'provide compony code', 'type': 'integer','default':1},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        country_code = request.args.get('countryCode')
        state_code = request.args.get('stateCode')
        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')       
        
        total_records = EppsCityMst.query.count()

        offset = (page - 1) * per_page

        query = EppsCityMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if country_code:
            query = query.filter_by(country_cd=country_code)
        if state_code:
            query = query.filter_by(state_cd=state_code)
        if is_active is not None:
            query = query.filter(EppsCityMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = EppsCityMstSerializer(many=True).dump(pagination)

        return jsonify({
            'ecode_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
ns_company= Namespace('compony', description="Resources to handle E-Code Category Link API")
@ns_company.route("/v1", methods=["GET"])
class EppsCompanyMstViews(Resource):
    @jwt_required()
    @ns_company.doc(description='Resource To Read E-Code Category Link Data', params={
    'componyCode': {'description': 'provide compony code', 'type': 'integer','default':1},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'auditTrailYn': {'description': 'provide auditTrailYn 1(Yes) or 0(No) Flag', 'type': 'integer','default':0},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')       
        
        total_records = EppsCityMst.query.count()

        offset = (page - 1) * per_page

        query = EppsCompanyMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsCompanyMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd' : link.comp_cd,
                'comp_disp_name' : link.comp_disp_name,
                'comp_long_name': link.comp_long_name,
                'add1' : link.add1,
                'add2': link.add2,
                'add3': link.add3,
                'city_cd': link.city_cd,
                'pin': link.pin,
                'country_cd': link.country_cd,
                'state_cd': link.state_cd,
                'mail_id': link.state_cd,
                'active_yn': link.state_cd,
                'epps_type': link.state_cd
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns_company.route("/v1/<int:companyCode>", methods=["GET"])
class EppsCompanyMst2Views(Resource):
    @jwt_required()
    @ns_company.doc(description='Resource To Read E-Code Category Link Data', params={
    # 'componyCode': {'description': 'provide compony code', 'type': 'integer','default':1},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'auditTrailYn': {'description': 'provide auditTrailYn 1(Yes) or 0(No) Flag', 'type': 'integer','default':0},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self,companyCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        is_active = request.args.get('isActive')
        query = EppsHrEmpMst.query.filter_by(comp_cd=companyCode)       
        
        total_records = EppsCityMst.query.count()

        offset = (page - 1) * per_page

        query = EppsCompanyMst.query
        if companyCode:
            query = query.filter_by(comp_cd=companyCode)
        if is_active is not None:
            query = query.filter(EppsCompanyMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd' : link.comp_cd,
                'comp_disp_name' : link.comp_disp_name,
                'comp_long_name': link.comp_long_name,
                'add1' : link.add1,
                'add2': link.add2,
                'add3': link.add3,
                'city_cd': link.city_cd,
                'pin': link.pin,
                'country_cd': link.country_cd,
                'state_cd': link.state_cd,
                'mail_id': link.state_cd,
                'active_yn': link.state_cd,
                'epps_type': link.state_cd
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })


ns_currency = Namespace('currency', description="(CORE)Customer Master API")


@ns_currency.route("/v1", methods=["GET"])
class EppsCurrencyMstViews(Resource):
    @jwt_required()
    @ns_currency.doc(description='Resource To Read E-Code Category Link Data', params={
    'componyCode': {'description': 'provide compony code', 'type': 'integer','default':1},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')       
        
        total_records = EppsCurrencyMst.query.count()

        offset = (page - 1) * per_page

        query = EppsCurrencyMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsCurrencyMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result =EppsCurrencyMstSerializer(many=True).dump(pagination)

        return jsonify({
            'currency-mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })    
    
from flask import request, jsonify
from flask_restx import Namespace, Resource
from datetime import datetime
from .models import db, EppsSdCustomerMst, EppsLocationMst, EppsWebNotificationPool

ns_customer = Namespace('customer', description="customer Master Controller API")

@ns_customer.route("/v1/cosignee", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','required':True},
    'divisionCode': {'description': 'provide division code', 'type': 'integer','required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer','required':True},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'sezFlag': {'description': 'sezFlag', 'type': 'integer'},
    'locationCodeList': {'description': 'provide locationCodeList', 'type': 'integer'},
    'tranIndicatorType': {'description': 'provide tranIndicatorType', 'type': 'string'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        customer_code = request.args.get('customerCode')
        division_code = request.args.get('divisionCode')
        locationCodeList = request.args.get('locationCodeList')
        tranIndicatorType = request.args.get('tranIndicatorType')


        total_records = EppsSdCustomerMst.query.count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsSdCustomerMst, EppsLocationMst, EppsWebNotificationPool).join(
            EppsLocationMst, EppsSdCustomerMst.comp_cd == EppsLocationMst.comp_cd
        )

        if company_code:
            query = query.filter(EppsSdCustomerMst.comp_cd == company_code)
        if customer_code:
            query = query.filter(EppsSdCustomerMst.cust_cd == customer_code)
        if division_code:
            query = query.filter(EppsSdCustomerMst.div_cd == division_code)
        if locationCodeList:
            query = query.filter(EppsLocationMst.loc_cd == locationCodeList)
        if tranIndicatorType:
            query = query.filter(EppsWebNotificationPool.tran_ind_type == tranIndicatorType)
        if is_active is not None:
            query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_customer_mst, epps_location_mst, epps_web_notification_pool = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_customer_mst.comp_cd,
                'div_cd': epps_customer_mst.div_cd,
                'cust_cd': epps_customer_mst.cust_cd,
                'cust_disp_name': epps_customer_mst.cust_disp_name,
                'cust_long_name': epps_customer_mst.cust_long_name,
                'cust_type': epps_customer_mst.cust_type,
                'credit_control_flag': epps_customer_mst.credit_control_flag,
                'credit_days': epps_customer_mst.credit_days,
                'credit_amt_limit': epps_customer_mst.credit_amt_limit,
                'cst_no': epps_customer_mst.cst_no,
                'cst_date': epps_customer_mst.cst_date,
                # Include fields from EppsLocationMst model
                'loc_cd': epps_location_mst.loc_cd,
                'loc_disp_name': epps_location_mst.loc_disp_name,
                # Include fields from EppsWebNotificationPool model
                'tran_ind_type': epps_web_notification_pool.tran_ind_type
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
customer_type_enum = ['PARTNER', 'WALK_IN_CUSTOMER','OVER_SEAS_CUSTOMER','LOCAL_CUSTOMER','DOMASTIC_CUSTOMER']
@ns_customer.route("/v1/<int:divisionCode>")
class EppsSdCustomerMstByDivision(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','required':True},
    'divisionCode': {'description': 'provide division code', 'type': 'integer'},
    # 'customerType': {'description': 'provide customer code', 'type': 'integer','required':True},
    'customerTypes': {'description': 'provide customer type', 'enum': customer_type_enum, 'type': 'list'},
    'channelViewApplicableFlag': {'description': 'channelViewApplicableFlag', 'type': 'integer'},
    'locationCodeList': {'description': 'provide locationCodeList', 'type': 'integer'},
    'tranIndicatorType': {'description': 'provide tranIndicatorType', 'type': 'string'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')
            employee_type = request.args.get('employeeType')
            partner_code = request.args.get('partnerCode')
            location_code = request.args.get('locationCodes')
            root_role_code = request.args.get('rootRoleCode')
          

            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if partner_code is not None:
                query = query.filter_by(partner_cd=partner_code)
            if location_code is not None:
                query = query.filter_by(partner_loc_cd=location_code)
            if root_role_code is not None:
                query = query.filter_by(role_cd=root_role_code)
            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
    
@ns_customer.route("/v1/<int:divisionCode>/<int:customerCode>")
class EppsSdCustomerMstByDivision(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','required':True},
    'currencyCode': {'description': 'provide currency code', 'type': 'integer'},
    'contactSerialNo': {'description': 'provide contactSerialNo', 'type': 'integer'},
    'customerAddressCode': {'description': 'provide customerAddress Code', 'type': 'integer'},
    'paytermCode': {'description': 'provide payterm code', 'type': 'integer'},
    'employeeCode': {'description': 'provide employee code', 'type': 'integer'},
    'customerCode': {'description': 'provide customer code', 'type': 'integer','required':True},
    'customerTypes': {'description': 'provide customer type', 'enum': customer_type_enum, 'type': 'list'},
    'channelViewApplicableFlag': {'description': 'channelViewApplicableFlag', 'type': 'integer'},
    'locationCodeList': {'description': 'provide locationCodeList', 'type': 'integer'},
    'tranIndicatorType': {'description': 'provide tranIndicatorType', 'type': 'string'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode,customerCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            is_active= request.args.get('isActive')
            employee_type = request.args.get('employeeType')
            partner_code = request.args.get('partnerCode')
            location_code = request.args.get('locationCodes')
            root_role_code = request.args.get('rootRoleCode')
          

            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)
            query = EppsSdCustomerMst.query.filter_by(cust_cd=customerCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if partner_code is not None:
                query = query.filter_by(partner_cd=partner_code)
            if location_code is not None:
                query = query.filter_by(partner_loc_cd=location_code)
            if root_role_code is not None:
                query = query.filter_by(role_cd=root_role_code)
            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
customer_address_type_enum = ['OFFICE _ADDRESS', 'BILLING_ADDRESS','SHIPPING_ADDRESS','HOME_ADDRESS','WORK_ADDRESS']
@ns_customer.route("/v1/<int:divisionCode>/address")
class EppsSdCustomerMstByDivisionaddress(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'customerAddressCode': {'description': 'provide customerAddressCode', 'type': 'integer'},
    'customerAddressType': {'description': 'provide customer address type', 'enum': customer_address_type_enum, 'type': 'string'},
    'countryCodeIncludeList': {'description': 'countryCodeIncludeList', 'type': 'integer'},
    'countryCodeExcludeList': {'description': 'provide countryCodeExcludeList ', 'type': 'integer'},
    'locationCodeList': {'description': 'provide locationCodeList', 'type': 'integer'},
    'sezFlag': {'description': 'sezFlag (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'consigneAddressFlag': {'description': 'consigneAddressFlag (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')
            employee_type = request.args.get('employeeType')
            partner_code = request.args.get('partnerCode')
            location_code = request.args.get('locationCodes')
            root_role_code = request.args.get('rootRoleCode')
          

            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if partner_code is not None:
                query = query.filter_by(partner_cd=partner_code)
            if location_code is not None:
                query = query.filter_by(partner_loc_cd=location_code)
            if root_role_code is not None:
                query = query.filter_by(role_cd=root_role_code)
            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })


customer_address_type_enum = ['OFFICE _ADDRESS', 'BILLING_ADDRESS','SHIPPING_ADDRESS','HOME_ADDRESS','WORK_ADDRESS']
@ns_customer.route("/v1/<int:divisionCode>/associates")
class EppsSdCustomerMstByDivisionaddress(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'employeeCode': {'description': 'provide employeeCode', 'type': 'string'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')
            employee_type = request.args.get('employeeType')
            partner_code = request.args.get('partnerCode')
            location_code = request.args.get('locationCodes')
            root_role_code = request.args.get('rootRoleCode')
          

            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
            if employee_type is not None:
                query = query.filter_by(emp_type=employee_type)
            if partner_code is not None:
                query = query.filter_by(partner_cd=partner_code)
            if location_code is not None:
                query = query.filter_by(partner_loc_cd=location_code)
            if root_role_code is not None:
                query = query.filter_by(role_cd=root_role_code)
            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
    

@ns_customer.route("/v1/<int:divisionCode>/bank")
class EppsSdCustomerMstByDivisionaddress(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'auditTrailYn': {'description': 'auditTrailYn (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')


            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
@ns_customer.route("/v1/<int:divisionCode>/contact")
class EppsSdCustomerMstByDivisionaddress(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'contactSerialNo': {'description': 'provide customer code', 'type': 'integer'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')


            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
from datetime import datetime
from flask import request, jsonify
from .models import db, EppsSdCustomerMst, EppsCurrencyMst

@ns_customer.route("/v1/<int:divisionCode>/currency", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode': {'description': 'provide company code', 'type': 'integer','required':True},
        'customerCode': {'description': 'provide customer code', 'type': 'integer'},
        'currencyCode': {'description': 'provide currency code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self, divisionCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        customer_code = request.args.get('customerCode')
        currency_code = request.args.get('currencyCode')

        total_records = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode).count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsSdCustomerMst, EppsCurrencyMst).join(
            EppsCurrencyMst, EppsSdCustomerMst.comp_cd == EppsCurrencyMst.comp_cd
        )

        if company_code:
            query = query.filter(EppsSdCustomerMst.comp_cd == company_code)
        if customer_code:
            query = query.filter(EppsSdCustomerMst.cust_cd == customer_code)
        if currency_code:
            query = query.filter(EppsCurrencyMst.curr_cd == currency_code)
        if is_active is not None:
            query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_customer_mst, epps_currency_mst = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_customer_mst.comp_cd,
                'div_cd': epps_customer_mst.div_cd,
                'cust_cd': epps_customer_mst.cust_cd,
                'cust_disp_name': epps_customer_mst.cust_disp_name,
                'cust_long_name': epps_customer_mst.cust_long_name,
                'cust_type': epps_customer_mst.cust_type,
                'credit_control_flag': epps_customer_mst.credit_control_flag,
                'credit_days': epps_customer_mst.credit_days,
                'credit_amt_limit': epps_customer_mst.credit_amt_limit,
                'cst_no': epps_customer_mst.cst_no,
                'cst_date': epps_customer_mst.cst_date,
                'curr_cd': epps_currency_mst.curr_cd,
                'curr_disp_name': epps_currency_mst.curr_disp_name,
                'curr_long_name': epps_currency_mst.curr_long_name,
                'created_by': epps_currency_mst.created_by,
                'created_dt': epps_currency_mst.created_dt.strftime("%Y-%m-%d %H:%M:%S") if epps_currency_mst.created_dt else None,
                'updated_by': epps_currency_mst.updated_by,
                'updated_dt': epps_currency_mst.updated_dt.strftime("%Y-%m-%d %H:%M:%S") if epps_currency_mst.updated_dt else None,
                'terminal_id': epps_currency_mst.terminal_id,
                'active_yn': epps_currency_mst.active_yn,
                'curr_unit_name': epps_currency_mst.curr_unit_name,
                'creator_role_cd': epps_currency_mst.creator_role_cd,
                'updator_role_cd': epps_currency_mst.updator_role_cd,
                'curr_rt_symbol': epps_currency_mst.curr_rt_symbol,
                'curr_abbr': epps_currency_mst.curr_abbr,
                'curr_small_deno': epps_currency_mst.curr_small_deno,
                'dflt_yn': epps_currency_mst.dflt_yn
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns_customer.route("/v1/<int:divisionCode>/payterm")
class EppsSdCustomerMstByDivisionaddress(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'paytermCode': {'description': 'provide paytermCode', 'type': 'integer'},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            employee_code = request.args.get('employeeCode')
            is_active= request.args.get('isActive')


            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if employee_code is not None:
                query = query.filter_by(emp_cd=employee_code)
            if is_active is not None:
                query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

            total_records = query.count()

            offset = (page - 1) * per_page

            business_zone_mst_pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(business_zone_mst_pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
@ns_customer.route("/v1/<int:divisionCode>/statutary")
class EppsSdCustomerMstByDivisionaddress(Resource):
    # @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','default':1,'required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self, divisionCode):
       
            # Parse request parameters
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 100)), 100)  

            company_code = request.args.get('companyCode')
            customer_code = request.args.get('customerCode')

            query = EppsSdCustomerMst.query.filter_by(div_cd=divisionCode)

            if company_code is not None:
                query = query.filter_by(comp_cd=company_code)
            if customer_code is not None:
                query = query.filter_by(emp_cd=customer_code)

            total_records = query.count()

            offset = (page - 1) * per_page

            pagination = query.offset(offset).limit(per_page).all()

            # Convert the result to JSON
            result = EppsSdCustomerMstSchema(many=True).dump(pagination)

            return jsonify({
                'hr_customer_mst': result,
                'page': page,
                'per_page': per_page,
                'total_items': total_records
            })
    
ns_department = Namespace("department", description="department Master API Details")

@ns_department.route("/v1")

class EppsHrEmpMstView(Resource):
    # @jwt_required()
    @ns_department.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'departmentCode': 'Department Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        department_code = request.args.get('departmentCode')
        is_active = request.args.get('isActive', None)
       


        total_records = EppsDeptMst.query.count()

        offset = (page - 1) * per_page

        query = EppsDeptMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if department_code:
            query = query.filter_by(dept_cd=department_code)
        if is_active is not None:
            query = query.filter(EppsDeptMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
            # Convert the result to JSON
        result = EppsDeptMstSerializer(many=True).dump(pagination)

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
@ns_department.route("/v1/<int:departmentCode>")
class EppsHrEmpMstasdepartmentView(Resource):
    # @jwt_required()
    @ns_department.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, departmentCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get('isActive', None)
        query = EppsDeptMst.query.filter_by(dept_cd=departmentCode)

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsDeptMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        
        # Convert the result to JSON
        result = EppsDeptMstSerializer(many=True).dump(pagination)

        return jsonify({
            'department_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })


ns_division = Namespace('division', description="(CORE)Division Master API")
@ns_division.route("/v1")
class EppsDivisionMstViews(Resource):
    @ns_division.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode': {'description': 'provide company code', 'type': 'integer'},
        'divisionCode': {'description': 'provide division code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        division_code = request.args.get('divisionCode')
        is_active = request.args.get('isActive', None)

        total_records = EppsDivisionMst.query.count()

        offset = (page - 1) * per_page

        query = EppsDivisionMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:  # Corrected variable name to division_code
            query = query.filter_by(div_cd=division_code)
        if is_active is not None:
            query = query.filter(EppsDivisionMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        # Serialize the result using EppsDivisionMstSchema
        result = []
        for item in pagination:
            serialized_item = EppsDivisionMstSchema().dump(item)
            result.append(serialized_item)

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })



ns_Finyr = Namespace('finance', description="(CORE)Financial Year API")
@ns_Finyr.route("/year/v1")
class EppsFinyrMstviews(Resource):
    # @jwt_required()
    @ns_Finyr.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide companyCode', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
 
        total_records = EppsFinyrMst.query.count()
        

        offset = (page - 1) * per_page

        query = EppsFinyrMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)

        pagination = query.offset(offset).limit(per_page).all()
            # Convert the result to JSON
        result = EppsFinyrMstSchema(many=True).dump(pagination)

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
ns_item= Namespace('item/group', description="Item Master API Details")
@ns_item.route("/v1")
class EppsMmGroupMstviews(Resource):
    # @jwt_required()
    @ns_item.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'groupCode': {'description': 'provide group code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        group_code = request.args.get("groupCode")
        is_active = request.args.get("isActive")
 
        total_records = EppsMmGroupMst.query.count()
        

        offset = (page - 1) * per_page

        query = EppsMmGroupMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if group_code:  # Corrected variable name to division_code
            query = query.filter_by(div_cd=group_code)
        if is_active is not None:
            query = query.filter(EppsMmGroupMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
            # Convert the result to JSON
        result = EppsMmGroupMstSchema(many=True).dump(pagination)

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
from flask import request, jsonify
from flask_restx import Namespace, Resource
from .models import db, EppsMmItemMst, EppsLocationMst, EppsWebNotificationPool

# Create a namespace for the item master API
ns_itemm = Namespace('item', description="Item Master API Details")

@ns_itemm.route("/v1")
class EppsItemMasterViews(Resource):

    @ns_itemm.doc(description='Resource To Read Item Master Data', params={
        'divisionCode': {'description': 'Provide division code', 'type': 'integer'},
        'locationCode': {'description': 'Provide an array of location codes', 'type': 'array', 'items': {'type': 'integer'}},
        'groupCodes': {'description': 'Provide an array of groupCodes', 'type': 'array', 'items': {'type': 'integer'}},
        'subGroupCodes': {'description': 'Provide an array of subGroupCodes', 'type': 'array', 'items': {'type': 'integer'}},
        'subSubGroupCodes': {'description': 'Provide an array of subSubGroupCodes', 'type': 'array', 'items': {'type': 'integer'}},
        'itemCategories': {'description': 'Provide an array of itemCategories', 'type': 'array', 'items': {'type': 'integer'}},
        'wareHouseCodes': {'description': 'Provide an array of wareHouseCodes', 'type': 'array', 'items': {'type': 'integer'}},
        'itemCodes': {'description': 'Provide an array of itemCodes', 'type': 'array', 'items': {'type': 'integer'}},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': [1, 0], 'type': 'integer'},
        'tranIndicatorType': {'description': 'Provide tranIndicatorType', 'type': 'string'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        # Extract query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        is_active = request.args.get('isActive')
        divisionCode = request.args.get('divisionCode')
        location_codes = request.args.get('locationCode')
        groupCodes = request.args.get('groupCodes')
        subGroupCodes = request.args.get('subGroupCodes')
        subSubGroupCodes = request.args.get('subSubGroupCodes')
        itemCategories = request.args.get('itemCategories')
        itemCodes = request.args.get('itemCodes')
        tranIndicatorType = request.args.get('tranIndicatorType')

        # Count total records for pagination
        total_records = EppsMmItemMst.query.count()

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Construct the base query
        query = db.session.query(EppsMmItemMst, EppsLocationMst, EppsWebNotificationPool)\
    .join(EppsLocationMst, EppsMmItemMst.comp_cd == EppsLocationMst.comp_cd)\
    .join(EppsWebNotificationPool, EppsMmItemMst.comp_cd == EppsWebNotificationPool.comp_cd)


        # Apply filters based on query parameters
        if divisionCode:
            query = query.filter(EppsLocationMst.div_cd == divisionCode)
        if groupCodes:
            groupCodes = [int(code) for code in groupCodes.split(',')]
            query = query.filter(EppsMmItemMst.grp_cd.in_(groupCodes))
        if subGroupCodes:
            subGroupCodes = [int(code) for code in subGroupCodes.split(',')]
            query = query.filter(EppsMmItemMst.grs_cd.in_(subGroupCodes))
        if subSubGroupCodes:
            subSubGroupCodes = [int(code) for code in subSubGroupCodes.split(',')]
            query = query.filter(EppsMmItemMst.grss_cd.in_(subSubGroupCodes))
        if itemCategories:
            itemCategories = [int(code) for code in itemCategories.split(',')]
            query = query.filter(EppsMmItemMst.item_category.in_(itemCategories))
        if itemCodes:
            itemCodes = [int(code) for code in itemCodes.split(',')]
            query = query.filter(EppsMmItemMst.itemcode.in_(itemCodes))
        if tranIndicatorType:
            query = query.filter(EppsWebNotificationPool.tran_ind_type == tranIndicatorType)
        if is_active is not None:
            query = query.filter(EppsMmItemMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))
        
        if location_codes:
            location_codes = [int(code) for code in location_codes.split(',')]
            query = query.filter(EppsLocationMst.loc_cd.in_(location_codes))

        pagination = query.offset(offset).limit(per_page).all()

        result = []
        for record in pagination:
            epps_mm_item_mst, epps_location_mst, epps_web_notification_pool = record
            combined_data = {
                'comp_cd': epps_mm_item_mst.comp_cd,
                'div_cd': epps_location_mst.div_cd,
                'groupCodes': epps_mm_item_mst.grp_cd,
                'subGroupCodes': epps_mm_item_mst.grs_cd,
                'subSubGroupCodes': epps_mm_item_mst.grss_cd,
                'itemCategories': epps_mm_item_mst.item_category,
                'itemCodes': epps_mm_item_mst.itemcode,
                'locationCode': epps_location_mst.loc_cd,
                'loc_disp_name': epps_location_mst.loc_disp_name,
                'tran_ind_type': epps_web_notification_pool.tran_ind_type
            }
            result.append(combined_data)

        # Return paginated results along with metadata
        return jsonify({
            'item_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns_itemm.route("/v1/cosignee", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    @jwt_required()
    @ns_customer.doc(description='Resource To Read E-Code Category Link Data', params={
    'companyCode': {'description': 'provide company code', 'type': 'integer','required':True},
    'divisionCode': {'description': 'provide division code', 'type': 'integer','required':True},
    'customerCode': {'description': 'provide customer code', 'type': 'integer','required':True},
    'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
    'sezFlag': {'description': 'sezFlag', 'type': 'integer'},
    'locationCodeList': {'description': 'provide locationCodeList', 'type': 'integer'},
    'tranIndicatorType': {'description': 'provide tranIndicatorType', 'type': 'string'},
    'page': {'description': 'Page number', 'type': 'integer'},
    'per_page': {'description': 'Items per page', 'type': 'integer'}
})
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        customer_code = request.args.get('customerCode')
        division_code = request.args.get('divisionCode')
        locationCodeList = request.args.get('locationCodeList')
        tranIndicatorType = request.args.get('tranIndicatorType')


        total_records = EppsSdCustomerMst.query.count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsSdCustomerMst, EppsLocationMst, EppsWebNotificationPool).join(
            EppsLocationMst, EppsSdCustomerMst.comp_cd == EppsLocationMst.comp_cd
        )

        if company_code:
            query = query.filter(EppsSdCustomerMst.comp_cd == company_code)
        if customer_code:
            query = query.filter(EppsSdCustomerMst.cust_cd == customer_code)
        if division_code:
            query = query.filter(EppsSdCustomerMst.div_cd == division_code)
        if locationCodeList:
            query = query.filter(EppsLocationMst.loc_cd == locationCodeList)
        if tranIndicatorType:
            query = query.filter(EppsWebNotificationPool.tran_ind_type == tranIndicatorType)
        if is_active is not None:
            query = query.filter(EppsSdCustomerMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_customer_mst, epps_location_mst, epps_web_notification_pool = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_customer_mst.comp_cd,
                'div_cd': epps_customer_mst.div_cd,
                'cust_cd': epps_customer_mst.cust_cd,
                'cust_disp_name': epps_customer_mst.cust_disp_name,
                'cust_long_name': epps_customer_mst.cust_long_name,
                'cust_type': epps_customer_mst.cust_type,
                'credit_control_flag': epps_customer_mst.credit_control_flag,
                'credit_days': epps_customer_mst.credit_days,
                'credit_amt_limit': epps_customer_mst.credit_amt_limit,
                'cst_no': epps_customer_mst.cst_no,
                'cst_date': epps_customer_mst.cst_date,
                # Include fields from EppsLocationMst model
                'loc_cd': epps_location_mst.loc_cd,
                'loc_disp_name': epps_location_mst.loc_disp_name,
                # Include fields from EppsWebNotificationPool model
                'tran_ind_type': epps_web_notification_pool.tran_ind_type
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
ns_location= Namespace('location', description="Item Master API Details")
@ns_location.route("/v1")
class EppsLocationMstviews(Resource):
    # @jwt_required()
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'divisionCode': {'description': 'provide division code', 'type': 'integer'},
        'locationCode': {'description': 'provide location code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'Provide Audit Trail Yes/No 1(Yes) or 0(No) Flag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        location_code = request.args.get("locationCode")
        is_active = request.args.get("isActive")
        division_code = request.args.get('divisionCode')
        total_records = EppsLocationMst.query.count()
        

        offset = (page - 1) * per_page

        query = EppsLocationMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if location_code:  # Corrected variable name to division_code
            query = query.filter_by(loc_cd=location_code)
        if is_active is not None:
            query = query.filter(EppsLocationMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
            # Convert the result to JSON
        result = EppsLocationMstSchema(many=True).dump(pagination)

        return jsonify({
            'hr_employee_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
@ns_location.route("/v1/<int:locationCode>")
class EppsHrEmpMstaslocationView(Resource):
    # @jwt_required()
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, locationCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")
        division_code = request.args.get('divisionCode')
        total_records = EppsLocationMst.query.count()
        query = EppsLocationMst.query.filter_by(loc_cd=locationCode)

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if is_active is not None:
            query = query.filter(EppsLocationMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        
        # Convert the result to JSON
        result = EppsLocationMstSchema(many=True).dump(pagination)

        return jsonify({
            'department_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

parser = reqparse.RequestParser()
parser.add_argument('companyCode', type=int, help='Provide Company Code', default=1)
parser.add_argument('divisionCode', type=int, help='Provide Division Code')
parser.add_argument('auditTrailYn', type=int, help='Provide Audit Trail YesNo 1(Yes) or 0(No) Flag', default=0)
parser.add_argument('isActive', type=int, help='Active 1/0')
parser.add_argument('paginationSearchVO', type=dict, location='args')


@ns_location.route("/v1/<locations>")
class LocationListView(Resource):
    @ns_location.doc(description='API for fetching location list based on provided location code list',
                     params={
                         'companyCode': 'Provide Company Code',
                         'divisionCode': 'Provide Division Code',
                         'auditTrailYn': 'Provide Audit Trail YesNo 1(Yes) or 0(No) Flag',
                         'isActive': 'Active 1/0',
                         'locations': {'description': 'Provide List of location codes', 'type': 'array',
                                       'items': {'type': 'integer'}}
                     })
    def get(self, locations):

        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        args = parser.parse_args()
        company_code = args['companyCode']
        division_code = args['divisionCode']
        is_active = args['isActive']

        query = EppsLocationMst.query

        if company_code:
            query = query.filter(EppsLocationMst.comp_cd == company_code)
        if division_code:
            query = query.filter(EppsLocationMst.div_cd == division_code)
        if is_active is not None:
            query = query.filter(EppsLocationMst.active_yn == ('Y' if is_active == 1 else 'N'))

        # Filter by multiple location codes
        if locations:
            location_codes = [int(code) for code in locations.split(',')]
            query = query.filter(EppsLocationMst.loc_cd.in_(location_codes))

        total_records = query.count()

        result = EppsLocationMstSchema(many=True).dump(query)

        return jsonify({
            'department_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

# Assuming EppsLocationMst and other relevant models are your SQLAlchemy models
from .models import db, EppsLocationMst, EppsDivisionMst#, EppsCityMst, EppsStateMst

# ... (your other imports)

# Define a DTO for the location
location_dto = ns_location.model('locationDTO', {
    'companyCode': fields.Integer(default=1),
    'divisionCode': fields.Integer(),
    'locationCode': fields.Integer(),
    'locationDisplayName': fields.String(),
    'address': fields.String(),
    'countryCode': fields.Integer(),
    'stateCode': fields.Integer(),
    'parentLocCd': fields.Integer(),
    'cityCode': fields.Integer()
})

@ns_location.route("/location/v1/")
class LocationCreate(Resource):
    # @jwt_required()
    @ns.expect(location_dto, validate=True)
    @ns.doc(description='Resource to Create Location Details')
    def post(self):
        try:
            request_data = request.get_json()

            # Set default values for comp_cd and process other request_data
            comp_cd = request_data.get('companyCode', 1)
            division_code = request_data.get('divisionCode')
            loc_code = request_data.get('locationCode')
            address = request_data.get('address')
            loc_disp_name = request_data.get('locationDisplayName')
            country_cd = request_data.get('countryCode')
            state_cd = request_data.get('stateCode')
            city_cd = request_data.get('cityCode')
            parent_loc_cd = request_data.get('parentLocCd')

            # # Check if division exists
            # existing_city = EppsCityMst.query.filter_by(comp_cd=comp_cd, country_cd=country_cd, state_cd=state_cd,city_cd=city_cd).first()
            # if existing_city is None:
            #     return {'error': 'city does not exist'}, 400

            # Create a new location record
            new_location = EppsLocationMst(
                comp_cd=comp_cd,
                div_cd=division_code,
                loc_cd=loc_code,
                add1=address,
                loc_disp_name=loc_disp_name,
                country_cd=country_cd,
                state_cd=state_cd,
                city_cd=city_cd,
                parent_loc_cd=parent_loc_cd
            )

            # Add the new location record to the database
            db.session.add(new_location)
            db.session.commit()

            # Return success response
            return {'message': 'Location Record Created Successfully'}, 200
        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500

# Import your database models
from .models import db, EppsLocationMst, EppsDivisionMst,  EppsStateMst, EppsCityMst  # Import your models from the 'models' module

# ... (other imports)

# Define your DTO model
location_dto = ns_location.model('locationDTO', {
    'companyCode': fields.Integer(default=1),
    'divisionCode': fields.Integer(),
    'locationCode': fields.Integer(),
    'locationDisplayName': fields.String(),
    'address': fields.String(),
    'countryCode': fields.Integer(),
    'stateCode': fields.Integer(),
    'parentLocCd': fields.Integer(),
    'cityCode': fields.Integer()
})

# Define your resource class
@ns_location.route("/location/v1/")
class LocationCreate(Resource):
    # @jwt_required()
    @ns.expect(location_dto, validate=True)
    @ns.doc(description='Resource to Create Location Details')
    def post(self):
        try:
            request_data = request.get_json()

            # Set default values for comp_cd and process other request_data
            comp_cd = request_data.get('companyCode', 1)
            division_code = request_data.get('divisionCode')
            loc_code = request_data.get('locationCode')
            address = request_data.get('address')
            loc_disp_name = request_data.get('locationDisplayName')
            country_cd = request_data.get('countryCode')
            state_cd = request_data.get('stateCode')
            city_cd = request_data.get('cityCode')
            parent_loc_cd = request_data.get('parentLocCd')

            # Check if division exists
            existing_division = EppsDivisionMst.query.filter_by(comp_cd=comp_cd, div_cd=division_code).first()
            if existing_division is None:
                return {'error': 'Division does not exist'}, 400

            # Create a new location record
            new_location = EppsLocationMst(
                comp_cd=comp_cd,
                div_cd=division_code,
                loc_cd=loc_code,
                # add1=address,
                loc_disp_name=loc_disp_name,
                country_cd=country_cd,
                state_cd=state_cd,
                city_cd=city_cd,
                parent_loc_cd=parent_loc_cd
            )

            # Add the new location record to the database
            db.session.add(new_location)
            db.session.commit()

            # Return success response
            return {'message': 'Location Record Created Successfully'}, 200
        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500

    # Modify this function for updating existing location details
    @ns.expect(location_dto, validate=True)
    @ns.doc(description='Resource to Update Location Details')
    def put(self):
        try:
            request_data = request.get_json()

            # Extract necessary data for update
            comp_cd = request_data.get('companyCode', 1)
            division_code = request_data.get('divisionCode')
            loc_code = request_data.get('locationCode')

            # Check if the location exists
            existing_location = EppsLocationMst.query.filter_by(comp_cd=comp_cd, div_cd=division_code, loc_cd=loc_code).first()
            if existing_location is None:
                return {'error': 'Location does not exist'}, 404

            # Update location details
            existing_location.add1 = request_data.get('address', existing_location.add1)
            existing_location.loc_disp_name = request_data.get('locationDisplayName', existing_location.loc_disp_name)
            existing_location.country_cd = request_data.get('countryCode', existing_location.country_cd)
            existing_location.state_cd = request_data.get('stateCode', existing_location.state_cd)
            existing_location.city_cd = request_data.get('cityCode', existing_location.city_cd)
            existing_location.parent_loc_cd = request_data.get('parentLocCd', existing_location.parent_loc_cd)

            # Commit the changes to the database
            db.session.commit()

            # Return success response
            return {'message': 'Location Record Updated Successfully'}, 200
        except Exception as e:
            # Handle any exceptions and return an error response
            return {'error': str(e)}, 500


  
ns_miscellaneous= Namespace('miscellaneous', description="Item Master API Details")
@ns_miscellaneous.route("/v1")
class EppsMiscMstviews(Resource):
    # @jwt_required()
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'miscType': {'description': 'provide miscType', 'type': 'integer'},
        'miscCode': {'description': 'provide miscCode', 'type': 'integer'},
        'miscValue': {'description': 'provide miscValue', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'Provide Audit Trail Yes/No 1(Yes) or 0(No) Flag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        misc_type = request.args.get("miscType")
        misc_code = request.args.get("miscCode")
        misc_value = request.args.get("miscValue")
        is_active = request.args.get("isActive")
        total_records = EppsMiscMst.query.count()

        offset = (page - 1) * per_page

        query = EppsMiscMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if misc_type:
            query = query.filter_by(misc_type=misc_type)
        if misc_code:  
            query = query.filter_by(misc_cd=misc_code)
        if misc_value:  
            query = query.filter_by(misc_value=misc_value)
        if is_active is not None:
            query = query.filter(EppsMiscMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd' : link.comp_cd,
                'misc_sr_no' : link.misc_sr_no,
                'misc_misc_cd':link.misc_misc_cd,
                'misc_misc_name':link.misc_misc_name,
                'parent_misc_cd':link.parent_misc_cd,
                'epps_only_flag':link.epps_only_flag,
                'misc_value' :link.misc_value,
                'remarks' :link.remarks,
                'created_by':link.created_by,
                'created_dt':link.created_dt,
                'updated_by':link.updated_by,
                'updated_dt':link.updated_dt,
                'terminal_id' :link.terminal_id,
                'active_yn':link.active_yn,
                'misc_type':link.misc_type,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd':link.updator_role_cd,
                'module_id' :link.module_id,
                'operation_done':link.operation_done,
                'insert_allow' :link.insert_allow
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    

@ns_miscellaneous.route("/v1/<string:miscType>")
class EppsHrEmpMstaslocationView(Resource):
    # @jwt_required()
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'miscCode': {'description': 'provide miscCode', 'type': 'integer'},
        'miscValue': {'description': 'provide miscValue', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, miscType):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        misc_code = request.args.get('miscCode')
        misc_value = request.args.get('miscValue')
        is_active = request.args.get("isActive")
        total_records = EppsMiscMst.query.count()
        query = EppsMiscMst.query.filter_by(misc_type=miscType)

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if misc_code:
            query = query.filter_by(misc_misc_cd=misc_code)
        if misc_value:
            query = query.filter_by(misc_value=misc_value)
        if is_active is not None:
            query = query.filter(EppsMiscMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd' : link.comp_cd,
                'misc_sr_no' : link.misc_sr_no,
                'misc_misc_cd':link.misc_misc_cd,
                'misc_misc_name':link.misc_misc_name,
                'parent_misc_cd':link.parent_misc_cd,
                'epps_only_flag':link.epps_only_flag,
                'misc_value' :link.misc_value,
                'remarks' :link.remarks,
                'created_by':link.created_by,
                'created_dt':link.created_dt,
                'updated_by':link.updated_by,
                'updated_dt':link.updated_dt,
                'terminal_id' :link.terminal_id,
                'active_yn':link.active_yn,
                'misc_type':link.misc_type,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd':link.updator_role_cd,
                'module_id' :link.module_id,
                'operation_done':link.operation_done,
                'insert_allow' :link.insert_allow
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

# @ns_miscellaneous.route("/v1/<string:miscType>/<string:micsCode>")
@ns_miscellaneous.route("/v1/<string:miscType>/<string:micsCode>")

class EppsHrEmpMstaslocationView(Resource):
    # @jwt_required()
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'miscValue': {'description': 'provide miscValue', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, miscType, micsCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        misc_value = request.args.get('miscValue')
        is_active = request.args.get("isActive")
        total_records = EppsMiscMst.query.count()
        query = EppsMiscMst.query.filter_by(misc_type=miscType)
        query = EppsMiscMst.query.filter_by(misc_misc_cd=micsCode)
        # query = EppsMiscMst.query.filter_by(misc_type=miscType, misc_misc_cd=micsCode).first()

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if misc_value:
            query = query.filter_by(misc_value=misc_value)
        if is_active is not None:
            query = query.filter(EppsMiscMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd' : link.comp_cd,
                'misc_sr_no' : link.misc_sr_no,
                'misc_misc_cd':link.misc_misc_cd,
                'misc_misc_name':link.misc_misc_name,
                'parent_misc_cd':link.parent_misc_cd,
                'epps_only_flag':link.epps_only_flag,
                'misc_value' :link.misc_value,
                'remarks' :link.remarks,
                'created_by':link.created_by,
                'created_dt':link.created_dt,
                'updated_by':link.updated_by,
                'updated_dt':link.updated_dt,
                'terminal_id' :link.terminal_id,
                'active_yn':link.active_yn,
                'misc_type':link.misc_type,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd':link.updator_role_cd,
                'module_id' :link.module_id,
                'operation_done':link.operation_done,
                'insert_allow' :link.insert_allow
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
 
ns_module= Namespace('module', description="Item Master API Details")

@ns_module.route("/v1")
class EppsModuleMst2views(Resource):
    # @jwt_required()
    @ns_module.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'Provide Audit Trail Yes/No 1(Yes) or 0(No) Flag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")
        total_records = EppsModuleMst.query.count()

        offset = (page - 1) * per_page

        query = EppsModuleMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsModuleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'module_id': link.module_id,
                'module_disp_name': link.module_disp_name,
                'active_yn': link.active_yn,
                'created_by': link.created_by,
                'created_dt': link.created_dt,
                'updated_by': link.updated_by,
                'updated_dt': link.updated_dt,
                'terminal_id': link.terminal_id,
                # 'module_disp_seq_no': link.module_disp_seq_no,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd': link.updator_role_cd,
                'default_access': link.default_access,
                'display_yn': link.display_yn
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
@ns_module.route("/v1/modules/<string:id>")

class EppsModuleMstView(Resource):
    # @jwt_required()
    @ns_department.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self,id ):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")
        total_records = EppsModuleMst.query.count()
        query = EppsModuleMst.query.filter_by(module_id=id)
      

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsModuleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'module_id': link.module_id,
                'module_disp_name': link.module_disp_name,
                'active_yn': link.active_yn,
                'created_by': link.created_by,
                'created_dt': link.created_dt,
                'updated_by': link.updated_by,
                'updated_dt': link.updated_dt,
                'terminal_id': link.terminal_id,
                # 'module_disp_seq_no': link.module_disp_seq_no,
                'creator_role_cd': link.creator_role_cd,
                'updator_role_cd': link.updator_role_cd,
                'default_access': link.default_access,
                'display_yn': link.display_yn
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
ns_program= Namespace('program', description="program Master API Details")

@ns_program.route("/v1", methods=["GET"])
class EppsCityMstViews(Resource):
    # @jwt_required()
    @ns_program.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'programCode':  {'description': 'provide programCode', 'type': 'integer'},
        'programDisplayName':  {'description': 'provide programDisplayName', 'type': 'string'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'Provide Audit Trail Yes/No 1(Yes) or 0(No) Flag', 'type': 'integer'},
        'moduleId':  {'description': 'provide moduleId', 'type': 'string'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        program_code = request.args.get('programCode')
        program_disp_name = request.args.get('programDisplayName')
        module_id = request.args.get('moduleId')
        is_active = request.args.get("isActive")       
        total_records = EppsProgMst.query.count()

        query = EppsProgMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if program_code:
            query = query.filter_by(prog_cd=program_code)
        if program_disp_name:
            query = query.filter_by(prog_disp_name=program_disp_name)
        if module_id:
            query = query.filter_by(module_id=module_id)
        if is_active is not None:
            query = query.filter(EppsProgMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        offset = (page - 1) * per_page
        pagination = query.offset(offset).limit(per_page).all()
        result = []

        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'prog_cd': link.prog_cd,
                'prog_id': link.prog_id,
                'prog_disp_name': link.prog_disp_name,
                'prog_long_name': link.prog_long_name,
                'prog_type': link.prog_type,
                'parent_id': link.parent_id,
                'module_id': link.module_id,
                'tran_indicator': link.tran_indicator,
                'prog_mtqr_flag': link.prog_mtqr_flag,
                'rep_type': link.rep_type,
                'menu_pass_parameter': link.menu_pass_parameter,
                'prog_report_name': link.prog_report_name,
                'prog_menu_display_yn': link.prog_menu_display_yn,
                'prog_disp_seq_no': link.prog_disp_seq_no
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records  
        })



@ns_program.route("/v1/<int:programCode>")

class EppsProgMstView(Resource):
    # @jwt_required()
    @ns_department.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self,programCode ):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")
        total_records = EppsProgMst.query.count()
        query = EppsProgMst.query.filter_by(prog_cd=programCode)
      

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsProgMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'prog_cd': link.prog_cd,
                'prog_id': link.prog_id,
                'prog_disp_name': link.prog_disp_name,
                'prog_long_name': link.prog_long_name,
                'prog_type': link.prog_type,
                'parent_id': link.parent_id,
                'module_id': link.module_id,
                'tran_indicator': link.tran_indicator,
                'prog_mtqr_flag': link.prog_mtqr_flag,
                'rep_type': link.rep_type,
                'menu_pass_parameter': link.menu_pass_parameter,
                'prog_report_name': link.prog_report_name,
                'prog_menu_display_yn': link.prog_menu_display_yn,
                'prog_disp_seq_no': link.prog_disp_seq_no
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
ns_rolelink = Namespace('role/link/', description="customer Master Controller API")
from sqlalchemy import and_

@ns_rolelink.route("/employee/location/v1", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    # @jwt_required()
    @ns_rolelink.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode': {'description': 'provide company code', 'type': 'integer'},
        'divisionCode': {'description': 'provide division code', 'type': 'integer'},
        'locationCode': {'description': 'provide division code', 'type': 'integer'},
        'roleCode': {'description': 'provide division code', 'type': 'integer'},
        'employeeCode': {'description': 'provide division code', 'type': 'integer'},
        'customerCode': {'description': 'provide customer code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'selLoctionFlag': {'description': 'sezFlag', 'type': 'integer'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        location_code = request.args.get('locationCode')
        employee_code = request.args.get('employeeCode')

        total_records = EppsRoleProgLnk.query.count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsRoleProgLnk, EppsLocationMst, EppsHrEmpMst).join(
            EppsLocationMst, and_(
                EppsRoleProgLnk.comp_cd == EppsLocationMst.comp_cd,
                EppsRoleProgLnk.div_cd == EppsLocationMst.div_cd,
                # Add additional join conditions as needed
            )
        ).join(
            EppsHrEmpMst, and_(
                EppsRoleProgLnk.comp_cd == EppsHrEmpMst.comp_cd,
                # Add additional join conditions as needed
            )
        )

        if company_code:
            query = query.filter(EppsRoleProgLnk.comp_cd == company_code)
        if division_code:
            query = query.filter(EppsRoleProgLnk.div_cd == division_code)
        if role_code:
            query = query.filter(EppsRoleProgLnk.role_cd == role_code)
        if location_code:
            query = query.filter(EppsLocationMst.loc_cd == location_code)
        if employee_code:
            query = query.filter(EppsHrEmpMst.emp_cd == employee_code)
        if is_active is not None:
            query = query.filter(EppsRoleProgLnk.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_role_mst, epps_location_mst, epps_loc_mst = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_role_mst.comp_cd,
                'div_cd': epps_role_mst.div_cd,
                # Include fields from EppsLocationMst model
                'loc_cd': epps_location_mst.loc_cd,
                # Include fields from EppsWebNotificationPool model
                'employee_code': epps_loc_mst.emp_cd
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns_rolelink.route("/employee/v1/employee/roles", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    # @jwt_required()
    @ns_rolelink.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode': {'description': 'provide company code', 'type': 'integer'},
        'divisionCode': {'description': 'provide division code', 'type': 'integer'},
        'locationCode': {'description': 'provide division code', 'type': 'integer'},
        'roleCode': {'description': 'provide division code', 'type': 'integer'},
        'employeeCode': {'description': 'provide division code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        location_code = request.args.get('locationCode')
        employee_code = request.args.get('employeeCode')

        total_records = EppsRoleProgLnk.query.count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsRoleProgLnk, EppsLocationMst, EppsHrEmpMst).join(
            EppsLocationMst, and_(
                EppsRoleProgLnk.comp_cd == EppsLocationMst.comp_cd,
                EppsRoleProgLnk.div_cd == EppsLocationMst.div_cd,
                # Add additional join conditions as needed
            )
        ).join(
            EppsHrEmpMst, and_(
                EppsRoleProgLnk.comp_cd == EppsHrEmpMst.comp_cd,
                # Add additional join conditions as needed
            )
        )

        if company_code:
            query = query.filter(EppsRoleProgLnk.comp_cd == company_code)
        if division_code:
            query = query.filter(EppsRoleProgLnk.div_cd == division_code)
        if role_code:
            query = query.filter(EppsRoleProgLnk.role_cd == role_code)
        if location_code:
            query = query.filter(EppsLocationMst.loc_cd == location_code)
        if employee_code:
            query = query.filter(EppsHrEmpMst.emp_cd == employee_code)
        if is_active is not None:
            query = query.filter(EppsRoleProgLnk.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_role_mst, epps_location_mst, epps_loc_mst = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_role_mst.comp_cd,
                'div_cd': epps_role_mst.div_cd,
                # Include fields from EppsLocationMst model
                'loc_cd': epps_location_mst.loc_cd,
                # Include fields from EppsWebNotificationPool model
                'employee_code': epps_loc_mst.emp_cd
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
@ns_rolelink.route("/employee/v1", methods=["GET"])
class EppsSdCustomerMstViews(Resource):
    # @jwt_required()
    @ns_rolelink.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode': {'description': 'provide company code', 'type': 'integer'},
        'divisionCode': {'description': 'provide division code', 'type': 'integer'},
        'locationCode': {'description': 'provide division code', 'type': 'integer'},
        'roleCode': {'description': 'provide division code', 'type': 'integer'},
        'employeeCode': {'description': 'provide division code', 'type': 'integer'},
        'customerCode': {'description': 'provide customer code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        is_active = request.args.get('isActive')
        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        location_code = request.args.get('locationCode')
        employee_code = request.args.get('employeeCode')

        total_records = EppsRoleProgLnk.query.count()

        offset = (page - 1) * per_page

        query = db.session.query(EppsRoleProgLnk, EppsLocationMst, EppsHrEmpMst).join(
            EppsLocationMst, and_(
                EppsRoleProgLnk.comp_cd == EppsLocationMst.comp_cd,
                EppsRoleProgLnk.div_cd == EppsLocationMst.div_cd,
                # Add additional join conditions as needed
            )
        ).join(
            EppsHrEmpMst, and_(
                EppsRoleProgLnk.comp_cd == EppsHrEmpMst.comp_cd,
                # Add additional join conditions as needed
            )
        )

        if company_code:
            query = query.filter(EppsRoleProgLnk.comp_cd == company_code)
        if division_code:
            query = query.filter(EppsRoleProgLnk.div_cd == division_code)
        if role_code:
            query = query.filter(EppsRoleProgLnk.role_cd == role_code)
        if location_code:
            query = query.filter(EppsLocationMst.loc_cd == location_code)
        if employee_code:
            query = query.filter(EppsHrEmpMst.emp_cd == employee_code)
        if is_active is not None:
            query = query.filter(EppsRoleProgLnk.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()

        result = []  # Define a list to store combined results

        for record in pagination:
            epps_role_mst, epps_location_mst, epps_loc_mst = record
            # Combine data from all three tables into a single dictionary
            combined_data = {
                'comp_cd': epps_role_mst.comp_cd,
                'div_cd': epps_role_mst.div_cd,
                # Include fields from EppsLocationMst model
                'loc_cd': epps_location_mst.loc_cd,
                # Include fields from EppsWebNotificationPool model
                'employee_code': epps_loc_mst.emp_cd
            }
            result.append(combined_data)

        return jsonify({
            'customer_mst_combined': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
  
ns_role= Namespace('program', description="program Master API Details")

@ns_role.route("/v1", methods=["GET"])
class EppsCityMstViews(Resource):
    # @jwt_required()
    @ns_role.doc(description='Resource To Read E-Code Category Link Data', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'programCode':  {'description': 'provide programCode', 'type': 'integer'},
        'programDisplayName':  {'description': 'provide programDisplayName', 'type': 'string'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'Provide Audit Trail Yes/No 1(Yes) or 0(No) Flag', 'type': 'integer'},
        'moduleId':  {'description': 'provide moduleId', 'type': 'string'},
        'page': {'description': 'Page number', 'type': 'integer'},
        'per_page': {'description': 'Items per page', 'type': 'integer'}
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)  

        company_code = request.args.get('companyCode')
        program_code = request.args.get('programCode')
        program_disp_name = request.args.get('programDisplayName')
        module_id = request.args.get('moduleId')
        is_active = request.args.get("isActive")       
        total_records = EppsProgMst.query.count()

        query = EppsProgMst.query
        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if program_code:
            query = query.filter_by(prog_cd=program_code)
        if program_disp_name:
            query = query.filter_by(prog_disp_name=program_disp_name)
        if module_id:
            query = query.filter_by(module_id=module_id)
        if is_active is not None:
            query = query.filter(EppsProgMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        offset = (page - 1) * per_page
        pagination = query.offset(offset).limit(per_page).all()
        result = []

        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'prog_cd': link.prog_cd,
                'prog_id': link.prog_id,
                'prog_disp_name': link.prog_disp_name,
                'prog_long_name': link.prog_long_name,
                'prog_type': link.prog_type,
                'parent_id': link.parent_id,
                'module_id': link.module_id,
                'tran_indicator': link.tran_indicator,
                'prog_mtqr_flag': link.prog_mtqr_flag,
                'rep_type': link.rep_type,
                'menu_pass_parameter': link.menu_pass_parameter,
                'prog_report_name': link.prog_report_name,
                'prog_menu_display_yn': link.prog_menu_display_yn,
                'prog_disp_seq_no': link.prog_disp_seq_no
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records  
        })
    
ns_role = Namespace('role', description="customer Master Controller API")
@ns_role.route("/v1/<int:divisionCode>")

class EppsRoleMstView(Resource):
    # @jwt_required()
    @ns_role.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'roleCode':  {'description': 'provide roleCode', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'auditTrailYn (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self,divisionCode ):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        is_active = request.args.get("isActive")
        total_records = EppsRoleMst.query.count()
        query = EppsRoleMst.query.filter_by(div_cd=divisionCode)
      

        total_records = query.count()

        offset = (page - 1) * per_page

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if role_code:
            query = query.filter_by(role_cd=role_code)
        if is_active is not None:
            query = query.filter(EppsRoleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'id' : link.id,
                'div_cd': link.div_cd,
                'role_cd' : link.role_cd,
                'role_disp_name': link.role_disp_name,
                'role_long_name': link.role_long_name,
                'role_parent_role' : link.role_parent_role,
                'role_type' : link.role_type,
                'role_disp_seq_no': link.role_disp_seq_no,
                'sys_admin_flag' : link.sys_admin_flag,
                'role_id': link.role_id,
                'per_item_limit' : link.per_item_limit,
                'per_transaction_limit': link.per_transaction_limit,
                'created_by': link.created_by,
                'created_dt' : link.created_dt
               
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

from sqlalchemy import and_

@ns_role.route("/v1/<int:divisionCode>/<int:roleCode>")
class EppsRoleMstView(Resource):
    # @jwt_required()
    @ns_role.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'auditTrailYn (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, divisionCode, roleCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")

        query = EppsRoleMst.query.filter_by(div_cd=divisionCode, role_cd=roleCode)

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsRoleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'id' : link.id,
                'div_cd': link.div_cd,
                'role_cd' : link.role_cd,
                'role_disp_name': link.role_disp_name,
                'role_long_name': link.role_long_name,
                'role_parent_role' : link.role_parent_role,
                'role_type' : link.role_type,
                'role_disp_seq_no': link.role_disp_seq_no,
                'sys_admin_flag' : link.sys_admin_flag,
                'role_id': link.role_id,
                'per_item_limit' : link.per_item_limit,
                'per_transaction_limit': link.per_transaction_limit,
                'created_by': link.created_by,
                'created_dt' : link.created_dt
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })


@ns_role.route("/v1/tree")
class EppsRoleMstView(Resource):
    # @jwt_required()
    @ns_role.doc(description='Endpoint to get department details', params={
        'roleCode':  {'description': 'provide roleCode', 'type': 'integer','required':True},
        'divisionCode':  {'description': 'provide divisionCode', 'type': 'integer'},
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'adminFlag':  {'description': 'provide adminFlag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        is_active = request.args.get("isActive")

        query = EppsRoleMst.query

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if role_code:
            query = query.filter_by(role_cd=role_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if is_active is not None:
            query = query.filter(EppsRoleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'id' : link.id,
                'div_cd': link.div_cd,
                'role_cd' : link.role_cd,
                'role_disp_name': link.role_disp_name,
                'role_long_name': link.role_long_name,
                'role_parent_role' : link.role_parent_role,
                'role_type' : link.role_type,
                'role_disp_seq_no': link.role_disp_seq_no,
                'sys_admin_flag' : link.sys_admin_flag,
                'role_id': link.role_id,
                'per_item_limit' : link.per_item_limit,
                'per_transaction_limit': link.per_transaction_limit,
                'created_by': link.created_by,
                'created_dt' : link.created_dt
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

@ns_role.route("/v1/tree/idValue")
class EppsRoleMstView(Resource):
    # @jwt_required()
    @ns_role.doc(description='Endpoint to get department details', params={
        'roleCode':  {'description': 'provide roleCode', 'type': 'integer','required':True},
        'divisionCode':  {'description': 'provide divisionCode', 'type': 'integer'},
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'adminFlag':  {'description': 'provide adminFlag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        is_active = request.args.get("isActive")

        query = EppsRoleMst.query

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if role_code:
            query = query.filter_by(role_cd=role_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if is_active is not None:
            query = query.filter(EppsRoleMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'id' : link.id,
                'div_cd': link.div_cd,
                'role_cd' : link.role_cd,
                'role_disp_name': link.role_disp_name,
                'role_long_name': link.role_long_name,
                'role_parent_role' : link.role_parent_role,
                'role_type' : link.role_type,
                'role_disp_seq_no': link.role_disp_seq_no,
                'sys_admin_flag' : link.sys_admin_flag,
                'role_id': link.role_id,
                'per_item_limit' : link.per_item_limit,
                'per_transaction_limit': link.per_transaction_limit,
                'created_by': link.created_by,
                'created_dt' : link.created_dt
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
ns_roleprogramm = Namespace('role/link/program', description="role program Master API")
@ns_roleprogramm.route("/v1/roles/linked/tree")
class EppsRoleMstView(Resource):
    # @jwt_required()
    @ns_roleprogramm.doc(description='Endpoint to get department details', params={
        'roleCode':  {'description': 'provide roleCode', 'type': 'integer','required':True},
        'divisionCode':  {'description': 'provide divisionCode', 'type': 'integer'},
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'adminFlag':  {'description': 'provide adminFlag', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        role_code = request.args.get('roleCode')
        division_code = request.args.get('divisionCode')
        is_active = request.args.get("isActive")

        query = EppsRoleProgLnk.query

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if role_code:
            query = query.filter_by(role_cd=role_code)
        if division_code:
            query = query.filter_by(div_cd=division_code)
        if is_active is not None:
            query = query.filter(EppsRoleProgLnk.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'div_cd': link.div_cd,
                'role_cd': link.role_cd,
                'prog_cd' : link.prog_cd,
                'created_by': link.created_by,
                'created_dt' : link.created_dt,
                'updated_by' : link.updated_by,
                'updated_dt' : link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn' : link.active_yn
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    

@ns_roleprogramm.route("/v1/<int:roleCode>")
class EppsRoleProgLnkView(Resource):
    # @jwt_required()
    @ns_roleprogramm.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn': {'description': 'auditTrailYn (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self, roleCode):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        is_active = request.args.get("isActive")

        query = EppsRoleProgLnk.query.filter_by(role_cd=roleCode)

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if is_active is not None:
            query = query.filter(EppsRoleProgLnk.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'div_cd': link.div_cd,
                'role_cd': link.role_cd,
                'prog_cd' : link.prog_cd,
                'created_by': link.created_by,
                'created_dt' : link.created_dt,
                'updated_by' : link.updated_by,
                'updated_dt' : link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn' : link.active_yn
            })

        return jsonify({
            'company-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
ns_stage= Namespace('stage', description="stage Master API")
@ns_stage.route("/v1")
class EppsStageMstView(Resource):
    # @jwt_required()
    @ns_stage.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'tiCode':  {'description': 'provide tiCode', 'type': 'string'},
        'stageDescription':  {'description': 'provide stageDescription', 'type': 'integer'},
        'stageCode':  {'description': 'provide stageCode', 'type': 'string'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn':  {'description': 'provide auditTrailYn', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        ti_code = request.args.get('tiCode')
        stage_description = request.args.get('stageDescription')
        stage_code = request.args.get('stageCode')
        is_active = request.args.get("isActive")

        query = EppsStageMst.query

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if ti_code:
            query = query.filter_by(ti_code=ti_code)
        if stage_description:
            query = query.filter_by(stage_desc=stage_description)
        if stage_code:
            query = query.filter_by(stage_cd=stage_code)
        if is_active is not None:
            query = query.filter(EppsStageMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'ti_code' : link.ti_code,
                'stage_cd' : link.stage_cd,
                'stage_desc': link.stage_desc,
                'created_by' : link.created_by,
                'created_dt': link.created_dt,
                'updated_by': link.updated_by,
                'updated_dt' : link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn' : link.active_yn,
                'creator_role_cd' : link.creator_role_cd,
                'updator_role_cd': link.updator_role_cd,
                'module_id': link.module_id
            })

        return jsonify({
            '-master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    
ns_state = Namespace('state', description="state Master API")
@ns_state.route("/v1")
class EppsStateMstView(Resource):
    # @jwt_required()
    @ns_state.doc(description='Endpoint to get department details', params={
        'companyCode':  {'description': 'provide company code', 'type': 'integer'},
        'countryCode':  {'description': 'provide countryCode', 'type': 'integer'},
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'auditTrailYn':  {'description': 'provide auditTrailYn', 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page'
    })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)

        company_code = request.args.get('companyCode')
        country_code = request.args.get('countryCode')
        is_active = request.args.get("isActive")

        query = EppsStateMst.query

        if company_code:
            query = query.filter_by(comp_cd=company_code)
        if country_code:
            query = query.filter_by(country_cd=country_code)
        if is_active is not None:
            query = query.filter(EppsStateMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'country_cd' : link.country_cd,
                'state_cd' : link.state_cd,
                'state_nm' : link.state_nm,
                'created_by' : link.created_by,
                'created_dt': link.created_dt,
                'updated_by' : link.updated_by,
                'updated_dt' : link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn': link.active_yn,
                'creator_role_cd' : link.creator_role_cd,
                'updator_role_cd' : link.updator_role_cd,
                'gst_state_cd' : link.gst_state_cd,
                'gstin_type': link.gstin_type,
                'gstin_state_abbr': link.gstin_state_abbr
            })

        return jsonify({
            'state master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
    

ns_subgroup = Namespace('item/subgroup', description="State Master API")

# Define parser for request arguments
parser = reqparse.RequestParser()
parser.add_argument('companyCode', type=int, required=True, help='Provide Company Code')
parser.add_argument('groupCodes', type=str, help='Provide List of groupCodes')
parser.add_argument('subGroupCodes', type=str, help='Provide List of subgroupCodes')
parser.add_argument('isActive', type=int, help='Active 1/0')

@ns_subgroup.route("/v1")
class LocationListView(Resource):
    @ns_subgroup.doc(description='API for fetching location list based on provided location code list',
                     params={
                         'companyCode': 'Provide Company Code',
                         'groupCodes': {'description': 'Provide List of groupCodes', 'type': 'array',
                                       'items': {'type': 'integer'}},
                        'subGroupCodes': {'description': 'Provide List of subgroupCodes', 'type': 'array',
                                       'items': {'type': 'integer'}},
                        
                         'isActive': 'Active 1/0',
                     })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        
        # Parse request arguments
        args = parser.parse_args()
        company_code = args['companyCode']
        is_active = args['isActive']
        group_codes = args.get('groupCodes', [])
        sub_group_codes = args.get('subGroupCodes', [])

        query = EppsMmSubGroupMst.query

        if company_code:
            query = query.filter(EppsMmSubGroupMst.comp_cd == company_code)
        if is_active is not None:
            query = query.filter(EppsMmSubGroupMst.active_yn == ('Y' if is_active == 1 else 'N'))

        # Filter by multiple group codes
        if group_codes:
            group_codes = [int(code) for code in group_codes.split(',')]
            query = query.filter(EppsMmSubGroupMst.grp_cd.in_(group_codes))
        
        # Filter by multiple subgroup codes
        if sub_group_codes:
            sub_group_codes = [int(code) for code in sub_group_codes.split(',')]
            query = query.filter(EppsMmSubGroupMst.grs_cd.in_(sub_group_codes))

        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'grp_cd': link.grp_cd,
                'grs_cd' : link.grs_cd,
                'grs_disp_name' : link.grs_disp_name,
                'grs_long_name' : link.grs_long_name,
                'mnt_grp_flag': link.mnt_grp_flag,
                'created_by' : link.created_by,
                'created_dt' : link.created_dt,
                'updated_by': link.updated_by,
                'updated_dt': link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn' : link.active_yn
            })

        return jsonify({
            'state master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

ns_subsubgroup = Namespace('item/subsubgroup', description="subsubgroup Master API")

# Define parser for request arguments
parser = reqparse.RequestParser()
parser.add_argument('companyCode', type=int, required=True, help='Provide Company Code')
parser.add_argument('groupCodes', type=int, help='Provide List of groupCodes')
parser.add_argument('subGroupCodes', type=int, help='Provide List of subgroupCodes')
parser.add_argument('subSubGroupCodes', type=int, help='Provide List of subsubgroupCodes')
parser.add_argument('isActive', type=int, help='Active 1/0')

@ns_subsubgroup.route("/v1")
class LocationListView(Resource):
    @ns_subsubgroup.doc(description='API for fetching location list based on provided location code list',
                     params={
                         'companyCode': 'Provide Company Code',
                         'groupCodes': {'description': 'Provide List of groupCodes', 'type': 'array',
                                       'items': {'type': 'integer'}},
                        'subGroupCodes': {'description': 'Provide List of subgroupCodes', 'type': 'array',
                                       'items': {'type': 'integer'}},
                        'subSubGroupCodes': {'description': 'Provide List of subgroupCodes', 'type': 'array',
                                       'items': {'type': 'integer'}},
                         'isActive': 'Active 1/0',
                     })
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        
        # Parse request arguments
        args = parser.parse_args()
        company_code = args['companyCode']
        is_active = args['isActive']
        group_codes = args.get('groupCodes', [])
        sub_group_codes = args.get('subGroupCodes', [])
        sub_sub_group_codes = args.get('subSubGroupCodes',[])

        query = EppsMmSubSubGroupMst.query

        if company_code:
            query = query.filter(EppsMmSubSubGroupMst.comp_cd == company_code)
        if is_active is not None:
            query = query.filter(EppsMmSubSubGroupMst.active_yn == ('Y' if is_active == 1 else 'N'))

        # Filter by multiple group codes
        if group_codes:
            group_codes = [int(code) for code in group_codes.split(',')]
            query = query.filter(EppsMmSubSubGroupMst.grp_cd.in_(group_codes))
        
        # Filter by multiple subgroup codes
        if sub_group_codes:
            sub_group_codes = [int(code) for code in sub_group_codes.split(',')]
            query = query.filter(EppsMmSubSubGroupMst.grs_cd.in_(sub_group_codes))

        if sub_sub_group_codes:
            sub_group_codes = [int(code) for code in sub_sub_group_codes.split(',')]
            query = query.filter(EppsMmSubSubGroupMst.grs_cd.in_(sub_sub_group_codes))
        total_records = query.count()

        offset = (page - 1) * per_page

        pagination = query.offset(offset).limit(per_page).all()
        result = []
        for link in pagination:
            result.append({
                'comp_cd': link.comp_cd,
                'grp_cd': link.grp_cd,
                'grs_cd' : link.grs_cd,
                'grss_cd': link.grss_cd,
                'grs_disp_name' : link.grs_disp_name,
                'grs_long_name' : link.grs_long_name,
                'mnt_grp_flag': link.mnt_grp_flag,
                'created_by' : link.created_by,
                'created_dt' : link.created_dt,
                'updated_by': link.updated_by,
                'updated_dt': link.updated_dt,
                'terminal_id': link.terminal_id,
                'active_yn' : link.active_yn
            })

        return jsonify({
            'subsubgroup master': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })

import os
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from .extensions import api


# Define the maximum allowed file size in bytes (e.g., 10MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Modify the upload directory path
upload_dir = '/home/epps/sakshi_workspace/python_my_code/admin_api/uploads'

# Define model for file upload response
ns_upload = Namespace('upload', description="Upload File")

# Define model for file upload response
upload_response_model = api.model('UploadResponse', {
    'message': fields.String(description='Message indicating the status of the file upload'),
    'filename': fields.String(description='Name of the uploaded file')
})

# Define a file upload parser for Flask-Restx
upload_parser = ns_upload.parser()
upload_parser.add_argument('file', location='files', type='file', required=True)

# Route for uploading files
@ns_upload.route('/file')
class UploadFile(Resource):
    @ns_upload.doc(description='Upload a file', parser=upload_parser)
    @ns_upload.response(200, 'Success', upload_response_model)
    def post(self):
        # Access the file from the request
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return {'error': 'No selected file'}, 400

        # Check if the file size exceeds the maximum allowed size
        if len(file.read()) > MAX_FILE_SIZE_BYTES:
            return {'error': 'File size exceeds the maximum allowed size'}, 400
        else:
            file.seek(0)  # Reset file pointer to the beginning for saving the file

        # Save the uploaded file to the specified directory on the server
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file.save(os.path.join(upload_dir, file.filename))

        return {'message': 'File uploaded successfully', 'filename': file.filename}, 200
