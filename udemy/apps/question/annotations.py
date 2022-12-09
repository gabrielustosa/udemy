from django.db.models import Count, Q


class QuestionAnnotations:
    @staticmethod
    def get_likes_count(related_field=''):
        return {'_likes_count': Count(f'{related_field}actions__id', filter=Q(**{f'{related_field}actions__action': 1}))}

    @staticmethod
    def get_dislikes_count(related_field=''):
        return {'_dislikes_count': Count(f'{related_field}actions__id', filter=Q(**{f'{related_field}actions__action': 2}))}
