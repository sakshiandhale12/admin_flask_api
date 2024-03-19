from marshmallow import Schema, fields
# from .resources import ns
class EmployeeFilterDTO(Schema):
    companyCode = fields.Integer(default=1)
    divisionCode = fields.Integer()
    employeeCode = fields.String()
    emailId = fields.String()
    isActive = fields.Integer()
    employeeType = fields.String()
    reportingEmpCode = fields.String()
    auditTrailYn = fields.Integer(default=0)
    
class EmployeeCreateDTO:
    def __init__(self, emp_first_name, emp_last_name, emp_mob_no, emp_mail_id, emp_password, emp_type):
        self.emp_first_name = emp_first_name
        self.emp_last_name = emp_last_name
        self.emp_mob_no = emp_mob_no
        self.emp_mail_id = emp_mail_id
        self.emp_password = emp_password
        self.emp_type = emp_type

# employee_dto = ns.model('EmployeeDTO', {
#     'companyCode': fields.Integer(default=1),
#     'divisionCode': fields.Integer(),
#     'employeeCode': fields.String(),
#     'employeeTitle': fields.String(),
#     'emp_first_name': fields.String(),
#     'emp_mail_id' : fields.String(),
#     'dept_cd': fields.Integer(),
#     'emp_password': fields.String(),
#     'created_by': fields.String(),
#     'created_dt': fields.String(),
#     'emp_type': fields.String(),
#     'auto_created': fields.Integer()
# })