def set_notice_defaults(notice):
    bc_text = 'The BC (Biocultural) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material or data. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information (DSI) generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC Labels are in development and their implementation is being negotiated.'
    tk_text = 'The TK (Traditional Knowledge) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.'
    bc_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/bc-notice.png'
    tk_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/tk-notice.png'
    
    if notice.notice_type == 'biocultural':
        notice.bc_img_url = bc_url
        notice.bc_default_text = bc_text
    if notice.notice_type == 'traditional_knowledge':
        notice.tk_img_url = tk_url
        notice.tk_default_text = tk_text
    if notice.notice_type == 'biocultural_and_traditional_knowledge':
        notice.bc_img_url = bc_url
        notice.bc_default_text = bc_text
        notice.tk_img_url = tk_url
        notice.tk_default_text = tk_text

    notice.save()  

def dev_prod_or_local(hostname):
    if 'anth-ja77-lc-dev-42d5' in hostname:
        return 'DEV'
    elif 'localcontextshub' in hostname:
        return 'PROD'
    elif 'anth-ja77-local-contexts-8985' in hostname:
        return 'AE_PROD' 