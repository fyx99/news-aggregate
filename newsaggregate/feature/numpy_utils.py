
from io import StringIO, BytesIO
import numpy as np

def numpy_2d_array_as_text(array):
    if len(array.shape) > 2:
        raise Exception("Only supports 2 dims")
    string_io = StringIO()
    np.savetxt(string_io, array)
    return string_io.getvalue()

    
def text_to_numpy_2d(bytes):

    bytes_io = BytesIO(bytes)
    array = np.loadtxt(bytes_io, dtype="float32")
    return array