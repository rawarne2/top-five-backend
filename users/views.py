from django.http import JsonResponse
from utils import get_db_handle


def index(request):
    database = get_db_handle('topfive_db')
    users_collection = database['users_userprofile']
    first_names = users_collection.find().distinct('first_name')

    # returns a list of every user's first name in the database
    return JsonResponse(first_names, safe=False)
