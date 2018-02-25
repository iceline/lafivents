# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import TemplateView 


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
