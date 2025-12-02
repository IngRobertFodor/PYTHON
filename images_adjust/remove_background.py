# pip install rembg
# pip install onnxruntime

from rembg import remove # type: ignore
from PIL import Image
import onnxruntime as ort  # type: ignore


input_path = 'C:\\Users\\I070494\\Desktop\\TEST AUTOMATION\\SCRIPTS\\PYTHON\\images_adjust\\tester_with_background.png'
output_path = 'C:\\Users\\I070494\\Desktop\\TEST AUTOMATION\\SCRIPTS\\PYTHON\\images_adjust\\tester_without_background.png'
my_picture_with_background = Image.open(input_path)
my_picture_without_background = remove(my_picture_with_background)
my_picture_without_background.save(output_path)