from src.analysis import analysis as anal

with open("test/berkas/image.jpg", "rb") as f: 
    data = f.read()

kunci = "00000000000000000000000000000000000"

anal(data, kunci)