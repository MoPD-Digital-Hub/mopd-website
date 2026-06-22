from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.page, {'page_id': 'about'}, name='about'),
    path('contact/', views.page, {'page_id': 'contact'}, name='contact'),
    path('leadership/', views.page, {'page_id': 'leadership'}, name='leadership'),
    path('leadership/<slug:slug>/', views.leader_detail, name='leader_detail'),
    path('gallery/', views.page, {'page_id': 'gallery'}, name='gallery'),
    path('press-release/', views.page, {'page_id': 'press-release'}, name='press'),
    path('climate/', views.page, {'page_id': 'about-climate'}, name='climate'),
    path('climate/documents/', views.page, {'page_id': 'climate-documents'}, name='climate_docs'),
    path('green-technology/', views.page, {'page_id': 'green-technology'}, name='green_tech'),
    path('statistics-documents/', views.page, {'page_id': 'statistics-documents'}, name='stats'),
    path('development-planning/', views.page, {'page_id': 'development-planning'}, name='devplan'),
    path('news/', views.news_list, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    # Legacy leader URLs
    path('leader-1.html', RedirectView.as_view(pattern_name='leader_detail', permanent=False), kwargs={'slug': 'fitsum-assefa'}),
    path('leader-2.html', RedirectView.as_view(pattern_name='leader_detail', permanent=False), kwargs={'slug': 'bereket-fesehatsion'}),
    path('leader-3.html', RedirectView.as_view(pattern_name='leader_detail', permanent=False), kwargs={'slug': 'seyum-mekonen'}),
    path('leader-4.html', RedirectView.as_view(pattern_name='leader_detail', permanent=False), kwargs={'slug': 'tirumar-abate'}),
    # Legacy .html URLs
    path('index.html', RedirectView.as_view(pattern_name='home', permanent=False)),
    path('about.html', RedirectView.as_view(pattern_name='about', permanent=False)),
    path('contact.html', RedirectView.as_view(pattern_name='contact', permanent=False)),
    path('news.html', RedirectView.as_view(pattern_name='news', permanent=False)),
    path('leadership.html', RedirectView.as_view(pattern_name='leadership', permanent=False)),
    path('gallery.html', RedirectView.as_view(pattern_name='gallery', permanent=False)),
    path('press-release.html', RedirectView.as_view(pattern_name='press', permanent=False)),
    path('about-climate.html', RedirectView.as_view(pattern_name='climate', permanent=False)),
    path('climate-documents.html', RedirectView.as_view(pattern_name='climate_docs', permanent=False)),
    path('green-technology.html', RedirectView.as_view(pattern_name='green_tech', permanent=False)),
    path('statistics-documents.html', RedirectView.as_view(pattern_name='stats', permanent=False)),
    path('development-planning.html', RedirectView.as_view(pattern_name='devplan', permanent=False)),
    path('news-un-guterres.html', RedirectView.as_view(url='/news/un-guterres/', permanent=False)),
    path('news-acs2.html', RedirectView.as_view(url='/news/acs2/', permanent=False)),
    path('news-state-minister-acs2.html', RedirectView.as_view(url='/news/state-minister-acs2/', permanent=False)),
    path('news-france-acs2.html', RedirectView.as_view(url='/news/france-acs2/', permanent=False)),
    path('news-donors-green.html', RedirectView.as_view(url='/news/donors-green/', permanent=False)),
    path('news-aprm-session.html', RedirectView.as_view(url='/news/aprm-session/', permanent=False)),
    path('news-procurement.html', RedirectView.as_view(url='/news/procurement/', permanent=False)),
    path('news-finance-cop28.html', RedirectView.as_view(url='/news/finance-cop28/', permanent=False)),
]
