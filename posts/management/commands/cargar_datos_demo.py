from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from posts.models import Post

POSTS_DEMO = [
    {
        "titulo": "Por qué empecé a programar en Python",
        "subtitulo": "De la gestión comercial a los datos",
        "estado": "publicado",
        "contenido": (
            "Después de más de quince años en gestión comercial y administración, "
            "me di cuenta de que gran parte de mi trabajo era repetir cálculos y "
            "controles a mano.\n\n"
            "Python me permitió automatizar esas tareas: leer planillas, limpiar datos, "
            "calcular y generar reportes. En este blog voy a contar lo que aprendo, "
            "con ejemplos reales y sin tecnicismos innecesarios."
        ),
    },
    {
        "titulo": "Mi primer proyecto de Data Science con datos sintéticos",
        "subtitulo": "Clasificación y clustering paso a paso",
        "estado": "publicado",
        "contenido": (
            "Para el trabajo final de Data Science construí un dataset sintético, "
            "porque los datos reales de un estudio previsional son confidenciales.\n\n"
            "El flujo fue: limpieza, separar entrenamiento y prueba antes de calcular "
            "estadísticas, comparar modelos con validación cruzada y explicar los "
            "resultados. Lo más importante que aprendí: evitar la fuga de información "
            "(data leakage) es más valioso que probar un modelo más complejo."
        ),
    },
    {
        "titulo": "Drones en el agro: qué se puede medir desde el aire",
        "subtitulo": "Servicios de relevamiento y aplicación",
        "estado": "publicado",
        "contenido": (
            "Un dron permite recorrer un lote en minutos y obtener imágenes que "
            "muestran diferencias de vigor, fallas de siembra o zonas con problemas.\n\n"
            "Combinar esas imágenes con análisis de datos abre la puerta a decisiones "
            "más precisas: dónde aplicar, cuánto y cuándo."
        ),
    },
    {
        "titulo": "Checklist para inspeccionar una propiedad",
        "subtitulo": "Lo que revisar antes de alquilar o vender",
        "estado": "publicado",
        "contenido": (
            "Una inspección ordenada evita sorpresas: instalación eléctrica, humedad, "
            "estado de techos y aberturas, cañerías y seguridad.\n\n"
            "Registrar todo con fotos y un informe simple ayuda tanto a inmobiliarias "
            "como a propietarios e inquilinos."
        ),
    },
    {
        "titulo": "Ideas para el próximo post (borrador)",
        "subtitulo": "Este post no es público",
        "estado": "borrador",
        "contenido": (
            "Temas pendientes: automatizar reportes con Python, un tablero en Power BI "
            "y cómo versionar proyectos con Git y GitHub."
        ),
    },
]


class Command(BaseCommand):
    help = "Crea posts de ejemplo (idempotente) para probar el blog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--usuario",
            help="Nombre de usuario existente que será autor de los posts. "
            "Si se omite se usa el primer superusuario.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        if options["usuario"]:
            try:
                autor = User.objects.get(username=options["usuario"])
            except User.DoesNotExist:
                self.stderr.write(f"No existe el usuario '{options['usuario']}'.")
                return
        else:
            autor = User.objects.filter(is_superuser=True).first()
            if autor is None:
                self.stderr.write(
                    "No hay superusuarios. Creá uno con: python manage.py createsuperuser"
                )
                return

        creados = 0
        for datos in POSTS_DEMO:
            if not Post.objects.filter(titulo=datos["titulo"]).exists():
                Post.objects.create(autor=autor, **datos)
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"Posts de ejemplo creados: {creados}"))
