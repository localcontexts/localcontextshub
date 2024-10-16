from django import template
from django.urls import reverse
from django.templatetags.static import static
import os

register = template.Library()


@register.simple_tag
def get_bclabel_img_url(img_type, *args, **kwargs):
    # Returns image url, usage: <img loading="lazy" src="{% get_bclabel_img_url img_type %}">
    if img_type == 'bcr':
        image_path = 'images/bc-labels/bc-research-use.png'
    elif img_type =='bccv':
        image_path = 'images/bc-labels/bc-consent-verified.png'
    elif img_type =='bccb':
        image_path = 'images/bc-labels/bc-open-to-collaboration.png'
    elif img_type =='bcoc':
        image_path = 'images/bc-labels/bc-open-to-commercialization.png'
    elif img_type =='bcp':
        image_path = 'images/bc-labels/bc-provenance.png'
    elif img_type =='bcmc':
        image_path = 'images/bc-labels/bc-multiple-community.png'

    elif img_type =='bccl':
        image_path = 'images/bc-labels/bc-clan.png'
    elif img_type =='bco':
        image_path = 'images/bc-labels/bc-outreach.png'
    elif img_type =='bccnv':
        image_path = 'images/bc-labels/bc-consent-non-verified.png'
    elif img_type =='bcnc':
        image_path = 'images/bc-labels/bc-non-commercial.png'

    return static(image_path)

@register.simple_tag
def get_tklabel_img_url(img_type, *args, **kwargs):
    # Returns image url, usage: <img loading="lazy" src="{% get_tklabel_img_url img_type %}">
    if img_type == 'tka':
        image_path = 'images/tk-labels/tk-attribution.png'
    elif img_type =='tkcl':
        image_path = 'images/tk-labels/tk-clan.png'
    elif img_type =='tkf':
        image_path = 'images/tk-labels/tk-family.png'
    elif img_type =='tkmc':
        image_path = 'images/tk-labels/tk-multiple-community.png'
    elif img_type =='tkcv':
        image_path = 'images/tk-labels/tk-community-voice.png'

    elif img_type =='tks':
        image_path = 'images/tk-labels/tk-seasonal.png'
    elif img_type =='tkwg':
        image_path = 'images/tk-labels/tk-women-general.png'
    elif img_type =='tkmg':
        image_path = 'images/tk-labels/tk-men-general.png'
    elif img_type =='tkmr':
        image_path = 'images/tk-labels/tk-men-restricted.png'
    elif img_type =='tkwr':
        image_path = 'images/tk-labels/tk-women-restricted.png'
    elif img_type =='tkcs':
        image_path = 'images/tk-labels/tk-culturally-sensitive.png'
    elif img_type =='tkss':
        image_path = 'images/tk-labels/tk-secret-sacred.png'

    elif img_type =='tkv':
        image_path = 'images/tk-labels/tk-verified.png'
    elif img_type =='tknv':
        image_path = 'images/tk-labels/tk-non-verified.png'
    elif img_type =='tkoc':
        image_path = 'images/tk-labels/tk-commercial.png'
    elif img_type =='tknc':
        image_path = 'images/tk-labels/tk-non-commercial.png'
    elif img_type =='tkco':
        image_path = 'images/tk-labels/tk-community-use-only.png'
    elif img_type =='tko':
        image_path = 'images/tk-labels/tk-outreach.png'
    elif img_type =='tkcb':
        image_path = 'images/tk-labels/tk-open-to-collaboration.png'
    elif img_type =='tkcr':
        image_path = 'images/tk-labels/tk-creative.png'
    return static(image_path)

@register.simple_tag
def can_user_approve_label(user, label, member_role):
    user_can_approve = True

    if member_role == 'viewer':
        user_can_approve = False
    else:
        if label.created_by == user:
            # If the user is the creator of the label
            if not label.last_edited_by:
                # If there is no last editor, the creator cannot approve
                user_can_approve = False
            elif label.last_edited_by == user:
                # If the last editor is also the creator, neither can approve
                user_can_approve = False
        else:
            # If the user is not the creator
            if label.last_edited_by == user:
                # If the user is the last editor, they cannot approve
                user_can_approve = False

    return user_can_approve

@register.filter
def get_filename(string):
    return os.path.basename(string)
