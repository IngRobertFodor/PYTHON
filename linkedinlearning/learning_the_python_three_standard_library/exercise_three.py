def create_file(file_path, contents):
    with open(file_path, 'w') as file:
        file.write(contents)

def count_words(file_path):
    my_file = open(file_path, "r")
    my_file_text = my_file.read()
    #print(my_file_text)
    if len(my_file_text) == 0:
        return print("File is empty.")
    else:
        return print(len(my_file_text.split()))


file_path = "my_article.txt"
contents = "The movie industry is undergoing significant changes due to new trends, with streaming services making films more accessible to a wider audience."


create_file(file_path, contents)
result = count_words(file_path)