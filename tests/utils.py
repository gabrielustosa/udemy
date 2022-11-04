def create_factory_in_batch(factory, amount=1, **kwargs):
    return [factory(**kwargs) for _ in range(amount)]
