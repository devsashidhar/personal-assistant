from flask import Flask, request, jsonify
from google_calendar import authenticate_google_calendar, create_event
from twilio_sms import send_sms_reminder

app = Flask(__name__)

# Authenticate Google Calendar service
calendar_service = authenticate_google_calendar()

@app.route('/api/schedule', methods=['POST'])
def schedule_event():
    data = request.json
    summary = data['summary']
    start_time = data['start_time']
    end_time = data['end_time']
    event = create_event(calendar_service, summary, start_time, end_time)
    return jsonify({"response": f"Event created: {event.get('htmlLink')}"})

@app.route('/api/reminder', methods=['POST'])
def send_reminder():
    data = request.json
    phone_number = data['phone_number']
    message = data['message']
    message_sid = send_sms_reminder(phone_number, message)
    return jsonify({"response": f"Message sent: {message_sid}"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
