from django.conf.urls import url
from . import views
import rest_framework.documentation as drf_doc
from rest_framework_simplejwt import views as jwt_views

app_name = 'apis'

urlpatterns = [
    url(r'^apis/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^apis/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^apis/hello/', views.HelloView.as_view(), name='hello'),
    url(r'', drf_doc.include_docs_urls(title='Victorius API')),
    url(r'^apis/lista/$', views.VictoriusApi.as_view()),
    url(r'^apis/actividades-todas/$', views.ActividadesTodasView.as_view()),
    url(r'^apis/actividades-atleta/$', views.ActividadesAfiliacionView.as_view()),
    url(r'^apis/detalle-actividad/(?P<id>[\w\-]+)', views.DetalleActividadView.as_view()),
    url(r'^apis/reservar/$',views.Reservar.as_view()),
    url(r'^apis/cancelar/$', views.Cancelar.as_view()),
    url(r'^apis/reservas/(?P<pk>[\w\-]+)', views.ActividadesReservadasView.as_view(), name="actividades_reservadas"),
    url(r'^apis/esperas/(?P<pk>[\w\-]+)', views.ActividadesEnEsperaView.as_view(), name="actividades_en_espera"),
    url(r'^apis/profiles/$', views.ProfilesApiView.as_view()),
    url(r'^apis/profiles/(?P<pk>[\w\-]+)', views.ProfileDetailApiView.as_view(), name="profile_detail"),
    url(r'^apis/centros/$', views.CentrosPublicosView.as_view()),
    url(r'^apis/centros/(?P<pk>[\w\-]+)', views.CentrosAfiliacionView.as_view(), name="centros_afiliacion"),
    url(r'^apis/localidades/$', views.LocalidadesView.as_view()),
    url(r'^apis/localidades/(?P<pk>[\w\-]+)', views.LocalidadesAfiliacionView.as_view(), name="localidades_afiliacion"),
    url(r'^apis/planes-atleta/(?P<pk>[\w\-]+)', views.PlanesAtletaView.as_view(), name="planes_atleta"),
    url(r'^apis/productos-actividad/(?P<pk>[\w\-]+)', views.ProductosActividadView.as_view(), name="productos_actividad"),
    url(r'^apis/docs/', drf_doc.include_docs_urls(title='Victorius API')),
    url(r'^apis/pin-notificaciones-atleta/$', views.PinNotificacionesAtletaView.as_view(), name="pin-notificaciones-atleta"),
    url(r'^apis/notificaciones-pendientes-atleta/$', views.NotificacionesPendientesAtletaView.as_view(), name="notificaciones-pendientes-atleta"),
    url(r'^apis/notificaciones-recientes-atleta/$', views.NotificacionesRecientesAtletaView.as_view(), name="notificaciones-recientes-atleta"),
    url(r'^apis/accion-notificacion-atleta/$', views.AccionNotificacionAtletaView.as_view(), name="accion-notificacion-atleta"),

]