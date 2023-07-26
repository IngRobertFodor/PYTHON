import file_for_import_custom_modules_3_1
from file_for_import_custom_modules_3_1 import multiplication

from custom_modules.variablesfunctions_in_customs_modules_folder import my_function_to_test_import


print(file_for_import_custom_modules_3_1.addition(2,5))
print("This is the value from variable a: " + str(file_for_import_custom_modules_3_1.a) + ", from file with this name: ""file_for_import_custom_modules_3_1"".")
print(file_for_import_custom_modules_3_1.a)
print(multiplication(2,5))

my_function_to_test_import()