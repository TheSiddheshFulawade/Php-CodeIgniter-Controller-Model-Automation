#####
import openpyxl
validation_dictionary = {'int': '!is_numeric', 'string': '!is_string', 'date': '!is_date', 'max': '<$max', 'min': '>$min'}
def validation(required_fields):
    result = [] 
    x = f'''$req = {required_fields};
                $int = {integer_values};
                $str = {string_values}
                //Calling check_empty function for validation
                $this->check_empty($postobj, $req);
                //Calling check_int function for validation  
                $this->check_int($int);
                //Calling check_string function for validation 
                $this->check_string($str);'''
    
    result.append('\t')
    
    result.append('\t')
    result.append('\t')
    result.append(x)
    result.append('\n')
    
       
    output = ''.join(result) 

    return output

def makeController(tableName, arrFields):
    def starter_template():
        start_code = '''<?php
use Restserver\Libraries\REST_Controller;
class '''+tableName+'''_Controller extends REST_Controller 
    {
        public function __construct() 
        {
            parent::__construct();
            $this->load->model(' '''+tableName+'''_model');
        }'''
        return start_code
    
    def select():
        select_code = '''\n\t\t //Select all records
        public function '''+tableName+'''_get_data_post() 
        {
            try{
                $postobj = $this->post();
                $result = $this->'''+tableName+'''_model->'''+tableName+'''_get_data();
                if ($result)
                {
                    $this->response($result, REST_Controller::HTTP_OK);
                } else {
                    $this->response(['message' => 'No users found.'], REST_Controller::HTTP_NOT_FOUND);
                    }
                }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''

        return select_code
    
    def get_By_ID():
        get_By_ID_code = '''\n\t\t //Get records by ID
        public function '''+tableName+'''_get_data_by_id_post()
        {
            try{
                $postobj = $this->post();
                $result = $this->'''+tableName+'''_model->'''+tableName+'''_get_data_by_id($postobj['id']);
                if ($result) 
                {
                    $this->response($users, REST_Controller::HTTP_OK);
                } else {
                    $this->response(['message' => 'No users found.'], REST_Controller::HTTP_NOT_FOUND);
                    }
                }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        return get_By_ID_code

    def insert():
        insert_code = '''\n\t\t//Post the records
        public function '''+tableName+'''_add_post() 
        {
            try{
                //Defining the variables:
                $data1 = [];
                $postobj = $this->post();
    %s
                //Calling the function from Model for max-min Validation
    %s
                //Calling the function from Model for int Validation
    %s
                //Calling the function from Model for max value Validation
    %s
                //Calling the function from Model for date Validation
    %s
                //Calling the function from Model for string Validation
    %s
    %s

                $id = $this->'''+tableName+'''_model->'''+tableName+'''_add($data1);
                if ($userId) 
                {
                    $this->response(['message' => 'User created.', ' '''+tableName+''' ' => $userId], REST_Controller::HTTP_CREATED);
                } else {
                    $this->response(['message' => 'Failed to create user.'], REST_Controller::HTTP_BAD_REQUEST);
                }
            }

            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        
        validations = validation(required_fields)
        
               
        #max-min
        output_for_maxmin = ""
        for max_val, min_val, field in zip(max_value, min_value, table_values):
            if isinstance(max_val, int) and isinstance(min_val, int):
                output_for_maxmin += f'''
                if (!$this->table_model->checklength("{field}",{min_val},{max_val}))
                {{
                    $this->response(['message' => 'Entered {field} value is out of range', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }}'''
        
        #int
        int_valid1 = []
        for g1 in arrFields:
            if g1[4] == 'int':
                int_valid1.append('''if (!$this->table_model->validateInteger(" '''+g1[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g1[0]+''' value is not a valid integer', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')        
        int_valid1 = "\n\t".join("\t\t\t" + line for line in int_valid1)
        
        #max value
        max_valid = []
        for g2 in arrFields:
            if g2[4] == 'int' and g2[7] is not None:
                max_valid.append('''if (!$this->table_model->max_value(" '''+g2[0]+''' ", '''+str(g2[7])+'''))
                {
                    $this->response(['message' => 'Entered '''+g2[0]+''' value is more than the maxvalue', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        max_valid = "\n\t".join("\t\t\t" + line for line in max_valid)
        
        #date
        date_valid = []
        for g1 in arrFields:
            if g1[4] == 'date':
                date_valid.append('''if (!$this->table_model->date_validation(" '''+g1[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g1[0]+''' value is not a valid date', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        date_valid = "\n\t".join("\t\t\t" + line for line in date_valid)
                
        #string
        string_values1 = []
        for g3 in arrFields:
            if g3[4] == 'string':
                string_values1.append('''if (!$this->table_model->validateString(" '''+g3[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g3[0]+''' value is not a valid string', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        string_values1 = "\n\t".join("\t\t\t" + line for line in string_values1)
        
        
        required_fields_code2 = [] 
        for b in required_fields:
            required_fields_code2.append('''$data1[' '''+b+''' ']=$data1[' '''+b+''' '];''')
        required_fields_code2 = "\n\t".join("\t\t\t" + line for line in required_fields_code2)

        
        insert_code_1 = insert_code % (validations, output_for_maxmin, int_valid1, max_valid, date_valid, string_values1, required_fields_code2) 

        return insert_code_1

    def update():
        update_code = '''\n\t\t//Update the records
        public function '''+tableName+'''_update_post() 
        {
            try{
                //Defining the variables:
                $condition = [];
                $postobj = $this->post();
    %s
                //Calling the function from Model for max-min Validation
    %s
                //Calling the function from Model for int Validation
    %s
                //Calling the function from Model for max value Validation
    %s
                //Calling the function from Model for date Validation
    %s
                //Calling the function from Model for string Validation
    %s
    %s
                $userId = $this->'''+tableName+'''_model->'''+tableName+'''_update($condition, $postobj);
                if ($userId) 
                {
                    $this->response(['message' => 'User updated.', '  '''+tableName+''' ' => $userId], REST_Controller::HTTP_OK);
                } else {
                    $this->response(['message' => 'Failed to update user.'], REST_Controller::HTTP_BAD_REQUEST);
                }
            }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        
        validations = validation(required_fields)
        
        #max-min
        output_for_maxmin = ""
        for max_val, min_val, field in zip(max_value, min_value, table_values):
            if isinstance(max_val, int) and isinstance(min_val, int):
                output_for_maxmin += f'''
                if (!$this->table_model->checklength("{field}",{min_val},{max_val}))
                {{
                    $this->response(['message' => 'Entered {field} value is out of range', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }}'''
        
        #int
        int_valid1 = []
        for g1 in arrFields:
            if g1[4] == 'int':
                int_valid1.append('''if (!$this->table_model->validateInteger(" '''+g1[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g1[0]+''' value is not a valid integer', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')        
        int_valid1 = "\n\t".join("\t\t\t" + line for line in int_valid1)
        
        #max value
        max_valid = []
        for g2 in arrFields:
            if g2[4] == 'int'and g2[7] is not None:
                max_valid.append('''if (!$this->table_model->max_value(" '''+g2[0]+''' ", '''+str(g2[7])+'''))
                {
                    $this->response(['message' => 'Entered '''+g2[0]+''' value is more than the maxvalue', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        max_valid = "\n\t".join("\t\t\t" + line for line in max_valid)
        
        #date
        date_valid = []
        for g1 in arrFields:
            if g1[4] == 'date':
                date_valid.append('''if (!$this->table_model->date_validation(" '''+g1[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g1[0]+''' value is not a valid date', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        date_valid = "\n\t".join("\t\t\t" + line for line in date_valid)
        
        #string
        string_values1 = []
        for g3 in arrFields:
            if g3[4] == 'string':
                string_values1.append('''if (!$this->table_model->validateString(" '''+g3[0]+''' "))
                {
                    $this->response(['message' => 'Entered '''+g3[0]+''' value is not a valid string', 'status' => "false"], REST_Controller::HTTP_CREATED);
                }''')
        string_values1 = "\n\t".join("\t\t\t" + line for line in string_values1)
        
        unique_fields_code2 = []
        for a3 in unique_fields:
            unique_fields_code2.append('''$condition[' '''+a3+''' ']=$postobj[' '''+a3+''' '];''')
        unique_fields_code2 = "\n\t".join("\t\t\t" + line for line in unique_fields_code2)
        
        update_code_1 = update_code % (validations, output_for_maxmin, int_valid1, max_valid, date_valid, string_values1, unique_fields_code2)  
      
        return update_code_1
  
    
    def delete():
        delete_code = '''\n\t\t 
        //Delete the post
        public function '''+tableName+'''_delete_post($id) 
        {
            try{
    %s
                $deleted = $this->'''+tableName+'''_model->'''+tableName+'''_delete($id);
                if ($deleted) 
                {
                    $this->response(['message' => 'User deleted.'], REST_Controller::HTTP_OK);
                } else {
                    $this->response(['message' => 'Failed to delete user.'], REST_Controller::HTTP_BAD_REQUEST);
                }
            }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        
        unique_fields_code2 = []
        for a3 in unique_fields:
            unique_fields_code2.append('''$condition[' '''+a3+''' ']=$postobj[' '''+a3+''' '];''')
        unique_fields_code2 = "\n\t".join("\t\t\t" + line for line in unique_fields_code2)
        
        
        delete_code_1 = delete_code % (unique_fields_code2) 
        
        return delete_code_1
    
    
    def checkemptyfunction():
        checkempty_code = '''
        //Check Empty Optimisation        
        public function check_empty($postobj,$array)
        {
            try{
                foreach($array as $key=>$value)
                {
                    if (!empty($postobj[$value]))
                    {
                        return $this->response(['message' => $value." Required", 'status' => "false"], REST_Controller::HTTP_CREATED);
                    }
                }   
            }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        
        return checkempty_code
    
    
    def checkintfunction():
        checkint_code = '''
        //Int function Optimisation
        public function check_int($int_array)
        {
            try{
                foreach($int_array as $key=>$value)
                {
                    if (!$this->table_model->validateInteger("$value"))
                    {
                        return $this->response(['message' => 'Entered $value value is not a valid integer', 'status' => "false"], REST_Controller::HTTP_CREATED);
                    }
                }
            }
            catch(Exception $e)
            {
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }'''
        
        return checkint_code
    
    
    def checkstringfunction():
        checkstring_code = '''
        //String function Optimisation
        public function check_string($str_array)
        {
            try{
                foreach($str_array as $key=>$value)
                {
                    if (!$this->table_model->validateString("$value"))
                    {
                        return $this->response(['message' => 'Entered $value value is not a valid string', 'status' => "false"], REST_Controller::HTTP_CREATED);
                    }
                }
            }
            catch(Exception $e)
            {    
                return $this->response(['message' => 'Exception error please check.'], REST_Controller::HTTP_BAD_REQUEST);
            }
        }
    }'''
        return checkstring_code
    
    fun1= starter_template()
    fun2= select()
    fun3= get_By_ID()
    fun4= insert()
    fun5= update()
    fun6= delete()
    fun7 = checkemptyfunction()
    fun8 = checkintfunction()
    fun9 = checkstringfunction()
    return (fun1+fun2+fun3+fun4+fun5+fun6+fun7+fun8+fun9)


def makeModel(tableName, arrFields):
    def starter_template_model():
        start_code_model = ''' <?php
class '''+tableName+'''_model extends CI_Model {
    public function __construct() {
        parent::__construct();
        $this->load->database(); // Load the database library
    }'''
        return start_code_model
    
    def select_model():
        select_code_model = '''
    //Select all records
    public function '''+tableName+'''_get_data() {
        $query = $this->db->get(' '''+tableName+''' '); // Select all records from 'users' table
        return $query->result(); // Return the result as an array of objects
    }'''
        return select_code_model
    
    def get_By_ID_model():
        get_By_ID_code_model = '''
    //Get records by ID
    public function '''+tableName+'''_get_data_by_id($condition) {
        $this->db->where($condition)
        $query = $this->db->get(' '''+tableName+''' '); // Select all records from 'users' table
        return $query->result(); // Return the result as an array of objects
    } '''
       
        return  get_By_ID_code_model
   
    def insert_model():
        insert_code_model = '''
    //Post the records
    public function '''+tableName+'''_add($postobj) {
        $this->db->insert(' '''+tableName+''' ', $postobj); // Insert data into 'users' table
%s
    }'''
        
        unique_fields_code2 = [] 
        for b in unique_fields:
            unique_fields_code2.append('''return $this->db->insert_'''+b+'''(); // Return the inserted record ID''') 
        unique_fields_code2 = "\n".join("\t\t" + line for line in unique_fields_code2)
        
        insert_code_model_1 = insert_code_model % (unique_fields_code2)
        
        
        return insert_code_model_1
        
    def update_model():
        update_code_model = ''' 
    //Update the records
    public function '''+tableName+'''_update($condition, $postobj) {
        $this->db->where($condition)
        $this->db->update(' '''+tableName+''' ', $postobj); // Update the record in 'users' table
        return $this->db->affected_rows(); // Return the number of affected rows
    }'''
        
        return update_code_model
    
    def delete_model():
        delete_code_model = ''' 
    //Delete the post
    public function '''+tableName+'''_delete($condition) {
        $this->db->where($id);
        $this->db->delete(' '''+tableName+''' '); // Delete the record from 'users' table
        return $this->db->affected_rows(); // Return the number of affected rows
    }'''
  
        return delete_code_model
    
    def checklength():
        checklength_code = '''
    //Function to checklength
    function checklength($string,$min,$max){
      $len= strlen($string);
      if($len<$min || $len>$max) {
          return false;
    } else {
          return true;
      }
    }'''   

        return checklength_code
        
    def checkmaxvalue():
        checkmaxvalue_code = '''
    //Function to check max value    
    function max_value($string, $table_value){
	  if ($string <= $table_value) {
          return true;
    } else {
          return false;
      }
    }'''
        
        return checkmaxvalue_code        
        
    def checkdate():
        checkdate_code = '''
    //Function to checkdate
    function date_validation($table_date){
      $date_parts = explode("-", $table_date); 
      $year = intval($date_parts[0]);
      $month = intval($date_parts[1]);
      $day = intval($date_parts[2]);

      if (checkdate($month, $day, $year)) {
          return true;
      } else {
          return false;
        }
    }'''
        
        return checkdate_code
    
    def checkint():
        checkint_code = '''
    //Function to check int
    function validateInteger($value){
	  if (is_numeric($value) && intval($value) == $value) {
    	return true;
      } else {
          return false;
        }
    }'''
        return checkint_code
    
    def checkstring():
        checkstring_code = '''
    //Function to check string
    function validateString($string) {
        $pattern = '/^[a-zA-Z\s@_.]+$/';
        if ((bool) preg_match($pattern, $string)) {
            return var_export(true);
        } else {
            return var_export(false);
          }
    }
}'''
        return checkstring_code   
    
    mod1 = starter_template_model()
    mod2 = select_model()
    mod3 = get_By_ID_model()
    mod4 = insert_model()
    mod5 = update_model()
    mod6 = delete_model()
    mod7 = checklength()
    mod8 = checkmaxvalue()
    mod9 = checkdate()
    mod10 = checkint()
    mod11 = checkstring()
        
    
    return (mod1+mod2+mod3+mod4+mod5+mod6+mod7+mod8+mod9+mod10+mod11)

# Open the Excel file
workbook = openpyxl.load_workbook('bonustable3.xlsx')

# Select the first sheet
sheet = workbook.active

# Variables for storing tableName and arrFields
tableName = None
arrFields = []


# Iterate over each row in the sheet
for row in sheet.iter_rows(values_only=True):
    cell1 = row[0]
    cell2 = row[1]
    if cell1 and not cell2:
        # Save the value of the first cell in tableName
        tableName = cell1
        
    elif cell1 and cell2:
        # Add the row as an array in arrFields
        arrFields.append(row)
        
        #Unique Fields Extraction  
        unique_fields = []
        for a in arrFields:
            if a[2] == 'yes':
                unique = a[0]
                unique_fields.append(unique)


        #Required Fields Extraction  
        required_fields = []
        for a in arrFields:
            if a[3] == 'yes':
                required = a[0]
                required_fields.append(required)

            
        #Validation for Required Fields
        validation_required_fields = []
        for a in arrFields:
            if a[3] == 'yes':
                validation_required_fields.append(a[4])
            elif a[3] == None:
                validation_required_fields.append(None)
                
                
        #All the Required Fields
        all_required_fields = []
        for a in arrFields:
            if a[3] == 'yes':
                all_required_fields.append(a[0])
            elif a[3] == None:
                all_required_fields.append(None)
                
                
        #All Unique Fields
        all_unique_fields = []
        for a in arrFields:
            if a[2] == 'yes':
                all_unique_fields.append(a[4])
            elif a[2] == None:
                all_unique_fields.append(None)
                
                
        #Validation for Unique Fields
        validation_unique_fields = []
        for a in arrFields:
            if a[2] == 'yes':
                validation_unique_fields.append(a[4])
            elif a[2] == None:
                validation_unique_fields.append(None)
                
         
        #Extracting Max and Min Values
        max_value = []
        min_value = []
        for num in arrFields:
            max_value.append(num[6])
            min_value.append(num[5])

        for i in range(len(max_value)):
            if not isinstance(max_value[i], int):
                max_value[i] = None

        for i in range(len(min_value)):
            if not isinstance(min_value[i], int):
                min_value[i] = None
                
        max_value.pop(0)
        min_value.pop(0)
        
        
        #Extracting the Table Values
        table_values = []
        for y1 in arrFields:
            table_values.append(y1[0])
        table_values.pop(0)
        
        #Integer Values
        integer_values = []
        for r in arrFields:
            if r[4] == 'int':
                integer_values.append(r[0])
        
        #String Values
        string_values = []
        for r in arrFields:
            if r[4] == 'string':
                string_values.append(r[0])
        
        file_name = tableName+"_Controller.php"  
        with open(file_name, 'w') as file:
            file.write(makeController(tableName, arrFields))
            
        file_name = tableName+"_Model.php"  
        with open(file_name, 'w') as file:
            file.write(makeModel(tableName, arrFields))

    elif not cell1:
        makeController(tableName, arrFields)
        makeModel(tableName, arrFields)
        tableName = None
        arrFields = []

    
print("Current Table name is: ",tableName)
print ("Current Table Values are: ",table_values)
print ("Current Unique Fields are: ",all_unique_fields)
print ("Current all Required Fields are: ",all_required_fields)
print("Current Validations for Unique Fields are: ",validation_unique_fields)
print("Current Validations for Required Fields are: ",validation_required_fields)
print("Current Table max values are: ",max_value)
print("Current Table min values are: ",min_value)
print("Current Table value is: ",arrFields)
