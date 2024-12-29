
# ...existing code (if any)...

def user_type_context(request):
    if request.user.is_authenticated:
        return {
            'is_doctor': request.user.groups.filter(name='Doctor').exists(),
            'is_patient': request.user.groups.filter(name='Patient').exists(),
        }
    return {}