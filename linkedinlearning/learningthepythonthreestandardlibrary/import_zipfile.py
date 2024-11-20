import zipfile


# Create a new zip object.
zip = zipfile.ZipFile("files_to_zip.zip", "r")

# List the files in the zip file.
print(zip.namelist())
print()

# Get information about a specific file in the zip file.
print(zip.getinfo("file_to_zip_one.txt"))
print(zip.getinfo("file_to_zip_two.txt"))
print()

# Read the contents of a specific file in the zip file.
print(zip.read("file_to_zip_one.txt"))
# Output: b'My content.'
# "b" means bytes.

# Extract a file from the zip file.
#zip.extract("file_to_zip_one.txt")
# Extract all files from the zip file.
#zip.extractall()

# Close the zip file.
zip.close()