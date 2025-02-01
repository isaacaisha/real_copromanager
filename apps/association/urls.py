# -*- encoding: utf-8 -*- apps/authentication/urls.py
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

#from .views import (
#    assign_syndic_to_residence, remove_syndic_from_residence,
#    remove_user_from_residence, associate_to_residence, associate_to_syndicate,
#    )

urlpatterns = [

    ## URLs for Assign User
    #path('assign-syndic/', assign_syndic_to_residence, name='assign-syndic'),
    #path('associate-to-residence/', associate_to_residence, name='associate-to-residence'),
    #path('associate-to-syndicate/', associate_to_syndicate, name='associate-to-syndicate'),

    ## URLs for Remove User Assignement
    #path('remove-syndic/', remove_syndic_from_residence, name='remove-syndic'),
    #path('residence/<int:residence_id>/remove-user/<str:role>/<int:user_id>/', remove_user_from_residence, name='remove-user-from-residence'),

]
