# Email Configuration Guide for SkyLearn

## Current Status
✅ **Email system is working!** Emails are being saved to the `sent_emails` folder.

## How to View Student Emails

### Option 1: Check the `sent_emails` folder
- Navigate to: `E:\Projects\SkyLearn-main\sent_emails\`
- Every email sent to students will be saved as a `.log` file
- Open these files to see the complete email content with student credentials

### Option 2: Use Admin Credential Display (Recommended)
- When you add a new student, you'll be redirected to a page showing their credentials
- You can copy the credentials and share them with students manually
- Use the "Reset Password" option from the student list to generate new credentials anytime

## Email Configuration Options

### For Development (Current Setup)
```python
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "sent_emails"
```

### For Production (Gmail SMTP)
1. Create a `.env` file in your project root:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=SkyLearn <your-email@gmail.com>
```

2. Enable 2-factor authentication on your Gmail account
3. Generate an "App Password" for Django
4. Use the app password in EMAIL_HOST_PASSWORD

### For Production (Other Providers)
- **Outlook/Hotmail**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Use your hosting provider's SMTP settings

## Testing Email
Run this command to test email functionality:
```bash
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Test message', 'noreply@skylearn.com', ['test@example.com'])"
```

## Troubleshooting
1. **No emails in sent_emails folder**: Check Django logs for errors
2. **SMTP errors**: Verify email credentials and 2FA settings
3. **Students not receiving emails**: Check spam folders, verify email addresses

## Current Solution
✅ **You can always access student credentials through the admin interface!**
- Add student → View credentials page
- Student list → Reset Password → View new credentials
- All credentials are displayed securely with copy functionality
