import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        if not self.email_from or not self.email_password:
            print("❌ ERROR: EMAIL_FROM o EMAIL_PASSWORD no configurados en .env")
        else:
            print(f"✅ Gmail configurado: {self.email_from}")
    
    def enviar_email(self, to, subject, html):
        """Enviar email genérico con Gmail (método público)"""
        return self._enviar_email(to, subject, html)
    
    def enviar_confirmacion(self, cita_data, cita_id):
        """Enviar email de confirmación al cliente"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                <div style="background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #007bff; margin-bottom: 20px; text-align: center;">✓ Your appointment is confirmed!</h2>
                        
                        <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                        
                        <p>Thank you for booking with <strong>Gold Shark Barber</strong>. Your appointment has been confirmed.</p>
                        
                        <div style="background-color: #f9f9f9; padding: 20px; border-left: 4px solid #007bff; margin: 30px 0; border-radius: 4px;">
                            <h3 style="margin-top: 0; color: #007bff;">Appointment Details:</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Service:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">{cita_data['servicio']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Date:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">{cita_data['dia']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">{cita_data['hora']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Payment:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">{cita_data['metodoPago'].capitalize()}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;"><strong>Price:</strong></td>
                                    <td style="padding: 10px 0; text-align: right;"><strong style="color: #28a745;">${cita_data['precio']}</strong></td>
                                </tr>
                            </table>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://goldenbarbershop.online/cita.html?id={cita_id}"
                               style="background-color: #007bff; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
                                View or Cancel Appointment
                            </a>
                        </p>
                        
                        <p>If you need to cancel or reschedule, you can do so from the link above.</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                            <strong>Gold Shark Barber</strong><br>
                            We look forward to seeing you!<br>
                            <a href="https://goldenbarbershop.online" style="color: #007bff; text-decoration: none;">Visit our website</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Confirmed - {cita_data['dia']} at {cita_data['hora']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error al enviar email de confirmación: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_cancelacion(self, cita_data, motivo):
        """Enviar email de cancelación al cliente"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                <div style="background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #dc3545; margin-bottom: 20px; text-align: center;">✗ Appointment Cancelled</h2>
                        
                        <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                        
                        <p>We regret to inform you that your appointment with <strong>Gold Shark Barber</strong> has been cancelled.</p>
                        
                        <div style="background-color: #ffe8e8; padding: 20px; border-left: 4px solid #dc3545; margin: 30px 0; border-radius: 4px;">
                            <h3 style="margin-top: 0; color: #dc3545;">Cancelled Appointment:</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf;"><strong>Date:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf; text-align: right;">{cita_data['dia']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf;"><strong>Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf; text-align: right;">{cita_data['hora']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf;"><strong>Service:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #f0cccf; text-align: right;">{cita_data['servicio']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;"><strong>Reason:</strong></td>
                                    <td style="padding: 10px 0; text-align: right;">{motivo}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://goldenbarbershop.online/reserva.html" 
                               style="background-color: #dc3545; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
                                Book a New Appointment
                            </a>
                        </p>
                        
                        <p>We'd love to see you again soon. Feel free to book a new appointment whenever you're ready.</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                            <strong>Gold Shark Barber</strong><br>
                            <a href="https://goldenbarbershop.online" style="color: #007bff; text-decoration: none;">Visit our website</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Cancelled - {cita_data['dia']} at {cita_data['hora']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error al enviar email de cancelación: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_reagendamiento(self, cita_data, nueva_fecha, nueva_hora, motivo):
        """Enviar email de reagendamiento al cliente"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                <div style="background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #ffc107; margin-bottom: 20px; text-align: center;">📅 Appointment Rescheduled</h2>
                        
                        <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                        
                        <p>Your appointment at <strong>Gold Shark Barber</strong> has been rescheduled to a new date and time.</p>
                        
                        <div style="background-color: #fff8f0; padding: 20px; border-left: 4px solid #ffc107; margin: 30px 0; border-radius: 4px;">
                            <h3 style="margin-top: 0; color: #ffc107;">Your New Appointment:</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc;"><strong>Previous Date:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right;"><s>{cita_data['dia']}</s></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc;"><strong>Previous Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right;"><s>{cita_data['hora']}</s></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; background-color: #ffffee;"><strong>New Date:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right; background-color: #ffffee;"><strong style="color: #28a745;">{nueva_fecha}</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; background-color: #ffffee;"><strong>New Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right; background-color: #ffffee;"><strong style="color: #28a745;">{nueva_hora}</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc;"><strong>Service:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right;">{cita_data['servicio']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;"><strong>Reason:</strong></td>
                                    <td style="padding: 10px 0; text-align: right;">{motivo}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://goldenbarbershop.online/cita.html?id={cita_data.get('_id', '')}" 
                               style="background-color: #ffc107; color: #000; padding: 14px 40px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
                                View Your New Appointment
                            </a>
                        </p>
                        
                        <p>Please confirm that you can attend at the new date and time. If you have any questions, feel free to contact us.</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                            <strong>Gold Shark Barber</strong><br>
                            We look forward to seeing you!<br>
                            <a href="https://goldenbarbershop.online" style="color: #007bff; text-decoration: none;">Visit our website</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Rescheduled - New Date: {nueva_fecha} at {nueva_hora}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error al enviar email de reagendamiento: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_recordatorio(self, cita_data, cita_id):
        """Enviar email de recordatorio 24h antes"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                <div style="background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff9800; margin-bottom: 20px; text-align: center;">⏰ Appointment Reminder</h2>
                        
                        <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                        
                        <p>This is a reminder that you have an appointment with <strong>Gold Shark Barber</strong> tomorrow!</p>
                        
                        <div style="background-color: #fff8f0; padding: 20px; border-left: 4px solid #ff9800; margin: 30px 0; border-radius: 4px;">
                            <h3 style="margin-top: 0; color: #ff9800;">Tomorrow's Appointment:</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc;"><strong>Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ffe0cc; text-align: right;">{cita_data['hora']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;"><strong>Service:</strong></td>
                                    <td style="padding: 10px 0; text-align: right;">{cita_data['servicio']}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://goldenbarbershop.online/cita.html?id={cita_id}" 
                               style="background-color: #ff9800; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
                                View Appointment
                            </a>
                        </p>
                        
                        <p style="text-align: center;">See you soon!</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                            <strong>Gold Shark Barber</strong><br>
                            <a href="https://goldenbarbershop.online" style="color: #007bff; text-decoration: none;">Visit our website</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Reminder: Your appointment tomorrow at {cita_data['hora']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error al enviar recordatorio: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_notificacion_barbero(self, cita_data, cita_id, email_barbero):
        """Enviar notificación al barbero cuando un cliente reserva"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                <div style="background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #28a745; margin-bottom: 20px; text-align: center;">📅 New Appointment Booked!</h2>
                        
                        <p>Hello,</p>
                        
                        <p>A new appointment has been booked at your barbershop. Here are the details:</p>
                        
                        <div style="background-color: #f0f8f0; padding: 20px; border-left: 4px solid #28a745; margin: 30px 0; border-radius: 4px;">
                            <h3 style="margin-top: 0; color: #28a745;">New Appointment:</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Client Name:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['cliente_nombre']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['cliente_email']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Phone:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['cliente_telefono']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Service:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['servicio']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Date:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['dia']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Time:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['hora']}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Payment:</strong></td>
                                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd; text-align: right;">{cita_data['metodoPago'].capitalize()}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;"><strong>Price:</strong></td>
                                    <td style="padding: 10px 0; text-align: right;"><strong style="color: #28a745;">${cita_data['precio']}</strong></td>
                                </tr>
                            </table>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://goldenbarbershop.online/dashboard.html" 
                               style="background-color: #28a745; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
                                Go to Dashboard
                            </a>
                        </p>
                        
                        <p style="font-size: 12px; color: #999; text-align: center;">
                            <strong>Gold Shark Barber</strong><br>
                            Appointment ID: {cita_id}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=email_barbero,
                subject=f"New Appointment - {cita_data['cliente_nombre']} on {cita_data['dia']} at {cita_data['hora']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error al enviar notificación al barbero: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def _enviar_email(self, to, subject, html):
        """Enviar email genérico con Gmail (método privado)"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to
            msg['Reply-To'] = self.email_from
            
            # Agregar versión de texto plano
            text_part = MIMEText('Please view this email in HTML format.', 'plain', 'utf-8')
            html_part = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Conectar a Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email_from, self.email_password)
            server.sendmail(self.email_from, to, msg.as_string())
            server.quit()
            
            print(f"✅ Email enviado a {to}")
        except Exception as e:
            print(f"❌ Error al enviar email: {str(e)}")
            raise