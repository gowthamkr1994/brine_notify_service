import requests
import json
import mysql.connector
from mysql.connector import Error
from constants import CURRENCIES, BITCOIN, ID, CURRENT_PRICE, CRYPTO_CURRENCY_URL, LAST_UPDATED, MAIL_BODY
from query import ALERT_QUERY, UPDATE_ALERT_STATUS
import time
from email.message import EmailMessage
import ssl
import smtplib
import redis
import json

class BrineDatabase:
    connection = mysql.connector.connect(host="127.0.0.1", user="root", password="root", database="brine")


class Redis:
    redisClient = redis.StrictRedis(host='localhost', port=6379, db=0)

    @classmethod
    def get_data(cls, key): 
        alerts_data = json.loads(Redis.redisClient.get(key))
        return alerts_data
      

class Crypto:
    @classmethod
    def send_email(cls, email_receiver, mail_body):
        try:
            email_sender = "gowtham.kolekar123@gmail.com"
            email_password = "ekiv cbgm cxuq hrak"
            subject = "Bitcoin Price Alert Notification"
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['subject'] = subject
            em.set_content(mail_body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string() )
                print("mail sent successfully")
        
        except Exception as e:
            print("Error while sending mail")        
                

    @classmethod
    def filter_bitcoin_currency(cls, currency):
        if currency.get(ID, None) == BITCOIN:
            return True
        else:
            return False
    

    @classmethod
    def get_bitcoin_price(cls,):
        try:
            response = requests.get(CRYPTO_CURRENCY_URL)
            currencies = json.loads(response.text)
            currencies = filter(cls.filter_bitcoin_currency, currencies)
            
            for currency in currencies:
                price = currency.get(CURRENT_PRICE)
                time = currency.get(LAST_UPDATED)
                bitcoin_details = { CURRENT_PRICE: price, LAST_UPDATED: time }
                return bitcoin_details

        except Exception as e:
            print("Error while fetching crypto currency details: ", e)
            bitcoin_details = {CURRENT_PRICE: 26466, LAST_UPDATED: "2023-05-26 03:30:30" }
            return bitcoin_details



    @classmethod
    def get_email_str(cls, emails):
        email_str = "("
    
        for index, email in enumerate(emails):
            email_str += "'" + email + "'," if index < len(emails)-1 else  "'" + email + "'"
        email_str += ")"
        return email_str
    


    @classmethod
    def update_alert_status(cls, emails, price):
        try:
            update_alert_params = dict()
            update_alert_params["username"] = Crypto.get_email_str(emails)
            update_alert_params["price"] = price
            
            connection = BrineDatabase.connection
            if connection.is_connected():
                cursor = connection.cursor()
                update_alert_query = UPDATE_ALERT_STATUS.format(**update_alert_params)
                cursor.execute(update_alert_query)
                
        except Error as e:
            print("Errorupdate_aleret_status", e)
                

    @classmethod
    def notify_users(cls):
        try:
            mail_params = dict()
            bitcoin_details = Crypto.get_bitcoin_price()
            current_price = str(bitcoin_details.get(CURRENT_PRICE, None))
            # print(current_price)
            users_list = []
            if bitcoin_details == None:
                raise Exception("Error while getching price")
            alerts = Redis.get_data("alerts")
        
            if alerts.get(current_price, False):
                user_keys = alerts.get(current_price)
                for user_key in user_keys:
                    username = user_key.split("~")[0]
                    users_list.append(username)
                    mail_params['price'] = current_price
                    mail_body = MAIL_BODY.format(**mail_params)
                    Crypto.send_email(users_list, mail_body)
                
                Crypto.update_alert_status(users_list, current_price) 
                
        except Error as e:
            print("error in notify user",e)
        

if __name__ == "__main__":
    while(True):
        bitcoint_price = Crypto.notify_users()
        time.sleep(30)


# with open('crypto_data.json') as user_file:
#     file_contents = user_file.read()
#     data = json.loads(file_contents)
#     currencies = data.get(CURRENCIES, None)
#     currency = filter(get_bitcoin_price, currencies)
#     for bit_curency in currency:
#         price = bit_curency.get(CURRENT_PRICE)
#         print(price)

# bitcoin_details.get(CURRENT_PRICE,26466)
            # data_elements = {CURRENT_PRICE: bitcoin_details.get(CURRENT_PRICE, None)}
            # mail_params["time"] = bitcoin_details[LAST_UPDATED][0:19]
            
            # connection = BrineDatabase.connection
            # alert_ids = list()
            # if connection.is_connected():
            #     cursor = connection.cursor()
            #     alert_query = ALERT_QUERY.format(**data_elements)
            #     cursor.execute(alert_query)
            #     alerts = cursor.fetchall()
            #     print(alerts)
            #     for alert in alerts:
            #         mail_params['id'] = alert[0]
            #         mail_params['username'] = alert[1]
            #         mail_params['email'] = alert[2]
            #         mail_params['price'] = alert[3]
            #         mail_params['status'] = alert[4]
            #         mail_params['first_name'] = alert[5]
                    
            #         mail_body = MAIL_BODY.format(**mail_params)
            #         alert_ids.append(alert[0])
            #         Crypto.send_email( mail_params['email'], mail_body)
                
            #     if alert_ids:
            #         Crypto.update_aleret_status(alert_ids)