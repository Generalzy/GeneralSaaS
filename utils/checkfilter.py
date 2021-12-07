from django.utils.safestring import mark_safe


class CheckFilter:
    def __init__(self, choices, request):
        self.choices = choices
        self.request = request

    def __iter__(self):
        for k, v in self.choices:
            status = self.request.GET.get('status')
            if str(k) == status:
                yield mark_safe(f'<label for="" class="cell"><input type="radio" value="{k}" checked=checked '
                                f'name="status">{v}</label>')
            else:
                yield mark_safe(f'<label for="" class="cell"><input type="radio" value="{k}" name="status">{v}</label>')
