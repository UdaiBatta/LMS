## Quiz Progress Troubleshooting Guide

### Testing Quiz Progress Access

To access the Quiz Progress page, use one of these methods:

1. **Via Sidebar Navigation:**

   - Login to your account
   - Look for "Quiz Progress Rec" in the sidebar
   - Click on it

2. **Direct URL Access:**

   ```
   http://127.0.0.1:8000/en/quiz/progress/
   ```

3. **Via Quiz Dashboard:**
   - Go to Quiz Dashboard
   - Look for progress/analytics links

### Common Issues and Solutions:

#### 1. **Permission Errors**

- Make sure you're logged in
- Students can see their own progress
- Lecturers can see their students' progress
- Admins can see all progress

#### 2. **URL Not Found (404 Error)**

- Check if the URL pattern is correct in `quiz/urls.py`
- Make sure the quiz app is included in the main `config/urls.py`

#### 3. **Template Errors**

- Check if `quiz/progress.html` exists
- Make sure all required context variables are available

#### 4. **Empty Progress Data**

- If no data shows, you need to:
  - Create some quizzes
  - Have students take the quizzes
  - Complete the quiz attempts

### Quick Test Commands:

You can run these in the Django shell to check data:

```python
# Check if you have quiz data
python manage.py shell

# In the shell:
from quiz.models import Quiz, Sitting, Progress
from accounts.models import User

# Check users
print("Users:", User.objects.count())

# Check quizzes
print("Quizzes:", Quiz.objects.count())

# Check completed quiz attempts
print("Completed attempts:", Sitting.objects.filter(complete=True).count())

# Check progress records
print("Progress records:", Progress.objects.count())
```

### Debug the QuizUserProgressView:

Add this to check what's happening in the view:

```python
# In quiz/views.py, add print statements to debug:
def get_context_data(self, **kwargs):
    print(f"User: {self.request.user}")
    print(f"User authenticated: {self.request.user.is_authenticated}")
    print(f"User role: {getattr(self.request.user, 'get_user_role', lambda: 'Unknown')()}")

    context = super().get_context_data(**kwargs)
    # ... rest of the method
```

Let me know what specific error message you're seeing when trying to access the quiz progress page!
