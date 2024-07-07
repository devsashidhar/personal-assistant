from twilio.rest import Client

account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

def send_sms_reminder(to, body):
    message = client.messages.create(
        body=body,
        from_='+1234567890',  # Replace with your Twilio number
        to=to
    )
    print(f"Message sent: {message.sid}")
    return message.sid
