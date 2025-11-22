from django.urls import resolve

match = resolve('/accounts/logout/')
print('view_name:', match.view_name)
print('func:', match.func)
print('args:', match.args)
print('kwargs:', match.kwargs)
try:
    print('module:', match.func.__module__)
    print('name:', match.func.__name__)
except Exception as e:
    print('func info error:', e)

