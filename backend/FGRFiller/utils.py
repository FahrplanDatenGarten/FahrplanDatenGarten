import io
import os
import time
import tempfile
import subprocess
from fdfgen import forge_fdf

def test_gen():
    full_dict = {
        "S1F1":'02', "S1F2":'04', "S1F3":'', "S1F4":'Göttingen', "S1F5":'', "S1F6":'', "S1F7":'Berlin', "S1F8":'', "S1F9":'', "S1F10":'', "S1F11":'', "S1F12":'', "S1F13":'', "S1F14":'', "S1F15":'', "S1F16":'', "S1F17":'', "S1F18":'', "S1F19":'', "S1F20":'', "S1F21":'', "S1F22":'', "S1F23":'', "S1F24":'', "S1F25":'', "S1F26":'', "S1F27":'', "S1F28":'', "S1F29":'', "S2F2":'', "S2F3":'', "S2F4":'', "S2F5":'', "S2F6":'', "S2F7":'', "S2F8":'', "S2F9":'', "S2F10":'', "S2F11":'', "S2F12":'', "S2F13":'', "S2F15":'', "S2F16":'', "S2F17":'', "S2F18":'', "S2F19":'', "S2F20":'', "S2F21":'', "S2F22":'', "S2F23":'', "S2F1":''
    }
    return generate_form(full_dict)

def generate_form(fields, pdftk="pdftk", *args, **kwargs):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    fp = tempfile.NamedTemporaryFile(delete=False)
    fpdf = tempfile.NamedTemporaryFile(delete=False)
    fdf = forge_fdf("", fields, [], [], [])
    fp.write(fdf)
    fp.close()
    subprocess.run([pdftk, dir_path + '/fahrgastrechte.pdf', "fill_form", fp.name, "output", fpdf.name])

    fpdf.seek(0)
    pdf = io.BytesIO()
    pdf.write(fpdf.read())

    fpdf.close()
    os.unlink(fp.name)
    os.unlink(fpdf.name)
    pdf.seek(0)
    return pdf
