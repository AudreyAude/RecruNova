import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def mailRegister(receiver_email,nom,password):
        sender_email='recrunova0@gmail.com'
        message = MIMEMultipart("alternative")
        message["Subject"] = "Bienvenue chez RecruNova"
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Bcc"]= sender_email
       
        html=html =f"""\
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px;">
            
            <h2 style="color: #0d6efd;">Bonjour {nom}  </h2>
            <p style="font-size: 16px; color: #333;">
                Nous sommes ravis de vous accueillir sur RecruNova !<br><br>
                Votre inscription a été complétée avec succès et vous faites désormais partie de notre communauté. Nous sommes impatients de vous accompagner dans vos démarches et de vous offrir une expérience enrichissante.<br><br>
        N’hésitez pas à explorer toutes les fonctionnalités de notre plateforme :<br>
        1- <a href="#" style="display: inline-block; padding: 10px 20px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 4px;">
                consulter les offre d'emploi
            </a><br>
      
        2-<a href="#" style="display: inline-block; padding: 10px 20px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 4px;">
                candidater directement
            </a>
        3-Cree un profil detaille <br><br><br> Si vous avez des questions ou besoin d'aide, notre équipe est à votre disposition. Vous pouvez nous contacter à tout moment via recrunova0@gmail.com

            </p>

            <a href="https://realpython.com" style="display: inline-block; padding: 10px 20px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 4px;">
                Visiter Real Python
            </a>

            <hr style="margin: 30px 0;">

            <p >
                Merci de faire partie de RecruNova. Nous vous souhaitons une expérience réussie et pleine de succès !<br>
                <strong>– L’équipe RecruNova</strong>
            </p>
            </div>
        </body>
        </html>
        """
        part=MIMEText(html,"html")
        message.attach(part)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
                return("Email envoyé avec succès !")
        except Exception as e:
                return(" Échec de l'envoi :", e)
        
def mailPostuleCandidat(receiver_email,nom,password):
        sender_email='recrunova0@gmail.com'
        message = MIMEMultipart("alternative")
        message["Subject"] = f"candidature via ReCruNova"
        message["From"] = sender_email
        message["To"] = receiver_email
     
        
        html=f"""\
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px;">
            
            <h2 style="color: #0d6efd;">Bonjour {nom}  </h2>
            <p style="font-size: 16px; color: #333;">
                Merci d’avoir postulé à une offre d’emploi sur <strong>RecruNova</strong> !<br><br>
        Nous avons bien reçu votre candidature et nous la transmettrons à l’employeur concerné dans les plus brefs délais Bonne chance!
            </p>


            <hr style="margin: 30px 0;">

            <p >
                Merci de faire partie de RecruNova. Nous vous souhaitons une expérience réussie et pleine de succès !<br>
                <strong>– L’équipe RecruNova</strong>
            </p>
            </div>
        </body>
        </html>
        """
        part=MIMEText(html,"html")
        message.attach(part)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
                return("Email envoyé avec succès !")
        except Exception as e:
                return(" Échec de l'envoi :", e)
        

        
def mailNotifyEmployeur(receiver_email,nom,password):
        sender_email='recrunova0@gmail.com'
        message = MIMEMultipart("alternative")
        message["Subject"] = f"candidature via ReCruNova"
        message["From"] = sender_email
        message["To"] = receiver_email
     
        
        html=f"""\
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px;">
            
            <h2 style="color: #0d6efd;">Bonjour {nom}  </h2>
            <p style="font-size: 16px; color: #333;">
             Vous avez reçu une nouvelle <strong>candidature</strong> à l'une de vos offres d’emploi publiées sur <strong>RecruNova</strong>.<br><br>
            Nous vous invitons à consulter les détails de cette candidature en vous connectant à votre espace employeur.
            </p>


            <hr style="margin: 30px 0;">

            <p >
                Merci de faire partie de RecruNova. Nous vous souhaitons une expérience réussie et pleine de succès !<br>
                <strong>– L’équipe RecruNova</strong>
            </p>
            </div>
        </body>
        </html>
        """
        part=MIMEText(html,"html")
        message.attach(part)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
                return("Email envoyé avec succès !")
        except Exception as e:
                return(" Échec de l'envoi :", e)
        

        


