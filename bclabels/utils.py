def check_bclabel_type(label):
    if label == 'bccv':
        return 'consent_verified'
    if label == 'bcr':
        return 'research'
    if label == 'bcocomm':
        return 'commercialization'
    if label == 'bcocoll':
        return 'collaboration'
    if label == 'bcmc':
        return 'multiple_community'
    if label == 'bcp':
        return 'provenance'
    if label == 'bccl':
        return 'clan'
    if label == 'bco':
        return 'outreach'
    if label == 'bccnv':
        return 'consent_non_verified'
    if label == 'bcnc':
        return 'non_commercial'
    if label == 'placeholder':
        return False

def assign_bclabel_img(label_type):
    baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/bclabels/'

    if label_type == 'bccv':
        return baseURL + 'bc-consent-verified.png'
    if label_type == 'bcr':
        return baseURL + 'bc-research-use.png' 
    if label_type == 'bcocomm':
        return baseURL + 'bc-open-to-commercialization.png'
    if label_type == 'bcocoll':
        return baseURL + 'bc-open-to-collaboration.png'
    if label_type == 'bcmc':
        return baseURL + 'bc-multiple-community.png'
    if label_type == 'bcp':
        return baseURL + 'bc-provenance.png'
    if label_type == 'bccl':
        return 'bc-clan.png'
    if label_type == 'bco':
        return 'bc-outreach.png'
    if label_type == 'bccnv':
        return 'bc-consent-non-verified.png'
    if label_type == 'bcnc':
        return 'bc-non-commercial.png'
    if label_type == 'placeholder':
        return None

def set_bcnotice_defaults(bcnotice):
    bcnotice.img_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/bc-notice.png'
    bcnotice.default_text = 'The BC (Biocultural) Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material or data. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information (DSI) generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC Labels are in development and their implementation is being negotiated.'
    bcnotice.save()