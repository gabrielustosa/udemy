def create_factory_in_batch(factory, amount=1, reverse=False, **kwargs):
    batch = [factory(**kwargs) for _ in range(amount)]
    return reversed(batch) if reverse else batch
