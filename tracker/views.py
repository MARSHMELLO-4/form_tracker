import base64
import io
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
import pywhatkit as kit
import datetime
# Helper function to find the column that contains "Enrollment"
def find_enrollment_column(df):
    for col in df.columns:
        # Convert the column name to a string before checking
        if "Enrollment" in str(col):  # Case-insensitive check
            return col
    return None

# Helper function to read the file from session
def read_excel_from_session(session, file_key, skip_rows=None):
    excel_file_base64 = session.get(file_key)
    if excel_file_base64:
        excel_file_content = base64.b64decode(excel_file_base64)
        excel_file = io.BytesIO(excel_file_content)
        
        # If skip_rows is provided, use it to skip rows while reading the Excel file
        if skip_rows is not None:
            return pd.read_excel(excel_file, skiprows=skip_rows)
        else:
            return pd.read_excel(excel_file)
    return None



def send_whatsapp_message(Mobile_no, message):
    # Format the Mobile number
    if not Mobile_no.startswith('+91'):
        Mobile_no = f'+91{Mobile_no}'

    # Calculate the current time for sending the message
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute + 2  # Send message 2 minutes later

    # Send the WhatsApp message using pywhatkit
    try:
        kit.sendwhatmsg(Mobile_no, message, hour, minute, 20, tab_close=True)
        print(f"WhatsApp message scheduled to be sent to {Mobile_no}")
    except Exception as e:
        print(f"Failed to send WhatsApp to {Mobile_no}: {e}")


import base64
import io
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
import pywhatkit as kit
import datetime

# Helper function to find the column that contains "Enrollment"
def find_enrollment_column(df):
    for col in df.columns:
        # Convert the column name to a string before checking
        if "Enrollment" in str(col):  # Case-insensitive check
            return col
    return None

# Helper function to read the file from session
def read_excel_from_session(session, file_key, skip_rows=None):
    excel_file_base64 = session.get(file_key)
    if excel_file_base64:
        excel_file_content = base64.b64decode(excel_file_base64)
        excel_file = io.BytesIO(excel_file_content)
        
        # If skip_rows is provided, use it to skip rows while reading the Excel file
        if skip_rows is not None:
            return pd.read_excel(excel_file, skiprows=skip_rows)
        else:
            return pd.read_excel(excel_file)
    return None

def send_whatsapp_message(Mobile_no, message):
    # Format the Mobile number
    if not Mobile_no.startswith('+91'):
        Mobile_no = f'+91{Mobile_no}'

    # Calculate the current time for sending the message
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute + 2  # Send message 2 minutes later

    # Send the WhatsApp message using pywhatkit
    try:
        kit.sendwhatmsg(Mobile_no, message, hour, minute, 20, tab_close=True)
        print(f"WhatsApp message scheduled to be sent to {Mobile_no}")
    except Exception as e:
        print(f"Failed to send WhatsApp to {Mobile_no}: {e}")

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
        df_total = read_excel_from_session(request.session, 'total_students', skip_rows=8)  # Read from 9th row
        df_filled = read_excel_from_session(request.session, 'filled_form')  # Read from the start

        if df_total is None or df_filled is None:
            return HttpResponse("Error: Please upload the Excel files before proceeding.", status=400)

        enrollment_col_total = find_enrollment_column(df_total)
        enrollment_col_filled = find_enrollment_column(df_filled)

        # Error handling for missing columns
        if not enrollment_col_filled or 'Name' not in df_filled.columns:
            return HttpResponse(f"Error: 'Enrollment' or 'Name' column not found in the filled form Excel file.", status=400)
        
        if not enrollment_col_total or 'Name' not in df_total.columns:
            return HttpResponse(f"Error: 'Enrollment' or 'Name' column not found in the total students Excel file.", status=400)

        # Clean the enrollment columns in both dataframes and convert to lowercase for case-insensitive comparison
        df_total[enrollment_col_total] = df_total[enrollment_col_total].astype(str).str.strip().str.lower()
        df_filled[enrollment_col_filled] = df_filled[enrollment_col_filled].astype(str).str.strip().str.lower()

        # Identify students who haven't filled the form
        df_not_filled = df_total[~df_total[enrollment_col_total].isin(df_filled[enrollment_col_filled])]

        if 'compare_excel' in request.POST:
            # Generate the Excel file with only the relevant columns
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_not_filled.to_excel(writer, index=False, columns=['Name', enrollment_col_total])
            output.seek(0)

            # Return Excel file for download
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=students_not_filled.xlsx'
            return response

        if 'send_email' in request.POST:
            if 'Email' not in df_total.columns:
                return HttpResponse("Error: 'Email' column not found in the total students Excel file.", status=400)
            # Send email to students who haven't filled the form
            for index, row in df_not_filled.iterrows():
                student_email = row['Email']
                if student_email:
                    send_mail(
                        'Reminder: Form Not Filled',
                        f"Dear {row['Name']}, you have not filled the form that was circulated. Please fill it ASAP.",
                        'your_email@gmail.com',
                        [student_email],
                        fail_silently=False,
                    )

        if 'send_whatsapp' in request.POST:
            if 'Phone no.' not in df_total.columns:
                return HttpResponse("Error: 'Phone no.' column not found in the total students Excel file.", status=400)
            # Send WhatsApp messages to students who haven't filled the form
            for index, row in df_not_filled.iterrows():
                phone_no = str(row['Phone no.'])
                if phone_no:
                    send_whatsapp_message(phone_no, f"Dear {row['Name']}, you haven't filled the form that was circulated. Please fill it as soon as possible.")
    
    # Pass the file names to the template
    context = {
        'total_students_name': request.session.get('total_students_name'),
        'filled_form_name': request.session.get('filled_form_name'),
    }
    return render(request, 'tracker/upload.html', context)




