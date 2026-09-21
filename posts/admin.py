from django.contrib import admin

from .models import Post

admin.site.site_header = "Administración del Blog"
admin.site.site_title = "Blog de Dante"
admin.site.index_title = "Gestión de contenido"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "estado", "fecha_creacion")
    list_editable = ("estado",)
    list_filter = ("estado", "fecha_creacion", "autor")
    search_fields = ("titulo", "subtitulo", "contenido", "autor__username")
    prepopulated_fields = {"slug": ("titulo",)}
    date_hierarchy = "fecha_creacion"
