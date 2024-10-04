from django import template

register = template.Library()

'''
    List of all icons in use on the site. Function will return selected icon for component.
'''
def get_icon(name):

    icon_type = {
        None: '',
        'labels': 'fa-solid fa-tag',
        'subprojects': 'fa-regular fa-diagram-subtask',
        'archive-projects': 'fa-solid fa-box-archive',

        # Arrows
        'right-arrow': 'fa-solid fa-arrow-right',
        'left-arrow': 'fa fa-arrow-left',
        'down-caret': 'fa-solid fa-angle-down',
        'large-down-caret': 'fa-solid fa-angle-down fa-2xl',
        'left-chevron': 'fa-solid fa-chevron-left',
        'left-chevrons': 'fa-solid fa-chevrons-left',
        'right-chevron': 'fa-solid fa-chevron-right',
        'right-chevrons': 'fa-solid fa-chevrons-right',

        # Action Icons
        'x-close': 'fa-regular fa-xmark fa-xl', # Update to fa-sharp fa-solid fa-xmark?
        'edit': 'fa-solid fa-pen-line',
        'add': 'fa fa-plus',
        'circle-add': 'fa-solid fa-circle-plus',
        'upload': 'fa-solid fa-arrow-up-from-line',
        'download': 'fa-solid fa-arrow-down-to-line',
        'copy': 'fa-regular fa-clone pointer',
        'trash': 'fa-regular fa-trash pointer',
        'search': 'fa-solid fa-magnifying-glass',
        'erase': 'fa-regular fa-eraser',
        'share': 'fa-solid fa-share-nodes',
        'view': 'fa-solid fa-eye',

        # User Icons
        'user': 'fa-light fa-user',
        'circle-user': 'fa-solid fa-circle-user fa-3x',
        'user-group': 'fa-solid fa-user-group',
        'add-user': 'fa fa-user-plus',

        # Link Icons
        'simple-link': 'fa-solid fa-link-simple',
        'break-link': 'fa-solid fa-link-simple-slash',
        'external-link': 'fa-solid fa-arrow-up-right-from-square fa-xs',

        # Social Media Icons
        'twitter': 'fa-brands fa-square-twitter',
        'instagram': 'fa-brands fa-square-instagram',
        'facebook': 'fa fa-facebook-square',
        'youtube': 'fa fa-youtube-square',
        'linkedin': 'fa fa-linkedin-square',
        'vimeo': 'fa-brands fa-square-vimeo',

        # Misc Icons
        'check': 'fa-solid fa-check',
        'circle-check': 'fa-solid fa-circle-check',
        'settings': 'fa fa-cog',
        'envelope': 'fa-solid fa-envelope',
        'key': 'fa fa-key',
        'power-off': 'fa fa-power-off fa-3x',
        'spinner': 'fa spinner-container fa-spinner fa-spin fa-2x spinner',
        'sliders': 'fa-solid fa-sliders',
        'location-marker': 'fa-solid fa-location-dot fa-3x',
        'code': 'fa fa-code fa-3x',
        'website': 'fa-solid fa-globe',
        'documentation': 'fa-solid fa-book',
        'columns': 'fa-regular fa-line-columns',
        'calendar': 'fa-light fa-calendar',
        'exclamation': 'fa fa-circle-exclamation',
        'language': 'fa fa-language fa-2x',
        'object-group': 'fa fa-object-group fa-2x',
        'large-minus': 'fa-solid fa-minus fa-xl',
        'large-plus': 'fa-solid fa-plus fa-xl',
        'address-card': 'fa-solid fa-address-card',
    }

    return icon_type[name]


'''
Button components and options:
    Style = String indicating the button type (primary, secondary, tertiary, ghost).
        Primary set as default.
    Label = Button Text as String
    Href = Link for button as string. If using an internal link, URL must be set first as
        a variable and then the variable passed to `href`. Example:
            {% url 'dashboard' as button_link %}
            {% button style='primary' label='Back to my profile' icon='right-arrow' href=button_link %}
    Icon = Name of Icon as string. (See `get_icon` for icon types)
    Helptext = If helptext is needed for a button, this takes a string that will be the text for
        the help text box.
    Disabled = Boolean if the button should be disabled (True/False). If disabled, `href` will
        not show.
    Rounded = Boolean if the button should be rounded (True/False). If rounded, only the
        icon will show, no label.
    Extra_args = To include extra arguments for buttons as a string. Example:
        extra_args="id='test' name='name-test'"
'''
@register.inclusion_tag(name='button', filename='components/input-components.html')
def buttons(
    style='primary',
    label=None,
    href=None,
    icon=None,
    helptext=None,
    disabled=None,
    rounded=None,
    **extra_args
):

    icon = get_icon(icon)
    if extra_args:
        extra_args = extra_args['extra_args']

    return {
        'style': style,
        'label': label,
        'icon': icon,
        'helptext': helptext,
        'disabled': disabled,
        'href': href,
        'rounded': rounded,
        'component': 'button',
        'extra_args': extra_args
    }
