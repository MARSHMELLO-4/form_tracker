# Form Tracker Website

## Description

The Form Tracker website is a tool designed for colleges to manage student form submissions. It allows users to upload an Excel file containing information about students and their form submission status. The website processes the file to identify students who have not yet filled out the Google form and provides a downloadable Excel file with this information. Additionally, it sends reminder emails to the students who haven't completed the form.

## Features

- **Upload Excel File**: Users can upload an Excel file with details about students and their form submission status.
- **Generate Report**: The website processes the file and generates a new Excel file listing students who haven’t filled out the form yet.
- **Send Emails**: Automated emails are sent to students who need to complete the form, reminding them to do so.
- **User-Friendly Interface**: A simple and intuitive interface for file upload and report generation.

## Requirements

- Python 3.x
- Django 5.x
- Pandas
- openpyxl
- smtplib (for sending emails)

## Usage
Upload the Excel file: Navigate to the file upload page and upload an Excel file with the total number of students and those who have filled out the form.
Generate Report: After uploading, the website will process the data and generate an Excel file listing the students who haven’t filled out the form yet.
Email Notifications: Emails will be sent automatically to the students who need to complete the form.
Configuration
Email Settings: Configure your email settings in settings.py to enable sending emails.
Excel File Format: Ensure the input Excel file follows the required format for accurate processing.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.

