from django import template

register = template.Library()


def get_icon(name):

    icon_type = {
        None: '',
        'edit': 'fa fa-pencil',
        'right-arrow': 'fa fa-arrow-right',
    }

    return icon_type[name]


@register.inclusion_tag(name='button', filename='components/input-components.html')
def buttons(style='primary', label=None, href='#', icon=None, state=None, rounded=None):

    icon = get_icon(icon)
    print(href)

    return {
        'style': style,
        'label': label,
        'icon': icon,
        'state': state,
        'href': href,
        'rounded': rounded,
        'component': 'button'
    }