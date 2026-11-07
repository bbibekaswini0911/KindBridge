from django.urls import path

from . import (views_center, views_deals, views_donor, views_offers,
            views_records, views_reports)

urlpatterns = [
    # care centre
    path('needs/new/', views_center.post_need, name='post_need'),
    path('needs/mine/', views_center.my_needs, name='my_needs'),
    path('needs/<int:pk>/close/', views_center.close_need, name='close_need'),
    path('centre/profile/', views_center.center_profile, name='center_profile'),

    # needs market (donors)
    path('needs/', views_donor.need_board, name='need_board'),
    path('needs/<int:pk>/', views_donor.need_detail, name='need_detail'),
    path('needs/<int:pk>/take/', views_donor.take_need, name='take_need'),

    # donor items
    path('offers/', views_offers.offer_board, name='offer_board'),
    path('offers/new/', views_offers.publish_offer, name='publish_offer'),
    path('offers/mine/', views_offers.my_offers, name='my_offers'),
    path('offers/<int:pk>/', views_offers.offer_detail, name='offer_detail'),
    path('offers/<int:pk>/claim/', views_offers.claim_offer, name='claim_offer'),
    path('offers/<int:pk>/close/', views_offers.offer_close, name='offer_close'),
    path('claims/<int:pk>/accept/', views_offers.claim_accept, name='claim_accept'),
    path('claims/<int:pk>/decline/', views_offers.claim_decline, name='claim_decline'),

    # deal page (pledges and claims)
    path('deal/<str:kind>/<int:pk>/', views_deals.deal_detail, name='deal_detail'),
    path('deal/<str:kind>/<int:pk>/complete/', views_deals.deal_complete, name='deal_complete'),
    path('deal/<str:kind>/<int:pk>/cancel/', views_deals.deal_cancel, name='deal_cancel'),

    # records and reports
    path('records/', views_records.records, name='records'),
    path('records/export/', views_reports.export_csv, name='export_csv'),
    path('certificate/<str:kind>/<int:pk>/', views_reports.certificate, name='certificate'),

    # landing page contact form and the admin inbox
    path('contact/', views_reports.contact_submit, name='contact_submit'),
    path('messages/', views_reports.admin_messages, name='admin_messages'),
    path('messages/<int:pk>/read/', views_reports.message_read, name='message_read'),
]
