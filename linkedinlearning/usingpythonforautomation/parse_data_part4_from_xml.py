import xml.etree.ElementTree as ET


file_path = "groceries.xml"
tree = ET.parse(file_path)
root = tree.getroot()
items_over_six = []
for item in root.findall("grocery_item"):
    name = item.find("name").text
    price = item.find("price").text
    print(name, price)
    if float(price) > 6:
        items_over_six.append(name)
print("")
print(items_over_six)