import json

# Your JSON string
json_string = "[{\"productName\":\"ABSTRACT\",\"productPrice\":2999,\"userProductSize\":\"M\",\"userItemCount\":1}]"

# Deserialize the JSON string to a Python dictionary
product_dict = json.loads(json_string)

# Now product_dict is a dictionary
print(product_dict)
