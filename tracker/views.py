from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
import pandas as pd
import io

def compare_excel(request):
    if request.method == 'POST':
        total_students = request.FILES['total_students']
        filled_form = request.FILES['filled_form']
        
        # Read Excel files
        df_total = pd.read_excel(total_students)
        df_filled = pd.read_excel(filled_form)
        
        # Check if 'Student ID' and 'Email' columns exist in both dataframes
        if 'Student ID' not in df_total.columns or 'Student ID' not in df_filled.columns:
            return HttpResponse("Error: 'Student ID' column not found in one or both Excel files. Please make sure both files have a 'Student ID' column.", status=400)
        
        if 'Email' not in df_total.columns:
            return HttpResponse("Error: 'Email' column not found in the total students Excel file.", status=400)
        
        # Compare and find students who didn't fill the form
        df_not_filled = df_total[~df_total['Student ID'].isin(df_filled['Student ID'])]
        
        # Send email to students who haven't filled the form
        for index, row in df_not_filled.iterrows():
            student_email = row['Email']
            send_mail(
                'Reminder: Form Not Filled',
                'Dear Student, you have not filled out the required form. Please do so at your earliest convenience.',
                'aman2004agrawal@gmail.com',  # Replace with your email address
                [student_email],
                fail_silently=False,
            )
        
        # Generate output Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_not_filled.to_excel(writer, index=False)
        output.seek(0)
        
        # Create response
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=students_not_filled.xlsx'
        
        return response
    
    return render(request, 'tracker/upload.html')
