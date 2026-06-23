from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Session, Semester, NewsAndEvents


class NewsAndEventsAdmin(TranslationAdmin):
    pass


class SemesterAdmin(admin.ModelAdmin):
    list_display = ['semester', 'session', 'is_current_semester', 'next_semester_begins']
    list_filter = ['is_current_semester', 'session', 'semester']
    list_editable = ['is_current_semester']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


class SessionAdmin(admin.ModelAdmin):
    list_display = ['session', 'is_current_session', 'next_session_begins']
    list_filter = ['is_current_session']
    list_editable = ['is_current_session']


admin.site.register(Semester, SemesterAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(NewsAndEvents, NewsAndEventsAdmin)
