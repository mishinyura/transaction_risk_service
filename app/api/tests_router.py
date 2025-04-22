from fastapi import APIRouter

test_router = APIRouter(prefix='/test')


@test_router.get('/')
def test():
    return {'message': 'ok'}