from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):
    template_name = 'color_widget/coloradio.html'
    option_template_name = 'color_widget/coloradio_option.html'
