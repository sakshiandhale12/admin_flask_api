from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from .models import EppsHrEmpMst
from .serializer import EppsLocationMstSchema,EppsMmGroupMstSchema,EppsFinyrMstSchema,EppsDivisionMstSchema, EmployeeSerializer,EppsEcodeMstSchema,EppsDeptMstSerializer,EppsCityMstSerializer,EppsCurrencyMstSerializer,EppsSdCustomerMstSchema
from .models import db
from .models import EppsMmItemMst,EppsMmGroupMst,EppsFinyrMst,EppsHrEmpMst,EppsDivisionMst,VAuditTrailYn,EppsDeptMst,EppsLocationMst, EppsHrProjectResLnk,EppsBusinessZoneMst,EppsEcodeMst,EppsCityMst,EppsSdCustomerMst,EppsCompanyMst,EppsCurrencyMst
from datetime import datetime
from flask import Flask
from flask_jwt_extended import create_access_token, jwt_required,create_refresh_token

# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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
        # location_codes = request.args.getlist('locationCode')
        # parsed_location_codes = []
        # for code in location_codes:
        #     parsed_location_codes.extend(map(int, code.split(',')))
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
            query = query.filter(EppsMmItemMst.grp_cd == groupCodes)
        if subGroupCodes:
            query = query.filter(EppsMmItemMst.grs_cd == subGroupCodes)
        if subSubGroupCodes:
            query = query.filter(EppsMmItemMst.grss_cd == subSubGroupCodes)
        if itemCategories:
            query = query.filter(EppsMmItemMst.item_category == itemCategories)
        if itemCodes:
            query = query.filter(EppsMmItemMst.itemcode == itemCodes)
        # if parsed_location_codes:
        #     query = query.filter(EppsLocationMst.loc_cd.in_(parsed_location_codes))
        if tranIndicatorType:
            query = query.filter(EppsWebNotificationPool.tran_ind_type == tranIndicatorType)
        if is_active is not None:
            query = query.filter(EppsMmItemMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        # Execute the query with pagination and retrieve the results
        pagination = query.offset(offset).limit(per_page).all()

        # Prepare the response data
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
    
#Location MAster


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
from flask import jsonify
from flask_restx import Resource, reqparse
parser = reqparse.RequestParser()
parser.add_argument('companyCode', type=int)
parser.add_argument('divisionCode', type=int)
parser.add_argument('isActive', type=str)
parser.add_argument('locations', type=int, action='append')  # Use action='append' for array parameters

@ns_location.route("/v1/locations")
class EppsHrEmpMstaslocationView(Resource):
    @ns_location.doc(description='Endpoint to get department details', params={
        'companyCode': 'Company Code',
        'isActive': {'description': 'Active dropdown (1 or 0)', 'enum': ['1', '0'], 'type': 'integer'},
        'page': 'Page number',
        'per_page': 'Items per page',
        'locationCode': {'description': 'Provide an array of location codes', 'type': 'array', 'items': {'type': 'integer'}}
    })
    def get(self):
        args = parser.parse_args()
        page = int(args.get('page', 1))
        per_page = min(int(args.get('per_page', 100)), 100)

        company_code = args.get('companyCode')
        location_codes = args.get('locations', [])  # Use get() with default value for array parameters
        is_active = args.get("isActive")
        division_code = args.get('divisionCode')

        # Start building the query
        query = db.session.query(EppsLocationMst)

        if company_code:
            query = query.filter(EppsLocationMst.comp_cd == company_code)
        if division_code:
            query = query.filter(EppsLocationMst.div_cd == division_code)
        if is_active is not None:
            query = query.filter(EppsLocationMst.active_yn == ('Y' if int(is_active) == 1 else 'N'))

        # Filter by multiple location codes
        if location_codes:
            query = query.filter(EppsLocationMst.loc_cd.in_(location_codes))

        total_records = query.count()

        # Continue with your pagination logic
        offset = (page - 1) * per_page
        pagination = query.offset(offset).limit(per_page).all()

        # Convert the result to JSON using marshmallow schema
        result = EppsLocationMstSchema(many=True).dump(pagination)

        return jsonify({
            'department_mst': result,
            'page': page,
            'per_page': per_page,
            'total_items': total_records
        })
