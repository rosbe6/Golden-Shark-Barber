import qrcode

# QR para reservas (clientes)
qr_reservas = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr_reservas.add_data("https://goldenbarbershop.online/reserva.html")
qr_reservas.make(fit=True)
img_reservas = qr_reservas.make_image(fill_color="black", back_color="white")
img_reservas.save("qr_reservas.png")
print("✅ QR de reservas creado: qr_reservas.png")

# QR para dashboard (barberos)
qr_dashboard = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr_dashboard.add_data("https://goldenbarbershop.online/dashboard.html")
qr_dashboard.make(fit=True)
img_dashboard = qr_dashboard.make_image(fill_color="black", back_color="white")
img_dashboard.save("qr_dashboard.png")
print("✅ QR de dashboard creado: qr_dashboard.png")