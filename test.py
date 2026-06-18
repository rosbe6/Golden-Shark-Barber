import qrcode
from PIL import Image

# URL a donde va el QR
url = "https://goldenbarbershop.online/"

# Crear QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Imagen QR
qr_img = qr.make_image(fill_color="black", back_color="white")

# Abrir logo
logo = Image.open('C:/Golden-Shark-Barber/backend/static/images/logo.jpeg')

# Redimensionar logo
qr_width, qr_height = qr_img.size
logo_size = qr_width // 5
logo = logo.resize((logo_size, logo_size))

# Centrar logo
logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

# Pegar
qr_img.paste(logo, logo_pos)

# Guardar
qr_img.save('C:/Golden-Shark-Barber/backend/static/images/qr_code.png')

print("✅ QR creado: qr_code.png")
print(f"📱 Código para: {url}")