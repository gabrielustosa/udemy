from django.db.models import Count, Avg, Q, Sum


class CourseAnnotations:
    @staticmethod
    def get_num_modules():
        return {'_num_modules': Count('modules')}

    @staticmethod
    def get_num_lessons():
        return {'_num_lessons': Count('lessons')}

    @staticmethod
    def get_num_contents():
        return {'_num_contents': Count('contents')}

    @staticmethod
    def get_avg_rating():
        return {'_avg_rating': Avg('ratings__rating')}

    @staticmethod
    def get_num_subscribers():
        return {'_num_subscribers': Count('students')}

    @staticmethod
    def get_num_contents_info():
        return {f'_content_num_{option}': Count('contents__id', filter=Q(contents__content_type__model=option))
                for option in ['text', 'link', 'file', 'image']}

    @staticmethod
    def get_estimated_content_length_video():
        return {'_estimated_content_length_video': Sum('lessons__video_duration')}
