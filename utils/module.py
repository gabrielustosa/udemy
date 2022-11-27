def get_class_from_module(module_name, class_name):
    module = __import__(module_name, globals(), locals(), class_name)
    return vars(module).get(class_name)
