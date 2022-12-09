from django.db.models import Count, Avg, Q, Sum


class CourseAnnotations:
    @staticmethod
    def get_num_modules(related_field=''):
        return {f'{related_field}_num_modules': Count(f'{related_field}modules')}

    @staticmethod
    def get_num_lessons(related_field=''):
        return {f'{related_field}_num_lessons': Count(f'{related_field}lessons')}

    @staticmethod
    def get_num_contents(related_field=''):
        return {f'{related_field}_num_contents': Count(f'{related_field}contents')}

    @staticmethod
    def get_avg_rating(related_field=''):
        return {f'{related_field}_avg_rating': Avg(f'{related_field}ratings__rating')}

    @staticmethod
    def get_num_subscribers(related_field=''):
        return {f'{related_field}_num_subscribers': Count(f'{related_field}students')}

    @staticmethod
    def get_num_contents_info(related_field=''):
        return {f'{related_field}_num_{option}': Count(f'{related_field}contents__id',
                                                       filter=Q(**{f'{related_field}contents__content_type__model': option}))
                for option in ['text', 'link', 'file', 'image']}

    @staticmethod
    def get_estimated_content_length_video(related_field=''):
        return {f'{related_field}_estimated_content_length_video': Sum(f'{related_field}lessons__video_duration')}
