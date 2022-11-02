from django.apps import apps


def get_model(model_name):
    if model_name in ['text', 'image', 'file', 'link']:
        return apps.get_model(app_label='content', model_name=model_name)
    return None
