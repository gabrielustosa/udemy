class AnnotationBase:

    @classmethod
    def get_annotations(cls, *fields, related_field=''):
        annotations = {}
        if '*' in fields:
            fields = getattr(cls, 'annotations_fields')
        for field in fields:
            annotations.update(getattr(cls.annotation_class, f'get_{field}')(related_field=related_field))
        return annotations
