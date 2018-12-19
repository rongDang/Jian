# -*- encoding:utf8 -*-
from django import forms
from mdeditor.fields import MDTextFormField


class ArticleForm(forms.Form):
    title = forms.CharField(max_length=100,)
    content = MDTextFormField()
