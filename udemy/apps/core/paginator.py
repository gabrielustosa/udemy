import re

from collections import OrderedDict
from dataclasses import dataclass
from typing import List

from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.utils.urls import replace_query_param

from django.core.paginator import Paginator, InvalidPage
from django.utils.functional import cached_property
from django.db.models import QuerySet

RELATED_OBJECT_PAGINATED_BY = 100


@dataclass
class PaginatorRelatedObject:
    queryset: QuerySet
    related_object_name: str
    related_object_fields: List[str]
    request: Request

    def paginate_queryset(self):
        page_size = self.get_page_size
        if not page_size:
            page_size = RELATED_OBJECT_PAGINATED_BY

        paginator = Paginator(self.queryset, page_size)
        page_number = self.get_page_number or 1

        self.num_pages = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            raise NotFound(f'Invalid page for `{self.related_object_name}`.')

        return list(self.page)

    @cached_property
    def get_page_number(self):
        for field in self.related_object_fields:
            match = re.search(r'page\(([0-9_]+)\)', field)
            if match:
                return match.group(1)

    @cached_property
    def get_page_size(self):
        for field in self.related_object_fields:
            match = re.search(r'page_size\(([0-9_]+)\)', field)
            if match:
                return match.group(1)

    def get_query_param(self):
        return f'fields[{self.related_object_name}]'

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.get_query_param(), self.replace_page(page_number))

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return replace_query_param(url, self.get_query_param(), self.remove_page())
        return replace_query_param(url, self.get_query_param(), self.replace_page(page_number))

    def replace_page(self, page):
        query_fields = ','.join(self.related_object_fields)
        return query_fields.replace(f'page({self.get_page_number})', f'page({page})')

    def remove_page(self):
        query_fields = [field for field in self.related_object_fields if field != f'page({self.get_page_number})']
        return ','.join(query_fields)

    def get_paginated_data(self, data):
        return OrderedDict([
            ('count', self.queryset.count()),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])
