import base64
import io
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
import pywhatkit as kit
import datetime

# Helper function to read the file from session
def read_excel_from_session(session, file_key):
    excel_file_base64 = session.get(file_key)
    if excel_file_base64:
        excel_file_content = base64.b64decode(excel_file_base64)
        excel_file = io.BytesIO(excel_file_content)
        return pd.read_excel(excel_file)
    return None

def send_whatsapp_message(phone_no, message):
    # Format the phone number
    if not phone_no.startswith('+91'):
        phone_no = f'+91{phone_no}'

    # Calculate the current time for sending the message
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute + 2  # Send message 2 minutes later

    # Send the WhatsApp message using pywhatkit
    try:
        kit.sendwhatmsg(phone_no, message, hour, minute, 20, tab_close=True)
        print(f"WhatsApp message scheduled to be sent to {phone_no}")
    except Exception as e:
        print(f"Failed to send WhatsApp to {phone_no}: {e}")

def compare_excel(request):
    if request.method == 'POST':
        if 'total_students' in request.FILES and 'filled_form' in request.FILES:
            total_students = request.FILES['total_students']
            filled_form = request.FILES['filled_form']

            # Store the uploaded files in session as base64 strings along with the file names
            request.session['total_students'] = base64.b64encode(total_students.read()).decode('utf-8')
            request.session['filled_form'] = base64.b64encode(filled_form.read()).decode('utf-8')
            request.session['total_students_name'] = total_students.name
            request.session['filled_form_name'] = filled_form.name

        # Read files from session
        df_total = read_excel_from_session(request.session, 'total_students')
        df_filled = read_excel_from_session(request.session, 'filled_form')

        if df_total is None or df_filled is None:
            return HttpResponse("Error: Please upload the Excel files before proceeding.", status=400)

        # Error handling for missing columns
        if 'Student ID' not in df_total.columns or 'Student ID' not in df_filled.columns:
            return HttpResponse("Error: 'Student ID' column not found in one or both Excel files. Please make sure both files have a 'Student ID' column.", status=400)
        
        if 'Email' not in df_total.columns or 'Phone no.' not in df_total.columns:
            return HttpResponse("Error: 'Email' or 'Phone no.' column not found in the total students Excel file.", status=400)

        # Identify students who haven't filled the form
        df_not_filled = df_total[~df_total['Student ID'].isin(df_filled['Student ID'])]

        if 'compare_excel' in request.POST:
            # Generate the Excel file of students who haven't filled the form
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_not_filled.to_excel(writer, index=False)
            output.seek(0)

            # Return Excel file for download
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=students_not_filled.xlsx'
            return response

        if 'send_email' in request.POST:
            # Send email to students who haven't filled the form
            for index, row in df_not_filled.iterrows():
                student_email = row['Email']
                send_mail(
                    'Reminder: Form Not Filled',
                    'Dear Student, you have not filled the form that was circulated. Please fill it ASAP.',
                    'your_email@gmail.com',
                    [student_email],
                    fail_silently=False,
                )

        if 'send_whatsapp' in request.POST:
            # Send WhatsApp messages to students who haven't filled the form
            for index, row in df_not_filled.iterrows():
                phone_no = str(row['Phone no.'])
                send_whatsapp_message(phone_no, "Dear Student, you haven't filled the form that was circulated. Please fill it as soon as possible.")

    # Pass the file names to the template
    context = {
        'total_students_name': request.session.get('total_students_name'),
        'filled_form_name': request.session.get('filled_form_name'),
    }
    return render(request, 'tracker/upload.html', context)
