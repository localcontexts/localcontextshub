from django.contrib import admin
from .models import *

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'notice_type', 'placed_by_researcher', 'placed_by_institution', 'created', 'archived' )
    search_fields = ('project',)

class InstitutionNoticeAdmin(admin.ModelAdmin):
    list_display = ('project', 'notice_type', 'institution', 'created', 'archived' )
    search_fields = ('project',)

class LabelTranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'language_tag', 'translation', )

class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'sender', 'community', 'message', 'created')
    search_fields = ('project',)

class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project', 'community', 'seen', 'status')
    search_fields = ('project',)

class EntitiesNotifiedAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project',)

class LabelNoteAdmin(admin.ModelAdmin):
    list_display = ('bclabel', 'tklabel', 'sender',)

class ConnectionsAdmin(admin.ModelAdmin):
    list_display = ('community', 'researcher', 'institution')

admin.site.register(Notice, NoticeAdmin)
admin.site.register(InstitutionNotice, InstitutionNoticeAdmin)
admin.site.register(LabelTranslation, LabelTranslationAdmin)
admin.site.register(ProjectComment, ProjectCommentAdmin)
admin.site.register(ProjectStatus, ProjectStatusAdmin)
admin.site.register(EntitiesNotified, EntitiesNotifiedAdmin)
admin.site.register(LabelNote, LabelNoteAdmin)
admin.site.register(Connections, ConnectionsAdmin)

