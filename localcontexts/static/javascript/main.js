// Dismiss Messages
var dismissBtn = document.getElementById('close-btn')
var messageDiv = document.getElementById('alert-message')

if (dismissBtn) { dismissBtn.addEventListener('click', () => { messageDiv.style.display = 'none'}) }

// Password fields in registration form
var passwordField = document.getElementById('id_password1')
var helpTextDiv = document.getElementById('help-text-pw')

if (passwordField) {
    passwordField.addEventListener('focusin', (event) => { helpTextDiv.style.display = 'block' })
    passwordField.addEventListener('focusout', (event) => { helpTextDiv.style.display = 'none' })
}

// Email validation function
function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

var registerUserBtn = document.getElementById('registerUserBtn')
if (registerUserBtn) { registerUserBtn.addEventListener('click', () => disableSubmitRegistrationBtn()) }

function disableSubmitRegistrationBtn() {
    document.getElementById('registerUserForm').submit()

    let oldValue = 'Continue <i class="fa fa-arrow-right"></i>'
    registerUserBtn.setAttribute('disabled', true)
    registerUserBtn.innerText = 'Submitting...'
    
    window.addEventListener('load', function() {
        registerUserBtn.innerText = oldValue
        registerUserBtn.removeAttribute('disabled')
    })
} 

(function() {
    // COPY BUTTONS
    const copyBtns = document.querySelectorAll('.copy-btn')
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = document.querySelector(`#${btn.dataset.target}`)
            target.select()
            target.setSelectionRange(0, 99999)
            navigator.clipboard.writeText(target.value)
        })
    })

    // GREY CONTENT DROPDOWNS
    const toggleIcons = document.querySelectorAll('.toggle-icon')
    toggleIcons.forEach(icon => {
        icon.addEventListener('click', () => {
            const targetDivId = icon.getAttribute('data-target')
            const targetDiv = document.getElementById(targetDivId)
            targetDiv.classList.toggle('hide')

            if (targetDiv.classList.contains('hide')) {
                icon.classList.replace('fa-angle-up', 'fa-angle-down');
            } else {
                icon.classList.replace('fa-angle-down', 'fa-angle-up');
            }
        })
    })

})()

if (window.location.href.includes('sandbox.localcontextshub')) {
    let regHeader = document.getElementById('reg-header')
    let authHeader = document.getElementById('auth-header')
    let svgHeader = document.getElementById('svg-header')

    if(regHeader) { regHeader.style.marginTop = '50px' }

    if (authHeader){
        svgHeader.style.marginTop = '32px'
        authHeader.style.top = '50px'
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const initializeCharacterCounter = (textAreaId, counterId, maxChars) => {
        let textArea = document.getElementById(textAreaId);
        let characterCounter = document.getElementById(counterId);

        const countCharacters = () => {
            let numOfEnteredChars = textArea.value.length;
            let counter = maxChars - numOfEnteredChars;
            characterCounter.textContent = counter + '/' + maxChars;

            if (counter < 0) {
                characterCounter.style.color = 'red';
            } else if (counter < 50) {
                characterCounter.style.color = '#EF6C00';
            } else {
                characterCounter.style.color = 'black';
            }
        };

        countCharacters();
        textArea.addEventListener('input', countCharacters);
    };

    const url = window.location.href;
    const createPages = ['create-community', 'create-institution', 'connect-researcher', 'create-service-provider'];
    const updatePages = ['communities/update', 'institutions/update', 'researchers/update', 'service-providers/update'];

    if (createPages.some(page => url.includes(page)) || updatePages.some(page => url.includes(page))) {
        initializeCharacterCounter('id_description', 'charCount', 200);
    }
});

// Get languages from the IANA directory
function fetchLanguages() {
    const endpoint = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'

    fetch(endpoint)
        .then(response => {
            if (response.ok) {
                return response.json()
            } else if (response.status === 404) {
                return Promise.reject('404 Not Found')
            }
        })
        .then(data => { languageList(data) })
        .catch((err) => {console.error('Error: ', err)})
}

function languageList(data) {
    let langArray = Object.keys(data)
    // feed only array of languages into this function
    var langInputElements = document.getElementsByClassName('languageListInput')
    for (var i=0; i < langInputElements.length; i++) {
        autocomplete(langInputElements[i], langArray); 
    }
}

// converts accented letters to the unaccented equivalent
function removeAccents(str) {
  var map = {
    "a": '[àáâãäåæāăąǻ]',
    "b": '[ɓ]',
    "c": '[çćĉċč]',
    "d": '[ďđ]',
    "e": '[èéêëēĕėęěɛə]',
    "g": '[ĝğġģ]',
    "h": '[ĥħḥ]',
    "i": '[ìíîïĩīĭįɨİ]',
    "j": '[ĵ]',
    "k": '[ķ]',
    "l": '[ĺļľŀłı̨]',
    "n": '[ñńņňŉŋ]',
    "o": '[òóôõöøōŏőǫ]',
    "r": '[ŕŗř]',
    "s": '[śŝşšșṣ]',
    "t": '[ţťŧțṭ]',
    "u": '[ùúûüũūŭůűų]',
    "w": '[ŵ]',
    "y": '[ýÿŷ]',
    "z": '[źżž]'
  };
  
  for (var pattern in map) {
    str = str.replace(new RegExp(map[pattern], "gi"), pattern);
  }
  return str;
}

// Searchbar with autocomplete
// Takes two args: text iput element and array of values to autocomplete
function autocomplete(inp, arr) {
    var currentFocus;

    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = removeAccents(this.value);
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { 
            translationFormValidation()
            return false;
        }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        translationFormValidation()

        for (i = 0; i < arr.length; i++) {
          /*check if the item starts with the same letters as the text field value:*/
          if (removeAccents(arr[i]).substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                inp.setAttribute('value', this.getElementsByTagName("input")[0].value)
                inp.setAttribute('readonly', true)
                inp.classList.add('readonly-input')
                showClearLangBtn(inp.closest('.add-translation-form'))
                translationFormValidation()
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
          }
        }
    });

    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
          /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
          currentFocus++;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 38) { //up
          /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
          currentFocus--;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 13) {
          /*If the ENTER key is pressed, prevent the form from being submitted,*/
          e.preventDefault();
          if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) x[currentFocus].click();
          }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    
        // Get the value of the input element
        var inputValue = inp.value;
    
        // Map accented characters to unaccented versions
        var unaccentedValue = removeAccents(inputValue);
    
        // Loop through the autocomplete items
        for (var i = 0; i < x.length; i++) {
            // Get the value of the current autocomplete item
            var itemValue = x[i].getElementsByTagName("input")[0].value;
            // Map accented characters to unaccented versions
            var unaccentedItemValue = removeAccents(itemValue);
            // Check if the unaccented value matches the unaccented item value
            if (unaccentedItemValue.toUpperCase().indexOf(unaccentedValue.toUpperCase()) > -1) {
            /*if the item is found, mark as active:*/
            x[i].classList.add("autocomplete-active");
            }
        }
    }    

    function removeActive(x) {
      /*a function to remove the "active" class from all autocomplete items:*/
      for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
      }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });

    function showClearLangBtn(elem) {
        translationFormValidation()
        var clearLangBtn = elem.getElementsByTagName("button")[0]
        clearLangBtn.classList.remove("hide")
        clearLangBtn.addEventListener("click", function(e) {
            e.preventDefault()
            langInput = elem.getElementsByTagName("input")
            textarea = elem.getElementsByTagName("textarea")
            langInput[0].value = ''
            langInput[0].removeAttribute('value')
            langInput[1].value = ''
            langInput[1].removeAttribute('value')
            textarea[0].value=''
            textarea[0].removeAttribute('value')
            langInput[1].focus()

            if (langInput[1].getAttribute('readonly', true) && langInput[1].classList.contains('readonly-input')) {
                langInput[1].removeAttribute('readonly')
                langInput[1].classList.remove('readonly-input')
            }

            if (e.target.tagName.toLowerCase() == 'i') {
                e.target.parentNode.classList.add('hide')
            } else { e.target.classList.add('hide') }

            translationFormValidation();
        })
    }  
}

// check to see if the label language has been selected where needed
function translationFormValidation() {
    const languageError = document.getElementById('language-error')
    const addTranslationForms = document.querySelectorAll('.add-translation-form')
    const mainLangInput = document.getElementById('id_language')

    function saveLabelBtnValidation(status) {
        if (status == 'enable') {
            saveLabelBtn.disabled=false
            languageError.classList.add('hide')
        } else if (status == 'disable') {
            saveLabelBtn.disabled=true
            languageError.classList.remove('hide')
        }
    }

    var valid = true
    if (window.location.href.includes('/labels/customize') &&
        (mainLangInput.value == '')) 
        { valid = false}
    // Validate addTranslationForms
    for (var i = 0; i < addTranslationForms.length; i++) {
        var translatedNameInput = addTranslationForms[i].querySelector('[id$="translated_name"]');
        var translatedLangInput = addTranslationForms[i].querySelector('[id$="language"]');
        var translatedTextInput = addTranslationForms[i].querySelector('[id$="translated_text"]');

        // Check if all required fields are empty or not
        if (translatedLangInput.value === '' && !translatedLangInput.classList.contains('readonly-input') &&
        translatedNameInput.value === '' &&
        translatedTextInput.value === '') {
            // All fields are empty - no issue
            valid = true
        }

        // Invalidate if any field is filled and others are empty
        if ((translatedLangInput.value !== '' && (translatedNameInput.value === '' || translatedTextInput.value === '')) ||
        (translatedNameInput.value !== '' && (translatedLangInput.value === '' || translatedTextInput.value === '')) ||
        (translatedTextInput.value !== '' && (translatedLangInput.value === '' || translatedNameInput.value === ''))) {
            valid = false
        }
    }

    if (valid == true) {
        saveLabelBtnValidation('enable')
    } else {saveLabelBtnValidation('disable')}
}

async function fetchLabels(type) {
    const response = await fetch('/static/json/Labels.json')
    const data = await response.json()
    if (type == 'bc') { return data.bcLabels } else if (type == 'tk') { return data.tkLabels } else if (type == 'both') { return data }
}

const supportedLanguages = ['French', 'Spanish', 'Māori', 'English'];

async function fetchLabelTranslations() {
    const response = await fetch('/static/json/LabelTranslations.json');
    const data = await response.json();
    return data;
}

function findLabelAndSetValues(labels, id, selectedLanguage,label_name,label_text) {
    const label = labels.find(label => id === label.labelCode && selectedLanguage === label.translated_language);
    if (label) {
        label_name.value = label.labelTranslatedName;
        label_text.innerHTML = label.labelTranslatedText;
        translationFormValidation()
    }
}

// Expand BC Labels Card in Community: Labels -> select-labels
function showBCLabelInfo() {
    let labelContainer = document.getElementById('expand-bclabels')
    let span = document.getElementById('show-more-down')
    let fullCard = document.getElementById('collapsed-card')
    let header = document.getElementById('bclabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        header.style.margin = "0"
        fullCard.style.height = "auto"
        labelContainer.style.height = "auto"
        span.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        header.style.margin = "auto 0"
        fullCard.style.height = "113px"
        // fullCard.style.transition = "height 0.5s"
        labelContainer.style.height = "0px"
        span.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
    }
}

// See more info about each label (Community:Labels)
function expandBCLabel(img) {

    // Toggle selected Label color 
    let txtDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    txtDivs.forEach(node => { if (node == img.parentElement.nextElementSibling) { node.classList.replace('grey-text', 'darkteal-text') } else { node.classList.replace('darkteal-text', 'grey-text') } })

    let targetImg = img.id

    // Provenance
    let infoProv = document.getElementById('bclabel-info-prov')
    let titleProv = document.getElementById('bc-label-title-prov')
    let templateTextProv = document.getElementById('label-template-text-bc-prov')
    let whyUseLabelTextProv = document.getElementById('why-use-this-label-bc-prov')

    // Protocols
    let infoProt = document.getElementById('bclabel-info-prot')
    let titleProt = document.getElementById('bc-label-title-prot')
    let templateTextProt = document.getElementById('label-template-text-bc-prot')
    let whyUseLabelTextProt = document.getElementById('why-use-this-label-bc-prot')

    // Permissions
    let infoPerms = document.getElementById('bclabel-info-perm')
    let titlePerms = document.getElementById('bc-label-title-perm')
    let templateTextPerms = document.getElementById('label-template-text-bc-perm')
    let whyUseLabelTextPerms = document.getElementById('why-use-this-label-bc-perm')

    // Hidden Inputs
    let inputProv = document.getElementById('bc-label-value-type-prov')
    let inputProt = document.getElementById('bc-label-value-type-prot')
    let inputPerms = document.getElementById('bc-label-value-type-perm')

    fetchLabels('bc').then(populateBCLabel)

    // Set content based on which Label was selected
    function populateBCLabel(data) {
        data.forEach(bclabel => {
            if (bclabel.labelCode == targetImg) { 
                displayExpandedImage(targetImg)
                checkLabelExists(bclabel, targetImg, 'BC')

                if (bclabel.labelCategory == 'protocol') {
                    openLabelInfoDiv(infoProt, infoProv, infoPerms)
                    //  Assign input value based on which bc label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = bclabel.labelName
                    templateTextProt.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProt.textContent = bclabel.whyUseThisLabel  
                
                } else if (bclabel.labelCategory == 'provenance') {
                    openLabelInfoDiv(infoProv, infoProt, infoPerms)
                    inputProv.value = targetImg
                    titleProv.textContent = bclabel.labelName
                    templateTextProv.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProv.textContent = bclabel.whyUseThisLabel

                } else if (bclabel.labelCategory == 'permission') {
                    openLabelInfoDiv(infoPerms, infoProt, infoProv)
                    inputPerms.value = targetImg
                    titlePerms.textContent = bclabel.labelName
                    templateTextPerms.textContent = bclabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = bclabel.whyUseThisLabel
                }
            }
        })
    }

}

// Will disable "customize Label" btn if Label exists (select-labels)
function checkLabelExists(label, selectedLabelCode, labelType) {
    let btnProv = document.getElementById(`btn${labelType}Prov`)
    let btnProt = document.getElementById(`btn${labelType}Prot`)
    let btnPerms = document.getElementById(`btn${labelType}Perms`)

    if (btnProv || btnProt || btnPerms) {
        // Takes all hidden inputs with the label_type of labels that have already been created by the community
        let inputs = Array.from(document.querySelectorAll(`.check${labelType}LabelType`))
        let values = []
        inputs.forEach(input => values.push(input.value))

        if (label.labelCode == selectedLabelCode) {
            if (values.includes(label.labelType)) {
                if (label.labelCategory == 'provenance') {
                    btnProv.setAttribute("disabled","disabled")
                } else if (label.labelCategory == 'protocol') {
                    btnProt.setAttribute("disabled","disabled")
                } else if (label.labelCategory == 'permission') {
                    btnPerms.setAttribute("disabled","disabled")
                }
            }  else {
                if (label.labelCategory == 'provenance') {
                    btnProv.removeAttribute("disabled")
                } else if (label.labelCategory == 'protocol') {
                    btnProt.removeAttribute("disabled")
                } else if (label.labelCategory == 'permission') {
                    btnPerms.removeAttribute("disabled")
                }
            }
        }        
    }
}

// Display Label images that was clicked in the expanded Div
function displayExpandedImage(labelCode) {
    let imgArray

    if (labelCode.startsWith('b')) {
        imgArray = Array.from(document.querySelectorAll('.bc-img-div'))
    } else if (labelCode.startsWith('t')) {
        imgArray = Array.from(document.querySelectorAll('.tk-img-div'))
    }

    for (let i = 0; i < imgArray.length; i ++) {
        // take the id and split it, compare labelCode to the split
        if (imgArray[i].id.slice(21) == labelCode) { imgArray[i].classList.replace('hide', 'show') } else { imgArray[i].classList.replace('show', 'hide') }
    }
}

// Community: Customize labels -- populate default text
var parentDiv = document.getElementById('target-img-div')
if (parentDiv) {
    var image = parentDiv.firstChild.nextSibling
    populateTemplate(image.id)
}

function populateTemplate(id) {
    let templateText = document.getElementById('label-template-text')
    let templateName = document.getElementById('label-template-name')
    let hiddenInput = document.getElementById('input-label-name')
    let whyUseText = document.getElementById('whyUseText')
    let labelNamePTag = document.getElementById('labelNamePTag')
    let language = document.getElementById('id_language')
    let language_support = document.getElementById('languageError')

    fetchLabels('both').then(populate)

    function populate(data) {
        if (id.startsWith('b')) {
            let bclabels = data.bcLabels
            bclabels.forEach(bclabel => {
                if (id == bclabel.labelCode) {
                    labelNamePTag.innerHTML = bclabel.labelName
                    whyUseText.textContent = bclabel.whyUseThisLabel
                    hiddenInput.value = bclabel.labelName
                    templateName.value = bclabel.labelName
                    templateText.textContent = bclabel.labelDefaultText
                }
            })
        } else if (id.startsWith('t')) {
            let tklabels = data.tkLabels
            tklabels.forEach(tklabel => {
                if (id == tklabel.labelCode) {
                    labelNamePTag.innerHTML = tklabel.labelName
                    whyUseText.textContent = tklabel.whyUseThisLabel
                    hiddenInput.value = tklabel.labelName
                    templateName.value = tklabel.labelName
                    templateText.textContent = tklabel.labelDefaultText
                }
            })
        }
    }

    const observer = new MutationObserver(async function (mutationsList) {
        for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                const selectedLanguage = language.value;
                if (selectedLanguage == "English" || selectedLanguage == "") {
                    language_support.style.display = (language_support.style.display === 'none') ? 'none' : 'none';
                    fetchLabels('both').then(populate)
                } else if (supportedLanguages.includes(selectedLanguage)) {
                    language_support.style.display = (language_support.style.display === 'none') ? 'none' : 'none';
                    try {
                        const data = await fetchLabelTranslations();
                        if (id.startsWith('b') && data.bcLabels) {
                        findLabelAndSetValues(data.bcLabels, id, selectedLanguage, templateName, templateText);
                        } else if (id.startsWith('t') && data.tkLabels) {
                        findLabelAndSetValues(data.tkLabels, id, selectedLanguage, templateName, templateText);
                        } else {
                        console.error(`Data for '${id.startsWith('b') ? 'bcLabels' : 'tkLabels'}' is missing or not in the expected format.`);
                        }
                    } catch (error) {
                        console.error("Error fetching label translations:", error);
                    }
                } else if (selectedLanguage != "") {
                    const language_supportMessage = `We do not have translated Label template text in ${selectedLanguage} at this time.`;
                    language_support.textContent = language_supportMessage;
                    language_support.style.display = (language_support.style.display === 'none') ? 'block' : 'block';
                    fetchLabels('both').then(populate)
                }
            }
        }
    });
      
    observer.observe(language, { attributes: true, attributeFilter: ['value'] });
}

function expandCCNotice(noticeDiv) {
    let divID = noticeDiv.id
    let divToOpen = document.getElementById(`openDiv-${divID}`)
    let clickedPTag = noticeDiv.querySelector('p')
    let allDivs = document.querySelectorAll('.cc-notice__expanded-container')

    let allPTags = Array.from(document.querySelectorAll('.cc-notice__container p'))

    allPTags.forEach((node) => {
        if (node === clickedPTag) {
            node.classList.toggle('cc-active')
        } else {
            node.classList.remove('cc-active')
        }
    })

    allDivs.forEach((div) => {
        if (div === divToOpen) {
            div.classList.toggle('hide')
        } else {
            div.classList.add('hide')
        }
    })
}

function expandDisclosureNotice(noticeDiv) {
    let divID = noticeDiv.id
    let divToOpen = document.getElementById(`openDiv-${divID}`)
    let clickedPTag = noticeDiv.querySelector('p')
    let allDivs = document.querySelectorAll('.disclosure-notice__expanded-container')

    let allPTags = Array.from(document.querySelectorAll('.cc-notice__container p'))

    allPTags.forEach((node) => {
        if (node === clickedPTag) {
            node.classList.toggle('cc-active')
        } else {
            node.classList.remove('cc-active')
        }
    })

    allDivs.forEach((div) => {
        if (div === divToOpen) {
            div.classList.toggle('hide')
        } else {
            div.classList.add('hide')
        }
    })
}

// Customize Label: clone translation form to add multiple translations
if (window.location.href.includes('/labels/customize') || window.location.href.includes('/labels/edit')) {
    const addTranslationBtn = document.getElementById('add-translation-btn')
    if (addTranslationBtn) { addTranslationBtn.addEventListener('click', cloneForm, false)}

    // h/t: https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript
    const initialTargetNodes = document.querySelectorAll('[id^="id_form-"][id$="-language"]');
    initializeObserver(initialTargetNodes);

    function cloneForm(e) {
        e.stopImmediatePropagation()
        e.preventDefault()
        
        let translationForm = document.querySelectorAll('.add-translation-form')
        let container = document.querySelector('#translation-form-container')
        let totalForms = document.querySelector("#id_form-TOTAL_FORMS")
        let lastDiv = document.getElementById('lastDiv')

        let formNum = translationForm.length-1

        let newForm = translationForm[0].cloneNode(true)
        let formRegex = RegExp(`form-(\\d){1}-`,'g')

        formNum++

        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`)
        newFormInputs = newForm.querySelectorAll('input, textarea')
        for (var i = 0; i < newFormInputs.length; i++){
            newFormInputs[i].removeAttribute('value')
            newFormInputs[i].removeAttribute('readonly')
            newFormInputs[i].classList.remove('readonly-input')
            newFormInputs[i].innerHTML="";
        }

        let newErrorDiv = newForm.querySelector(`#id_form-${formNum}-language_support`);
        if (newErrorDiv) {
            newErrorDiv.style.display = 'none';
        }
        
        newFormLangButton = newForm.querySelector('button[name="clear-language-btn"]')
        newFormLangButton.classList.add('hide')
        container.insertBefore(newForm, lastDiv)
        totalForms.setAttribute('value', `${formNum+1}`)
        languageFormValidation()

        const updatedTargetNodes = document.querySelectorAll('[id^="id_form-"][id$="-language"]');
        disconnectObserver();
        initializeObserver(updatedTargetNodes);

        languageFormValidation();
    }

    function initializeObserver(targetNodes) {
        const config = { attributes: true, attributeFilter: ['value'] };
        observer = new MutationObserver(handleValueChange);

        targetNodes.forEach(targetNode => {
            observer.observe(targetNode, config);
        });
    }

    function disconnectObserver() {
        if (observer) {
            observer.disconnect();
        }
    }

    async function handleValueChange(mutationsList) {
        for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                const idMatches = mutation.target.id.match(/id_form-(\d+)-language/);
                if (idMatches) {
                    const formNumber = idMatches[1];
                    const required_language = mutation.target.value;
                    const translatedNameElement = document.querySelector(`#id_form-${formNumber}-translated_name`);
                    const translationSupport = document.querySelector(`#id_form-${formNumber}-language_support`);
                    const translatedTextElement = document.querySelector(`#id_form-${formNumber}-translated_text`);
                    if (supportedLanguages.includes(required_language)) {
                        translationSupport.style.display = (translationSupport.style.display === 'none') ? 'none' : 'none';
                        try {
                            const data = await fetchLabelTranslations();
                            if (image.id.startsWith('b') && data.bcLabels) {
                            findLabelAndSetValues(data.bcLabels, image.id, required_language, translatedNameElement, translatedTextElement);
                            } else if (image.id.startsWith('t') && data.tkLabels) {
                            findLabelAndSetValues(data.tkLabels, image.id, required_language, translatedNameElement, translatedTextElement);
                            }
                        } catch (error) {
                            console.error("Error fetching label translations:", error);
                        }
                    }
                    else if (required_language === ""){
                        translationSupport.style.display = (translationSupport.style.display === 'none') ? 'none' : 'none';
                        translatedNameElement.value = " ";
                        translatedTextElement.innerHTML= " ";
                    }
                    else if(!supportedLanguages.includes(required_language)){
                        const language_supportMessage = `We do not have translated Label template text in ${required_language} at this time.`;
                        translationSupport.textContent = language_supportMessage;
                        translationSupport.style.display = (translationSupport.style.display === 'none') ? 'block' : 'block';

                    }  
                }
            }
        }
    }
    languageFormValidation()

    // adds input event for translation name and text to make sure language is also selected
    function languageFormValidation() {
        var translation_name = document.querySelectorAll('[id$="translated_name"]')
        var translation_text = document.querySelectorAll('[id$="translated_text"]')
        
        for (var i=0; i < translation_name.length; i++) {
            translation_name[i].addEventListener('input', translationFormValidation)
        }
        for (var i=0; i < translation_text.length; i++) {
            translation_text[i].addEventListener('input', translationFormValidation)
        } 

        fetchLanguages()
    }

    const saveLabelBtn = document.getElementById('saveLabelBtn')
    saveLabelBtn.addEventListener('click', function() {    
        document.getElementById('saveLabelForm').submit()

        let oldValue = 'Save Label'
            saveLabelBtn.setAttribute('disabled', true)
            saveLabelBtn.innerText = 'Saving...'
            
        window.addEventListener('load', function() {
            saveLabelBtn.innerText = oldValue;
            saveLabelBtn.removeAttribute('disabled');
        })
    })
}

// Approve Label: show note div
if (window.location.href.includes('communities/labels/')) {
    const noBtn = document.getElementById('displayLabelNote')
    const closeNoteDivBtn = document.getElementById('closeNoteDiv')

    if (noBtn && closeNoteDivBtn) {
        noBtn.addEventListener('click', (e) => {
            e.preventDefault()
            let div = document.getElementById('labelNoteDiv')
            div.classList.remove('hide')
            div.classList.add('show')
        })

        closeNoteDivBtn.addEventListener('click', (e) => {
            e.preventDefault()
            let div = document.getElementById('labelNoteDiv')
            div.classList.replace('show', 'hide')
        }) 
    }
}

// Show more content: Project Overview Page
function showMore(elem) {
    let idToMatch = elem.id
    let expandDiv = document.getElementById(`expand-div-${idToMatch}`)
    let contentCard = document.getElementById(`full-div-card-${idToMatch}`)

   expandDiv.classList.toggle('hide')
   expandDiv.classList.toggle('show')

    if (expandDiv.classList.contains('show')) {
        elem.innerHTML = 'Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>'
        if (contentCard) { contentCard.style.height = "auto" }
    } else {
        elem.innerHTML = 'Show More <i class="fa fa-angle-down" aria-hidden="true"></i>'
        if (contentCard) { contentCard.style.height = "auto" }
    }
}

// Community: create project
// Community: apply labels
function displayDefaultText(elem) {
    let isChecked = elem.checked
    let labelID = elem.id
    let targetNum = labelID.slice(14)

    let targetDiv = document.getElementById(`open-default-text-${targetNum}`)
    let labelName = document.getElementById(`label-name-${targetNum}`)

    if (isChecked) {
        targetDiv.style.height = 'auto'
        labelName.classList.replace('grey-text', 'darkteal-text')
    } else {
        targetDiv.style.height = '0'
        labelName.classList.replace('darkteal-text', 'grey-text')
    }
}

if (window.location.href.includes('/labels/apply-labels/')) {
    const applyLabelsBtn = document.getElementById('applyLabelsBtn')
    applyLabelsBtn.addEventListener('click', function() {    
        document.getElementById('applyLabelsForm').submit()

        let oldValue = '<i class="fa fa-check" aria-hidden="true"></i>'
        applyLabelsBtn.setAttribute('disabled', true)
        applyLabelsBtn.innerText = 'Applying Labels...'
        
        window.addEventListener('load', function() {
            applyLabelsBtn.innerText = oldValue;
            applyLabelsBtn.removeAttribute('disabled');
        })
    })
}


// TK Labels : community -> labels -> select labels
function showTKLabelInfo() {
    let labelContainer = document.getElementById('expand-tklabels')
    let span = document.getElementById('show-more-tk-down')
    let fullCard = document.getElementById('collapsed-tkcard')
    let header = document.getElementById('tklabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        header.style.margin = "0"
        fullCard.style.height = "auto"
        labelContainer.style.height = "auto"
        span.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        header.style.margin = "auto 0"
        fullCard.style.height = "113px"
        labelContainer.style.height = "0px"
        span.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
    }
}

// Select Label - View Info about label 
function expandTKLabel(img) {
    // Change Text Color on selected Label
    let txtDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    txtDivs.forEach(node => {
        if (node == img.parentElement.nextElementSibling) { node.classList.replace('grey-text', 'darkteal-text') } else { node.classList.replace('darkteal-text', 'grey-text') }
    })

    const targetImg = img.id

    // Provanance
    let infoProv = document.getElementById('tklabel-info-prov')
    let titleProv = document.getElementById('tk-label-title-prov')
    let templateTextProv = document.getElementById('label-template-text-tk-prov')
    let whyUseLabelTextProv = document.getElementById('why-use-this-label-tk-prov')

    // Protocols
    let infoProt = document.getElementById('tklabel-info-prot')
    let titleProt = document.getElementById('tk-label-title-prot')
    let templateTextProt = document.getElementById('label-template-text-tk-prot')
    let whyUseLabelTextProt = document.getElementById('why-use-this-label-tk-prot')

    // Permissions
    let infoPerms = document.getElementById('tklabel-info-perm')
    let titlePerms = document.getElementById('tk-label-title-perm')
    let templateTextPerms = document.getElementById('label-template-text-tk-perm')
    let whyUseLabelTextPerms = document.getElementById('why-use-this-label-tk-perm')

    // Hidden inputs to store Label selected value
    let inputProv = document.getElementById('tk-label-value-type-prov')
    let inputProt = document.getElementById('tk-label-value-type-prot')
    let inputPerms = document.getElementById('tk-label-value-type-perm')

    fetchLabels('tk').then(populateTKLabel)

    function populateTKLabel(data) {
        data.forEach(tklabel => {
            if (tklabel.labelCode == targetImg) {
                displayExpandedImage(targetImg)
                checkLabelExists(tklabel, targetImg, 'TK')

                if (tklabel.labelCategory == 'protocol') {
                    openLabelInfoDiv(infoProt, infoProv, infoPerms)
                    //  Assign input value based on which tk label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = tklabel.labelName
                    templateTextProt.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProt.textContent = tklabel.whyUseThisLabel       

                } else if (tklabel.labelCategory == 'provenance') {
                    openLabelInfoDiv(infoProv, infoProt, infoPerms)
                    inputProv.value = targetImg
                    titleProv.textContent = tklabel.labelName
                    templateTextProv.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProv.textContent = tklabel.whyUseThisLabel

                } else if (tklabel.labelCategory == 'permission') {
                    openLabelInfoDiv(infoPerms, infoProt, infoProv)
                    inputPerms.value = targetImg
                    titlePerms.textContent = tklabel.labelName
                    templateTextPerms.textContent = tklabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = tklabel.whyUseThisLabel       
                }
            }
        })
    }
}

// When Label is clicked to be customized, show details
function openLabelInfoDiv(targetDiv, divToCloseOne, divToCloseTwo) {
    // Open target div 
    if (targetDiv.classList.contains('hide')) { targetDiv.classList.replace('hide', 'show') }

    // Close other two divs if open
    if (divToCloseOne.classList.contains('show')) { divToCloseOne.classList.replace('show', 'hide') }
    if (divToCloseTwo.classList.contains('show')) { divToCloseTwo.classList.replace('show', 'hide') }
}

function closeLabelInfoDiv(targetBtn) {
    // Divs to close
    let infoTKProv = document.getElementById('tklabel-info-prov')
    let infoTKProt = document.getElementById('tklabel-info-prot')
    let infoTKPerm = document.getElementById('tklabel-info-perm')
    let infoBCProv = document.getElementById('bclabel-info-prov')
    let infoBCProt = document.getElementById('bclabel-info-prot')
    let infoBCPerm = document.getElementById('bclabel-info-perm')

    let btnId = targetBtn.id

    // Check if target button includes str in id
    let tkProv = btnId.includes('tk-prov')
    let bcProv = btnId.includes('bc-prov')
    let tkProt = btnId.includes('tk-prot')
    let bcProt = btnId.includes('bc-prot')
    let tkPerm = btnId.includes('tk-perm')
    let bcPerm = btnId.includes('bc-perm')

    switch(true) {
        case tkProv:
            infoTKProv.classList.replace('show', 'hide')        
            break;
        case bcProv:
            infoBCProv.classList.replace('show', 'hide')        
            break;
        case tkProt:
            infoTKProt.classList.replace('show', 'hide')
            break;
        case bcProt:
            infoBCProt.classList.replace('show', 'hide')
            break;
        case tkPerm:
            infoTKPerm.classList.replace('show', 'hide')
            break;
        case bcPerm:
            infoBCPerm.classList.replace('show', 'hide')
            break;
    }
}

// CREATE PROJECT: PROJECT TYPE OTHER: TOGGLE VISIBILITY
var projectTypeSelect = document.getElementById('id_project_type')
if (projectTypeSelect) {
    projectTypeSelect.addEventListener('change', function() {
        let otherTypeField = document.getElementById('otherTypeField')
        if (projectTypeSelect.value == 'Other') {
            otherTypeField.classList.replace('hide', 'show')
        } else {
            otherTypeField.classList.replace('show', 'hide')
        }
    })
}

let selectedDivCount = 0; 
// PROJECTS: NOTIFY communities - select desired communities
function selectCommunities() {
    let select = document.getElementById('communities-select')
    let allOptionsArray = Array.from(select.options)
    // Remove first element of options array
    let allOptionsMinusFirst = allOptionsArray.slice(1)

    allOptionsMinusFirst.forEach(option => {
        let selectedCommunityDiv = document.getElementById(`selected-community-${option.id}`)
        let div = document.getElementById(`comm-id-input-${option.id}`)

        if (option.selected  && !selectedCommunityDiv.classList.contains('show')) {
            selectedDivCount++;
            selectedCommunityDiv.classList.replace('hide', 'show')
            div.innerHTML = `<input type="hidden" value="${option.id}" name="selected_communities">`
        }
        select.disabled = notification_count > 1 && selectedDivCount >= notification_count;
    })
}

// Projects: notify communities - close selected
function cancelCommunitySelection(elem) {
    let id = elem.id
    let matches = id.match(/(\d+)/)
    let targetNum = matches[0]
    let divToClose = document.getElementById(`selected-community-${targetNum}`)
    let inputDivToRemove = document.getElementById(`comm-id-input-${targetNum}`)
    var select = document.getElementById('communities-select')

    divToClose.classList.replace('show', 'hide')
    inputDivToRemove.innerHTML = ``
    if (selectedDivCount > 0) {
        selectedDivCount--;
    }
    if (selectedDivCount < notification_count) {
        select.disabled = false;
    }
    
}


// Add project people on institution create-project
// h/t: https://medium.com/all-about-django/adding-forms-dynamically-to-a-django-formset-375f1090c2b0
document.addEventListener('DOMContentLoaded', (event) => {
    if (window.location.href.includes('/projects/create-project')) {
        initializeCreateProject();
    } else if (window.location.href.includes('/projects/edit-project')) {
        initializeEditProject();
    }

    function initializeCreateProject() {
        var count = 0;

        document.querySelectorAll('.clone-form-btn').forEach(button => {
            button.addEventListener('click', () => cloneCreateProjectForm(count));
        });

        function cloneCreateProjectForm() {
            const clonedItemsContainer = document.getElementById('clonedItems');

            // Total forms hidden input needs to be incremented
            let hiddenInputs = document.getElementsByName('form-TOTAL_FORMS');
            let totalFormInput = hiddenInputs[0];

            // Need to increment that number by 1 each time parent div is duplicated
            // Get parent div, clone it and change its attributes
            let parentDiv = document.getElementById('person-form-0');
            let clone = parentDiv.cloneNode(true);
            clone.id = 'person-form-' + ++count; // unique id
            clone.classList.add('mt-8');

            // Name input has name='form-0-name' and id='id_form-0-name'
            // Email input has name='form-0-email' and id='id_form-0-email'

            let nameInput = clone.getElementsByTagName('input')[0];
            let emailInput = clone.getElementsByTagName('input')[1];
            nameInput.value = '';
            emailInput.value = '';
            nameInput.id = `id_form-${count}-name`;
            nameInput.name = `form-${count}-name`;
            emailInput.id = `id_form-${count}-email`;
            emailInput.name = `form-${count}-email`;
            totalFormInput.value = parseInt(totalFormInput.value) + 1;

            // Append clone to sibling
            clonedItemsContainer.appendChild(clone);

            // Attach event listener to new clone button
            clone.querySelector('.clone-form-btn').addEventListener('click', () => cloneCreateProjectForm(count));
        }
    }

    function initializeEditProject() {
        var count = parseInt(document.getElementById('id_additional_contributors-INITIAL_FORMS').value);

        document.querySelectorAll('.clone-form-btn').forEach(button => {
            button.addEventListener('click', () => cloneEditProjectForm(count));
        });

        function cloneEditProjectForm() {
            const clonedItemsContainer = document.getElementById('clonedItems');

            // Total forms hidden input needs to be incremented
            let totalFormInput = document.getElementsByName('additional_contributors-TOTAL_FORMS')[0];

            // Need to increment that number by 1 each time parent div is duplicated
            let currentIndex = parseInt(totalFormInput.value);
            let newIndex = currentIndex + 1;

            // Get parent div, clone it and change its attributes
            let parentDiv = document.getElementById('person-form-0');
            let clone = parentDiv.cloneNode(true);
            clone.id = 'person-form-' + newIndex; // unique id

            // Name input has name='additional_contributors-0-name' and id='id_additional_contributors-0-name'
            // Email input has name='additional_contributors-0-email' and id='id_additional_contributors-0-email'
            let nameInput = clone.querySelector('input[name$="-name"]');
            let emailInput = clone.querySelector('input[name$="-email"]');
            nameInput.value = '';
            emailInput.value = '';
            nameInput.id = `id_additional_contributors-${newIndex}-name`;
            nameInput.name = `additional_contributors-${newIndex}-name`;
            emailInput.id = `id_additional_contributors-${newIndex}-email`;
            emailInput.name = `additional_contributors-${newIndex}-email`;

            totalFormInput.value = newIndex;
            clonedItemsContainer.appendChild(clone);
            count++;

            // Attach event listener to new clone button
            clone.querySelector('.clone-form-btn').addEventListener('click', () => cloneEditProjectForm(count));
        }
    }
});
if (window.location.href.includes('/projects/edit-project') || window.location.href.includes('/projects/create-project') ) {
    // PROJECT LINKS
    const addProjectLinkBtn = document.getElementById('addProjectUrlBtn')
    addProjectLinkBtn.onclick = function() {
        const ul = document.getElementById('projectLinksUl')
        const input = document.getElementById('projectLinksInput')
        const items = input.value.split(',')

        for (const item of items) {
            // console.log(`${item}: `+isValidHttpUrl(item))
      
            if (isValidHttpUrl(item.trim())) {
                const li = document.createElement('li')
                li.id = item.trim()
                li.classList.add('mb-8')
                li.classList.add('show')
                li.innerHTML = `
                <div class="grey-chip flex-this row space-between">
                    <div><p class="center-name word-break">${item}</p></div>
                    <div id="btn-${item.trim()}" class="removeProjectUrlBtn pointer ml-8">&times;</div>
                </div>
                <input type="hidden" value="${item.trim()}" name="project_urls">`
    
                ul.appendChild(li)
            } else {
                alert('Please include full URL (with http or https) for project links.')
            }
        }
        input.value = ''
        // for create-project
        removeTargetDiv()
    }
    // For edit-project
    removeTargetDiv()

    function removeTargetDiv() {
        const removeProjectUrlBtns = document.querySelectorAll('.removeProjectUrlBtn')
        if (removeProjectUrlBtns != null) {
            removeProjectUrlBtns.forEach(btn => {
                let btnID = btn.id.trim()
                let arr = btnID.split('btn-')
                let divID = arr[1]
    
                btn.onclick = function() {
                    document.getElementById(divID).remove()
                }
            }) 
        }
    }

    // ADD / REMOVE CONTRIBUTORS
    const addContributorBtn = document.getElementById('add-contributor-btn')
    addContributorBtn.addEventListener('click', selectContributors)

    removeSelectedContributors()

    function selectContributors() {
        let contribInput = document.getElementById('contributor-input')
        let contribOptionsArray = Array.from(document.getElementById('contributors').options)

        contribOptionsArray.forEach(option => {
            // compare input value to option value
            if (option.value == contribInput.value) {

                // push id to researcherArray or institutionArray
                if (contribInput.value.includes('Researcher')) {
                    contribInput.value = ''

                    let selectedResearcherDiv = document.getElementById(`selected-researcher-${option.dataset.resid}`)
                    selectedResearcherDiv.classList.replace('hide', 'show')

                    let input = document.createElement('input')
                    input.setAttribute('id', `hiddenRes-${option.dataset.resid}` )
                    input.setAttribute('type', 'hidden')
                    input.setAttribute('name', 'selected_researchers')
                    input.setAttribute('value', option.dataset.resid)

                    selectedResearcherDiv.appendChild(input)
                } else if (contribInput.value.includes('Institution')) {
                    contribInput.value = ''

                    let selectedInstitutionDiv = document.getElementById(`selected-institution-${option.dataset.instid}`)
                    selectedInstitutionDiv.classList.replace('hide', 'show')

                    let input = document.createElement('input')
                    input.setAttribute('id', `hiddenInst-${option.dataset.instid}` )
                    input.setAttribute('type', 'hidden')
                    input.setAttribute('name', 'selected_institutions')
                    input.setAttribute('value', option.dataset.instid)

                    selectedInstitutionDiv.appendChild(input)
                } else {
                    contribInput.value = ''

                    let selectedCommunityDiv = document.getElementById(`selected-community-${option.dataset.commid}`)
                    selectedCommunityDiv.classList.replace('hide', 'show')

                    let input = document.createElement('input')
                    input.setAttribute('id', `hiddenComm-${option.dataset.commid}` )
                    input.setAttribute('type', 'hidden')
                    input.setAttribute('name', 'selected_communities')
                    input.setAttribute('value', option.dataset.commid)
                    selectedCommunityDiv.appendChild(input)
                }
            }
        })
    }

    function removeSelectedContributors() {
        const removeResearcherBtns = document.querySelectorAll('.removeSelectedResearcherBtn')
        const removeInstitutionBtns = document.querySelectorAll('.removeSelectedInstitutionBtn')
        const removeCommunityBtns = document.querySelectorAll('.removeSelectedCommunityBtn')
        const removeProjectPersonBtns = document.querySelectorAll('.removeSelectedProjectPerson');

        function remove(btnGroup, btnIDStrToSplit, elemIDToHide, inputIDStrToRemove) {
            btnGroup.forEach(btn => {
                let btnID = btn.id.trim();
                let arr = btnID.split(btnIDStrToSplit);
                let targetID = arr[1];

                btn.onclick = function() {
                    let divToHide = document.getElementById(`${elemIDToHide}${targetID}`);
                    divToHide.classList.replace('show', 'hide');
                    document.getElementById(`${inputIDStrToRemove}${targetID}`).remove();
                };
            });
        }

        remove(removeResearcherBtns, 'closeRes-', 'selected-researcher-', 'hiddenRes-')
        remove(removeInstitutionBtns, 'closeInst-', 'selected-institution-', 'hiddenInst-')
        remove(removeCommunityBtns, 'closeComm-', 'selected-community-', 'hiddenComm-')
        removeProjectPersonBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const parent = btn.closest('li')
                const deleteField = parent.querySelector('input[name$="-DELETE"]')

                if (deleteField) {
                    deleteField.checked = true
                    parent.style.display = 'none'
                }
            })
        })
    }
}



function isValidHttpUrl(string) {
    let url;
    try { url = new URL(string) } catch (_) { return false }
    return url.protocol === "http:" || url.protocol === "https:"
  }

// Communities: Projects: Notify status
function setProjectStatus(elem) {
    let elementId = elem.id
    let projectID = elementId.slice(7)
    let statusSelect = document.getElementById(elementId)
    let statusSelectedInput = document.getElementById(`status-selection-input-${projectID}`)

    // Set second hidden value to value of option selected
    statusSelectedInput.value = statusSelect.options[statusSelect.selectedIndex].value
}

// Institutions/researchers: create-project: select Notices, show Notice descriptions
var submitProjectBtn = document.getElementById('submitProjectBtn')
if (submitProjectBtn) { 
    const projectForm = document.querySelector('#createProjectForm')
    const notices = projectForm.querySelectorAll('input[type=checkbox]:not([id*="DELETE"])')

    if (notices) {
        for (let i = 0; i < notices.length; i++) {
            notices[i].addEventListener('change', showDescription)
        }        
    }

    submitProjectBtn.addEventListener('click', validateProjectDisableSubmitBtn) 
}

function showDescription() {
    let target = document.getElementById(`show-description-${this.id}`)
    let pTag = document.getElementById(`title-${this.id}`)

    if (this.checked) {
        target.classList.replace('hide', 'show')
        pTag.classList.replace('grey-text', 'darkteal-text')
    } else {
        target.classList.replace('show', 'hide')
        pTag.classList.replace('darkteal-text', 'grey-text')
    }
}

function validateProjectDisableSubmitBtn() {
    // Require Checkbox selection for Notices in create-project researcher and institution
    // h/t: https://vyspiansky.github.io/2019/07/13/javascript-at-least-one-checkbox-must-be-selected/

    let form = document.querySelector('#createProjectForm')
    let checkboxes = form.querySelectorAll('input[type=checkbox]:not([id*="DELETE"]):not(.no-auto-validate)')

    if (checkboxes.length == 0) {
        disableSubmitBtn()
    } else {
        if (!isChecked()) {
            const errorMsg = !isChecked() ? 'At least one Notice must be selected.' : ''
            checkboxes[0].setCustomValidity(errorMsg)
        } else {
            disableSubmitBtn()
        } 
    }

    function isChecked() {
        for (let i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) return true
        }
        return false
    }

    function disableSubmitBtn() {
        document.getElementById('createProjectForm').submit()

        let oldValue = 'Save Project'
        submitProjectBtn.setAttribute('disabled', true)
        submitProjectBtn.innerText = 'Saving Project...'
        
        window.addEventListener('load', function() {
            submitProjectBtn.innerText = oldValue;
            submitProjectBtn.removeAttribute('disabled');
        })
    }      

}

function toggleNotifications(scope) {
  let activebutton = document.getElementById(`notification-button-${scope}`);
  let allButtons = document.querySelectorAll('[id^="notification-button-"]');
  let allNotificationDivs = document.querySelectorAll(
    '[id^="notification-v2-"]'
  );
  let activeNotificationDiv = document.getElementById(
    `notification-v2-${scope}`
  );

  allButtons.forEach(function (button) {
    if (button !== activebutton) {
      button.classList.remove("notification-button");
    }
  });

  activebutton.classList.toggle("notification-button");

  allNotificationDivs.forEach(function (element) {
    if (element !== activeNotificationDiv) {
      element.classList.remove("show");
    }
  });

  activeNotificationDiv.classList.toggle("show");

  window.onclick = function (event) {
    if (!event.target.matches(".dropbtn, .dropbtn i")) {
      allButtons.forEach(function (button) {
        button.classList.remove("notification-button");
      });

      allNotificationDivs.forEach(function (element) {
        element.classList.remove("show");
      });
    }
  };
}

if (window.location.href.includes('connect-community') || window.location.href.includes('connect-institution')) {

    let inputList = document.getElementById('selectedOrganizationInputList')
    inputList.addEventListener('change', setCommunity)
    inputList.addEventListener('click', setCommunity)

    function setCommunity() {
        let hiddenCommunityInput = document.getElementById('hidden-target-input')
        hiddenCommunityInput.value = inputList.value
    }

    // Join an organization
    const joinBtn = document.getElementById('openJoinRequestModalBtn')
    joinBtn.addEventListener('click', function(e) {

        // handle when inputlist value is ''
        if (!inputList.value) {
            alert('Please select an organization from the list')
        } else {
            e.preventDefault()
            const modal = document.getElementById('joinRequestModal')
            if (modal.classList.contains('hide')) {
                modal.classList.replace('hide', 'show')
            }
        
            const closeModalBtn = document.querySelector('.close-modal-btn')
            closeModalBtn.addEventListener('click', function() {
                modal.classList.replace('show', 'hide')
            })
        }
    })
} 

// Copy text to clipboard
function copyToClipboard(elemID) {
    let span = document.getElementById(elemID)
    var textArea = document.createElement("textarea");
    textArea.value = span.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("Copy");
    textArea.remove();
}
function buttonPulse(btnElm, milliseconds= 1000) {
    /*
    * Allows simulates the pulsing effect for some time period
    * */
    const pulseClasses = ['fa-solid', 'fa-check', 'fa-beat']

    btnElm.classList.add(...pulseClasses)
    setTimeout(() => {
        btnElm.classList.remove(...pulseClasses)
    }, milliseconds)
}


function openMemberModal() {
    const memberModal = document.getElementById('memberModal')
    memberModal.classList.replace('hide', 'show')

    // by default open the addModalView
    openAddModalView()

    const closeBtn = document.querySelector('.close-modal-btn')
    closeBtn.onclick = function() {
        memberModal.classList.replace('show', 'hide')
    }
}

function acceptJoinRequestModal(elem) {
    let modal = document.getElementById(`acceptJoinRequestModal_${elem.id}`)
    modal.classList.replace('hide', 'show')
    
    const closeBtn = document.getElementById(`closeModal${elem.id}`)
    closeBtn.onclick = function() {
        modal.classList.replace('show', 'hide')
    }
}

// use
// openBtnClasses: '.example'
// modalPartialId: 'modalName'
// closeBtnPartialId: 'closeModalBtn'
function modalToggle(openBtnClasses, modalPartialId, closeBtnPartialId) {
    const roleBtns = document.querySelectorAll(openBtnClasses)
    roleBtns.forEach(btn => {
        let buttonId = btn.id
        let arr = buttonId.split('_')
        let primary_id = arr[0]
        let user_id = arr[1]

        const openChangeRoleBtn = document.getElementById(`${primary_id}_${user_id}`)
        openChangeRoleBtn.addEventListener('click', function(e) {
            e.preventDefault()
            openTargetModal(user_id)
        })
    })

    function openTargetModal(id) {
        const modal = document.getElementById(`${modalPartialId}_${id}`)
        modal.classList.replace('hide', 'show')

        const closeModalBtn = document.getElementById(`${closeBtnPartialId}_${id}`)
        closeModalBtn.addEventListener('click', function(e) {
            e.preventDefault()
            modal.classList.replace('show', 'hide')
        })    
    }
}

// Change member role / remove member
if (window.location.href.includes('members')) {
    modalToggle('.changeRoleBtn', 'changeRoleModal', 'closeRoleChangeModal')
    modalToggle('.removeMemberBtn', 'removeMemberModal', 'closeRemoveMemberModal')
    document.getElementById('userListInput').addEventListener('input', disableBtnDuringInput)
} 

// Leave account
if (window.location.href.includes('manage')) {
    modalToggle('.leaveCommunityBtn', 'leaveCommAccountModal', 'closeLeaveCommModal')
    modalToggle('.leaveInstitutionBtn', 'leaveInstAccountModal', 'closeLeaveInstModal')
} 

function disableBtnDuringInput() {
    const currentValue = document.getElementById('userListInput').value;
    document.getElementById('sendMemberInviteBtn').disabled = currentValue.length === 0 || document.querySelector('option[value="' + currentValue + '"]') === null;
}

// Deactivate user popup in user settings
var deactivateAccountBtn = document.getElementById('submitDeactivation')
if (deactivateAccountBtn) {
    deactivateAccountBtn.addEventListener('click', function(event) {
        event.preventDefault()
        let deactivationModal = document.getElementById('deactivationModal')
        deactivationModal.classList.replace('hide', 'show')

        let cancelBtn = document.getElementById('closeDeactivationModal')
        cancelBtn.addEventListener('click', function(event) { deactivationModal.classList.replace('show', 'hide')})

        let continueDeactivationBtn = document.getElementById('continueDeactivationBtn')
        continueDeactivationBtn.addEventListener('click', function(){ document.getElementById('deactivateUserForm').submit() })
    })
}

// Deactivate and unlink g-account in user settings
function showConfirmationAlert() {
    var confirmationAlert = document.getElementById('googleConfirmationAlert');
    confirmationAlert.style.display = 'block';
}

function confirmUnlink() {
    var confirmationAlert = document.getElementById('googleConfirmationAlert');
    confirmationAlert.style.display = 'none';
    document.getElementById('unlinkForm').submit();
}

function cancelUnlink() {
    var confirmationAlert = document.getElementById('googleConfirmationAlert');
    confirmationAlert.style.display = 'none';
}

function cancelDisclaimer() {
    var disclaimerAlert = document.getElementById('disclaimerAlert');
    disclaimerAlert.style.display = 'none';
}
if (window.location.href.includes('newsletter/preferences/') ) {
    const unsubscribeChkbox = document.getElementById('unsubscribe');
    const unsubscribeBtn = document.getElementById('unsubscribebtn');
    const updatePreferencesBtn = document.getElementById('updatebtn');
    var topicChkbox = document.getElementsByName('topic');
    
    function unsubscribeDeselect() {
        if (unsubscribeChkbox.checked == true) {
            for (var i = 0; i < topicChkbox.length; i++){
                topicChkbox[i].checked=false;
                topicChkbox[i].disabled=true;
            }
        }

        if (unsubscribeChkbox.checked == false) {
            for (var i = 0; i < topicChkbox.length; i++){
                topicChkbox[i].disabled=false;
            }
        }
    }
}

// Add API Key Modals
if (window.location.href.includes('api-key')) {
    const generateAPIKeymodal = document.getElementById('generateAPIKeymodal')
    const generateAPIKeybtn = document.getElementById('generateAPIKeybtn')
    const deleteAPIKeymodal = document.getElementById('deleteAPIKeymodal')

    generateAPIKeybtn.addEventListener('click', () => {
        if (generateAPIKeymodal.classList.contains('hide')) { generateAPIKeymodal.classList.replace('hide', 'show')}
    })
    const closegenerateAPIKeymodal = document.getElementById('closegenerateAPIKeymodal')
    closegenerateAPIKeymodal.addEventListener('click', function() { generateAPIKeymodal.classList.replace('show', 'hide')})

    const closedeleteAPIKeymodal = document.getElementById('closedeleteAPIKeymodal')
    closedeleteAPIKeymodal.addEventListener('click', function() { deleteAPIKeymodal.classList.replace('show', 'hide')})
}

// REGISTRY FILTERING AND JOIN REQUESTS / CONTACT MODAL
if (window.location.href.includes('communities/view/') || window.location.href.includes('institutions/view/') || window.location.href.includes('researchers/view/') || window.location.href.includes('service-providers/view/') ) {

    // Join request modal and form
    const openRequestToJoinModalBtn = document.getElementById('openRequestToJoinModalBtn') 
    const requestToJoinModal = document.getElementById('requestToJoinModal') 

    const requestToJoinForm = document.getElementById('requestToJoinForm') 
    const sendRequestToJoinBtn = document.getElementById('sendRequestToJoinBtn') 

    const openContactModalBtn = document.getElementById('openContactModalBtn') 
    const contactModal = document.getElementById('contactModal') 
    const sendMsgForm = document.getElementById('sendMsgForm') 
    const sendMsgBtn = document.getElementById('sendMsgBtn') 

    // Open either modal
    if (openRequestToJoinModalBtn) {
        openRequestToJoinModalBtn.addEventListener('click', function() { requestToJoinModal.classList.replace('hide', 'show') })
    }
    openContactModalBtn.addEventListener('click', function() { contactModal.classList.replace('hide', 'show') })

    // Contact modal
    sendMsgBtn.addEventListener('click', function() { 
        let btnContent = `Send message <i class="fa fa-envelope" aria-hidden="true"></i>`
        disableSendBtn(sendMsgBtn, btnContent, sendMsgForm) 
    })

    sendRequestToJoinBtn.addEventListener('click', function() {
        let btnContent = `Send request`
        disableSendBtn(sendRequestToJoinBtn, btnContent, requestToJoinForm) 
    })

    closeModal(requestToJoinModal)
    closeModal(contactModal)

    // Temporarily disable the submit button to prevent multiple form submission
    function disableSendBtn(btn, btnContent, formToSubmit) {
        formToSubmit.submit() 

        btn.setAttribute('disabled', true)
        btn.innerText = 'Sending...'

        window.addEventListener('load', function() {
            btn.innerText = btnContent;
            btn.removeAttribute('disabled')
        })
    }

    function closeModal(modal) {  
        let closeBtns = Array.from(document.getElementsByClassName('close-modal-btn'))
        closeBtns.forEach(btn => { btn.addEventListener('click', hideModal)})
        function hideModal () { modal.classList.replace('show', 'hide') }
    }
}

if (
    window.location.href.includes('/invitations/')
) {
    document.addEventListener('DOMContentLoaded', function() {
        var disabledDiv = document.querySelector('.disabled-btn');
        if (disabledDiv) {
            disabledDiv.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
            });
        }
    });
}    
//  ONBOARDING MODAL: Shows up in dashboard if there isn't a localstorage item saved and onboarding_on is set to true
if (window.location.href.includes('dashboard')) {
    const hiddenInput = document.getElementById('openOnboarding')
    const onboardingModal = document.getElementById('onboardingModal')
    const closeOnboardBtns = document.querySelectorAll('.close-onboarding-btn')
    const nextBtns = document.querySelectorAll('.btn-next')
    const backBtns = document.querySelectorAll('.btn-back')
    const modalSteps = document.querySelectorAll('.onboard-step')

    let modalStepsNum = 0
    // If user does not have a last login and nothing is stored on localstorage
    if (hiddenInput.value == 'true' && !localStorage.getItem('closedOnboarding')) {
        // show modal
        onboardingModal.classList.replace('hide', 'show')
    } else {
        // if modal is showing, hide it
        if (onboardingModal.classList.contains('show')) {
            onboardingModal.classList.replace('show', 'hide')
        } else {
            onboardingModal.classList.add('hide')
        }
    }
    
    closeOnboardBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            onboardingModal.classList.add('hide')
            localStorage.setItem('closedOnboarding', 'true')
        })
    })
   
    nextBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            modalStepsNum++
            updateModalSteps()
        })
    })

    backBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            modalStepsNum--
            updateModalSteps()
        })
    })

    function updateModalSteps() {
        modalSteps.forEach(modalStep => {
            modalStep.classList.contains('onboard-step-active') &&
            modalStep.classList.remove('onboard-step-active')
        })
        modalSteps[modalStepsNum].classList.add('onboard-step-active')
    }

    // When 'tutorial' is clicked, removes localstorage item so onboarding can pop up
    const onboardingOn = document.getElementById('onboardingOn')
    onboardingOn.addEventListener('click', function() {
        localStorage.removeItem('closedOnboarding')
    })
}

// Notice Modals
if (window.location.href.includes('notices')) { 
    const OTCModal = document.getElementById('addURLModal')
    const addURLBtn = document.getElementById('addURLBtn')
    const shareBtn = document.getElementById('shareBtn')

    // OTC Add URL modal
    addURLBtn.addEventListener('click', () => {
        if (OTCModal.classList.contains('hide')) { OTCModal.classList.replace('hide', 'show')}
    })
    const closeAddURLModal = document.getElementById('closeAddURLModal')
    closeAddURLModal.addEventListener('click', function() { OTCModal.classList.replace('show', 'hide')})

    if (shareBtn){
        // Share OTC Notice Modal
        shareBtn.addEventListener('click', () => {
            if (shareOTCNoticeModal.classList.contains('hide')) { shareOTCNoticeModal.classList.replace('hide', 'show')}
        })
    }
    const closeshareOTCNoticeModal = document.getElementById('closeshareOTCNoticeModal')
    closeshareOTCNoticeModal.addEventListener('click', function() { shareOTCNoticeModal.classList.replace('show', 'hide')})

    // CC Notices modal
    const ccNoticeModal = document.getElementById('addCCPolicyModal')
    if (ccNoticeModal) {
        const openCCModalBtn = document.getElementById('openCCNoticeModal')
        openCCModalBtn.addEventListener('click', (e) => {
            e.preventDefault()
            if (ccNoticeModal.classList.contains('hide')) { ccNoticeModal.classList.replace('hide', 'show')}
        })
        const closeCCNoticeModal = document.getElementById('closeCCNoticeModal')
        closeCCNoticeModal.addEventListener('click', function() { ccNoticeModal.classList.replace('show', 'hide')})    
    }
}

// PROJECT ACTION PAGE
var copyProjectURLBtn = document.getElementsByClassName('copyProjectURLBtn')
var copyProjectIDBtn = document.getElementsByClassName('copyProjectIDBtn')
if (copyProjectIDBtn && copyProjectURLBtn) {
    for (var i = 0; i < copyProjectIDBtn.length; i++) {
        greenCopyBtn(copyProjectIDBtn[i], 'projectIDToCopy')
    }
    for (var i = 0; i < copyProjectURLBtn.length; i++) {
        greenCopyBtn(copyProjectURLBtn[i], 'projectURLToCopy')
    }
}

function greenCopyBtn(btnElem, spanIDToCopy) {
    btnElem.addEventListener('click', function() {
        copyToClipboard(spanIDToCopy)

        btnElem.innerHTML = `<i class="round-btn fa-solid fa-check fa-beat"></i>`
        setTimeout(() => {
            btnElem.innerHTML = `<i class="round-btn fa-regular fa-clone fa-rotate-90"></i>`
        }, 1000)
    })
}

// Share Modal - Embed Code customization options
if (
        window.location.href.includes('/projects/') || 
        window.location.href.includes('/notices/')
    ) {
    let embedCode = document.getElementById('embedToCopy')
    var layoutDropdown = document.getElementById('embedLayoutOptions')
    var languageDropdown = document.getElementById('embedLanguageOptions')
    var alignmentDropdown = document.getElementById('embedAlignOptions')
    var langArray= new Array();
    var layoutType, languageType, alignType = null

    if (layoutDropdown) {
        layoutDropdown.addEventListener("change", function(e) {
            layoutType = 'lt='+this.value+'&'
            updateEmbedCode()
        })
    }
    if (languageDropdown) {
        for (i=0;i < languageDropdown.options.length; i++) {
            if (langArray.includes(languageDropdown.options[i].value) == false) {
                langArray.push(languageDropdown.options[i].value)
                languageDropdown.options[i].classList.remove("hide");
            }
            else {
                languageDropdown.options[i].classList.add("hide");
            }
        }

        languageDropdown.addEventListener("change", function(e) {
            languageType = 'lang='+this.value+'&'
            updateEmbedCode()
        })
    }
    if (alignmentDropdown) {
        alignmentDropdown.addEventListener("change", function(e) {
            alignType = 'align='+this.value+'&'
            updateEmbedCode()
        })
    }

    function updateEmbedCode() {
        let customizationOptions = ""
        
        if (layoutType) {
            customizationOptions += layoutType
        }
        if (languageType) {
            customizationOptions += languageType
        }
        if (alignType) {
            customizationOptions += alignType
        }

        customizationOptions = customizationOptions.slice(0,-1)
        dataURL = embedCode.dataset.url
        dataTitle = embedCode.title

        embedCode.value = '<iframe width="100%" height="150" src="' + dataURL + '?' + customizationOptions + '" title="' + dataTitle + '" frameborder="0"></iframe>'
    }
}

// Open Window on Click
function openLinkInWindow(url) {
    window.open(url, "_blank")
}

// Share on Social Media
var shareToSocialsBtn = document.getElementsByClassName('shareToSocialsBtn')
if (shareToSocialsBtn) {
    for (var i = 0; i < shareToSocialsBtn.length; i++) {
        shareToSocialsBtnAction(shareToSocialsBtn[i])
    }
}

function shareToSocialsBtnAction(btnElem) {
    btnElem.addEventListener('click', function() {
        socialType = btnElem.getAttribute("data-social")
        dataURL = btnElem.getAttribute("data-url")
        dataTitle = btnElem.getAttribute("data-title")
        dataType = btnElem.getAttribute("data-type")

        if (socialType == 'email') {
            if( dataType == "project") {
                var emailSubject = encodeURIComponent("Local Contexts Project")
                var emailBody = encodeURIComponent("Check out this Local Contexts Project! "+dataTitle+" at "+dataURL)
            } else if( dataType == "otc-notice") {
                var emailSubject = encodeURIComponent("Local Contexts Open to Collaborate")
                var emailBody = encodeURIComponent("Check out my Local Contexts profile and Open to Collaborate Notice! at "+dataURL)
            }

            var mailtoLink = "mailto:?subject="+emailSubject+"&body="+emailBody
            window.location.href = mailtoLink

        } else if (socialType == 'facebook') {
            window.open('http://www.facebook.com/sharer/sharer.php?u='+dataURL, 'Share on Facebook')

        } else if (socialType == 'twitter') {
            if (dataType == "project") {
                messageText = "Check out this @LocalContexts project! #LocalContexts #traditionalknowledge #indigenousdata"
            } else if (dataType == "otc-notice") {
                messageText = "Check out my @LocalContexts profile and Open to Collaborate Notice! #LocalContexts #traditionalknowledge #indigenousdata #opentocollaborate"
            }

            window.open('https://twitter.com/intent/tweet?url='+dataURL+'&text='+messageText, 'Share on Twitter')

        } else if (socialType == 'linkedin') {
            window.open('https://www.linkedin.com/shareArticle?url='+dataURL)

        } else if (socialType == 'whatsapp') {
            if (dataType == "project") {
                messageText = encodeURIComponent("Check out this Local Contexts Project! "+dataTitle+" at "+dataURL)
            } else if (dataType == "otc-notice") {
                messageText = encodeURIComponent("Check out my Local Contexts profile and Open to Collaborate Notice at "+dataURL)
            }

            window.location.href = 'https://api.whatsapp.com/send?text='+messageText
        }
    })
}

function openModal(modalId, closeBtnId) {
    console.log(modalId)
    const modal = document.getElementById(modalId)
    modal.classList.replace('hide', 'show')

    const closeModalBtn = document.getElementById(closeBtnId)
    closeModalBtn.addEventListener('click', function() {
        modal.classList.replace('show', 'hide')
        closeModalBtn.removeEventListener('click', arguments.callee)
    })
}

function toggleSectionInfo(self, idToToggle) {
    let div = document.getElementById(idToToggle)
    let allDivs = document.querySelectorAll('.section-header-div')
    let lastDiv = allDivs[allDivs.length - 1]

    if (div.style.height == "0px") {
        self.innerHTML = '<i class="fa-solid fa-minus fa-xl darkteal-text"></i>'
        div.style.height = 'auto'
        div.style.overflow = 'visible'
        self.parentElement.classList.add('border-bottom-solid-teal')

        if (self.parentElement != lastDiv) {
            lastDiv.classList.add('border-bottom-solid-teal');
        }
    } else {
        div.style.height = '0px'
        div.style.overflow = 'hidden'
        self.innerHTML = '<i class="fa-solid fa-plus fa-xl darkteal-text"></i>'
        self.parentElement.classList.remove('border-bottom-solid-teal')

        if (self.parentElement == lastDiv) {
            lastDiv.classList.add('border-bottom-solid-teal');
        }
    }
}

function openUnlinkProjectModal(id) {
    const modal = document.getElementById(`unlinkProjectModal-${id}`)
    modal.classList.replace('hide', 'show')

    const cancelBtn = document.getElementById(`cancelBtn-${id}`)
    cancelBtn.addEventListener('click', function() { modal.classList.replace('show', 'hide')})

    const closeModalBtn = document.getElementById(`close-modal-btn-${id}`)
    closeModalBtn.addEventListener('click', function() { modal.classList.replace('show', 'hide')})
}

var checkList = document.getElementById('relatedProjectsList');
if (checkList) {
    checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
        if (checkList.classList.contains('visible'))
          checkList.classList.remove('visible');
        else
          checkList.classList.add('visible');
      }
    
    let connectBtn = document.getElementById('connectProjectsBtn')
    let checkboxes = document.querySelectorAll('input[name="projects_to_link"]')
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            let isChecked = Array.from(checkboxes).some(function(checkbox) {
                return checkbox.checked
            })

            connectBtn.disabled = !isChecked
            if (isChecked) {
                connectBtn.classList.replace('disabled-btn', 'action-btn')
            } else {
                connectBtn.classList.replace('action-btn', 'disabled-btn')
            }
        })
    })
}

function showProjectLabels(elem) {
    let id = elem.id
    let expandDiv = document.getElementById(`showContent-${id}`)

    expandDiv.classList.toggle('hide')
    expandDiv.classList.toggle('show')

    if (expandDiv.classList.contains('show')) {
        elem.classList.replace('fa-angle-down', 'fa-angle-up')
    } else {
        elem.classList.replace('fa-angle-up', 'fa-angle-down')
    }
}


if (window.location.href.includes('create-institution') && !window.location.href.includes('/noROR')) {
    const nameInputField = document.getElementById('organizationInput')
    const suggestionsContainer = document.getElementById('suggestionsContainer')
    const cityTownInputField = document.getElementById('institutionCityTown')
    const stateProvRegionInputField = document.getElementById('institutionStateProvRegion')
    const countryInputField = document.getElementById('institutionCountry')
    const hiddenInputField = document.getElementById('institutionIDROR')
    const createInstitutionBtn = document.getElementById('createInstitutionBtn')
    const clearFormBtn = document.getElementById('clearFormBtn')
    const descriptionField = document.getElementById('id_description')
    const contactNameField = document.getElementById('institutionContactNameField')
    const contactEmailField = document.getElementById('institutionContactEmailField')

    let characterCounter = document.getElementById('charCount')
    let delayTimer

    createInstitutionBtn.disabled = true

    nameInputField.addEventListener('input', () => {
        clearTimeout(delayTimer)

        const inputValue = nameInputField.value
        if (inputValue.length >= 3) { // Minimum characters required before making a request
            let queryURL = 'https://api.ror.org/organizations?query='
            
            delayTimer = setTimeout(() => {
            fetch(`${queryURL}${encodeURIComponent(inputValue)}`)
                .then(response => response.json())
                .then(data => {
                    showSuggestions(data.items)
                })
                .catch(error => { console.error(error)})
            }, 300) // Delay in milliseconds before making the request
        } else { clearSuggestions() }
    })

    clearFormBtn.addEventListener('click', (e) => {
        e.preventDefault()
        nameInputField.value = ''
        nameInputField.focus()
        createInstitutionBtn.disabled = true

        if (nameInputField.getAttribute('readonly', true) && nameInputField.classList.contains('readonly-input')) {
            nameInputField.removeAttribute('readonly')
            nameInputField.classList.remove('readonly-input')
        }

        cityTownInputField.value = ''
        stateProvRegionInputField.value = ''
        countryInputField.value = ''
        descriptionField.value = ''
        contactNameField.value = ''
        contactEmailField.value = ''

        characterCounter.textContent = '200/200'
    })

    function showSuggestions(items) {
        // Clear previous suggestions
        clearSuggestions()
        // Get the first 5 most relevant items
        const relevantItems = items.slice(0, 5)

        // Create and append suggestion items
        relevantItems.forEach(item => {
            const suggestionItem = document.createElement('div')
            suggestionItem.classList.add('suggestion-item')
            suggestionItem.innerHTML = `
                ${item.name} <br> 
                <small>${item.types}, ${item.country.country_name}</small>
            `
            suggestionItem.addEventListener('click', () => {
                // Populate input field with the selected suggestion
                nameInputField.value = item.name
                countryInputField.value = item.country.country_name
                hiddenInputField.value = item.id

                const addresses = item.addresses;
                if (addresses.length > 0) {
                    const address = addresses[0];
                    cityTownInputField.value = address.city
                    stateProvRegionInputField.value = address.state
                }
                createInstitutionBtn.disabled = false
                createInstitutionBtn.classList.replace('disabled-btn', 'action-btn')

                nameInputField.setAttribute('readonly', true)
                nameInputField.classList.add('readonly-input')

                clearSuggestions()
            })
                suggestionsContainer.appendChild(suggestionItem)
        })
    }
    
    function clearSuggestions() { suggestionsContainer.innerHTML = '' }
}

if (window.location.href.includes('/institutions/update/') || window.location.href.includes('/communities/update/') || window.location.href.includes('/researchers/update/') || window.location.href.includes('/service-providers/update/')) {
    const realImageUploadBtn = document.getElementById('institutionImgUploadBtn') || document.getElementById('communityImgUploadBtn') || document.getElementById('researcherImgUploadBtn') || document.getElementById('serviceProviderImgUploadBtn')
    const customImageUploadBtn = document.getElementById('altImageUploadBtn')
    const imagePreviewContainer = document.getElementById('imagePreviewContainer')

    function showFile() {
        const selectedFile = realImageUploadBtn.files[0]

        if (selectedFile) {
            showImagePreview(selectedFile)
        } else {
            clearImagePreview()
        }
    }

    function showImagePreview(file) {
        const reader = new FileReader()
        reader.onload = function(e) {
            const imagePreview = document.createElement('img')
            imagePreview.src = e.target.result
            imagePreviewContainer.innerHTML = ''
            imagePreviewContainer.appendChild(imagePreview)
        }
        reader.readAsDataURL(file)
    }

    function clearImagePreview() {
        imagePreviewContainer.innerHTML = ''
    }

    customImageUploadBtn.addEventListener('click', function(e) {
        e.preventDefault()
        realImageUploadBtn.click()
    })
 }


 if (window.location.href.includes('institutions/notices/')) {
    const realFileUploadBtn = document.getElementById('ccNoticePolicyUploadBtn')
    const customFileUploadBtn = document.getElementById('customCCPolicyFileUploadBtn')

    function showFileName() {
        const selectedFile = realFileUploadBtn.files[0]
        customFileUploadBtn.innerHTML = `${selectedFile.name} <i class="fa-solid fa-check"></i>`
    }

    function validatePolicyDocument() {
        const file = realFileUploadBtn.files[0]

        if (file) {
            const allowedExtensions = ['.pdf', '.doc', '.docx']
            const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))

            if (!allowedExtensions.includes(fileExt)) {
                alert('Invalid document file extension. Only PDF and DOC/DOCX files are allowed.')
                realFileUploadBtn.value = '' // Clear the file input field
                customFileUploadBtn.innerHTML = 'Upload Document <i class="fa-solid fa-upload"></i>'
                return false
            }

            const allowedMimeTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if (!allowedMimeTypes.includes(file.type)) {
                alert('Invalid document file type. Only PDF and DOC/DOCX files are allowed.')
                realFileUploadBtn.value = ''
                customFileUploadBtn.innerHTML = 'Upload Document <i class="fa-solid fa-upload"></i>'
                return false
            }
        }
        return true
    }

    customFileUploadBtn.addEventListener('click', function(e) {
        e.preventDefault()
        realFileUploadBtn.click()
    })

    realFileUploadBtn.addEventListener('change', validatePolicyDocument)

    // Collections Care Button Download
    const ccNoticeDownloadBtn = document.getElementById('ccNoticeDownloadBtn')
    if (ccNoticeDownloadBtn){
        ccNoticeDownloadBtn.addEventListener('click', function() {    
            let oldValue = 'Download Notices <i class="fa-solid fa-download"></i>'
            ccNoticeDownloadBtn.setAttribute('disabled', true)
            ccNoticeDownloadBtn.innerHTML = 'Downloading <div class="custom-loader ml-8"></div>'

            // Re-enable the button after a certain timeout
            // re-enable it after a while, assuming an average download duration
            setTimeout(function() {
                ccNoticeDownloadBtn.innerHTML = oldValue
                ccNoticeDownloadBtn.removeAttribute('disabled')
            }, 15000)
        })
    }
 }

 if (window.location.href.includes('/communities/labels/customize/') || window.location.href.includes('/communities/labels/edit/')) {
    const realAudioUploadBtn = document.getElementById('originalLabelAudioUploadBtn')
    const customAudioUploadBtn = document.getElementById('customLabelAudioFileUploadBtn')
    const clearAudioFileBtn = document.getElementById('clearAudiofileOnCustomizeBtn')

    function showAudioFileName() {
        const selectedFile = realAudioUploadBtn.files[0]
        customAudioUploadBtn.innerHTML = `${selectedFile.name} <i class="fa-solid fa-check"></i>`
        clearAudioFileBtn.classList.remove('hide')
    }

    customAudioUploadBtn.addEventListener('click', function(e) {
        e.preventDefault()
        realAudioUploadBtn.click()
    })

    clearAudioFileBtn.addEventListener('click', function(e) {
        e.preventDefault()
        customAudioUploadBtn.innerHTML = 'Upload audio file <i class="fa-solid fa-upload"></i>'
        clearAudioFileBtn.classList.add('hide')
        realAudioUploadBtn.value = ''
    })
 }

 if (window.location.href.includes('projects/actions/')) {
    function openRemoveContributorModal() {
        const modal = document.getElementById('removeContribModal')
        const closeModalBtn = document.getElementById('closeContributorModalBtn')

        modal.classList.remove('hide')

        closeModalBtn.addEventListener('click', function(e) {
            e.preventDefault()
            modal.classList.add('hide')
        })
    }

 }

 if (window.location.href.includes('communities/members/') ||  window.location.href.includes('institutions/members/') || window.location.href.includes('service-providers/members/')) {

    // Add member modal
    function openAddModalView() {
        const inviteView = document.getElementById('inviteUserModalView')
        const addView = document.getElementById('addMemberModalView')

        // hide inviteView and show addView
        addView.classList.replace('hide', 'show')
        inviteView.classList.replace('show', 'hide')

        // stop clicking on elements below
        event.stopPropagation()
    }

    function openInviteUserModalView() {
        const inviteView = document.getElementById('inviteUserModalView')
        const addView = document.getElementById('addMemberModalView')

        // hide addView and show inviteView
        addView.classList.replace('show', 'hide')
        inviteView.classList.replace('hide', 'show')

        // stop clicking on elements below
        event.stopPropagation()
    }

    function closeMemberModal() {
        const modalContent = document.getElementById('memberModalContent')
        const elementClickedIsChild = modalContent.contains(event.target)
        const elementClickedIsSelf = modalContent === event.target
        const elementClickedIsNotChild = !elementClickedIsChild || elementClickedIsSelf

        if (elementClickedIsNotChild) {
            const modal = document.getElementById('memberModal')
            modal.classList.replace('show', 'hide')
        }
    }
 }

if (window.location.href.includes('subscription-inquiry')) {
    function cancelDisclaimer() {
        var joinAlert = document.getElementById('disclaimerAlert');
        joinAlert.style.display = 'none';
    }
    document.addEventListener('DOMContentLoaded', function() {
    const nameInputField = document.getElementById('organizationInput')
    const suggestionsContainer = document.getElementById('suggestionsContainer')

    let delayTimer

    nameInputField.addEventListener('input', () => {
        clearTimeout(delayTimer)

        const inputValue = nameInputField.value.trim()
        if (inputValue.length >= 3) { // Minimum characters required before making a request
            let queryURL = 'https://api.ror.org/organizations?query='

            delayTimer = setTimeout(() => {

                var matchingInstitutions = nonRorInstitutes.filter(function(item) {
                    return item.fields.institution_name.toLowerCase().includes(inputValue.toLowerCase());
                });
                var matchingCommunities = communities.filter(function(item){
                    return item.fields.community_name.toLowerCase().includes(inputValue.toLowerCase());
                });
                var matchingServiceProviders = serviceProviders.filter(function(item){
                    return item.fields.name.toLowerCase().includes(inputValue.toLowerCase());
                });

                fetch(`${queryURL}${encodeURIComponent(inputValue)}`)
                    .then(response => response.json())
                    .then(data => {
                        showSuggestions(data.items, matchingInstitutions, matchingCommunities, matchingServiceProviders, inputValue)

                    })
                    .catch(error => { console.error(error)})

            }, 300) // Delay in milliseconds before making the request
        } else { clearSuggestions() }
    })

    function showSuggestions(items, matchingInstitutions, matchingCommunities, matchingServiceProviders, userInput) {
        // Clear previous suggestions
        clearSuggestions()
        // Get the first 5 most relevant itemss
        const combinedItems = [...matchingInstitutions, ...matchingCommunities, ...matchingServiceProviders, ...items];

        const filteredItems = combinedItems.filter(item =>
            (typeof item === 'object' && item.name?.toLowerCase().includes(userInput.toLowerCase())) ||
            (typeof item === 'object' && item.fields?.institution_name?.toLowerCase().includes(userInput.toLowerCase())) ||
            (typeof item === 'object' && item.fields?.community_name?.toLowerCase().includes(userInput.toLowerCase())) ||
            (typeof item === 'object' && item.fields?.name?.toLowerCase().includes(userInput.toLowerCase()))
        );

        // Check if any item exactly matches the user input
        const exactMatch = combinedItems.some(item =>
            (typeof item === 'object' && item.name?.toLowerCase() === userInput.toLowerCase()) ||
            (typeof item === 'object' && item.fields?.institution_name?.toLowerCase() === userInput.toLowerCase()) ||
            (typeof item === 'object' && item.fields?.community_name?.toLowerCase() === userInput.toLowerCase()) ||
            (typeof item === 'object' && item.fields?.name?.toLowerCase() === userInput.toLowerCase())
        );
        const relevantItems = filteredItems.slice(0, 5);
        // If no exact match, show 'not found in ROR List' message
        if (!exactMatch) {
            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.innerHTML = `${userInput} (Not in List)`;
            suggestionItem.addEventListener('click', () => {
                nameInputField.value = userInput;
                clearSuggestions();
                });
                suggestionsContainer.appendChild(suggestionItem);
        }
        displaySuggestions(relevantItems);

    }

      function displaySuggestions(items) {
        items.forEach(item => {
          const suggestionItem = document.createElement('div');
          suggestionItem.classList.add('suggestion-item');

          let displayName = '';
          let displayDetails = '';

          if (typeof item === 'object' && item.hasOwnProperty('name')) {
            displayName = item.name;
            displayDetails = `${item.types.join(", ")}, ${item.country.country_name} Institution`;
        } else if (typeof item === 'object' && item.hasOwnProperty('fields') && item.model === "institutions.institution") {
            displayName = item.fields.institution_name;
            displayDetails = `${item.fields.country ? item.fields.country + " " : ""}Institution`;
        } else if (typeof item === 'object' && item.hasOwnProperty('fields') && item.model === "communities.community") {
            displayName = item.fields.community_name;
            displayDetails = `${item.fields.country ? item.fields.country + " " : ""}Community`;
        } else if (typeof item === 'object' && item.hasOwnProperty('fields') && item.model === "serviceproviders.serviceprovider") {
            displayName = item.fields.name;
            displayDetails = `Service Provider`;
        }
          suggestionItem.innerHTML = `${displayName} <br> <small>${displayDetails}</small>`;

          suggestionItem.addEventListener('click', () => {
            nameInputField.value = displayName;
            clearSuggestions();
          });

          suggestionsContainer.appendChild(suggestionItem);
        });
    }

    function clearSuggestions() { suggestionsContainer.innerHTML = '' }
    })
};

if (window.location.href.includes('subscription-form')) {
    document.addEventListener("DOMContentLoaded", function () {
        const firstNameInput = document.querySelector('input[name="first_name"]');
        const lastNameInput = document.querySelector('input[name="last_name"]');
        const emailInput = document.querySelector('input[type="email"]');
        const organizationInput = document.querySelector('input[name="organization_name"]');
        const inquiryTypeRadios = document.querySelectorAll('input[name="inquiry_type"]');
        const submitButton = document.getElementById("createSubscription");
        const clearFormBtn = document.getElementById('clearFormBtn')
        
        validateForm()
        submitButton.addEventListener("click", disableButton)
        firstNameInput.addEventListener("input", validateForm);
        emailInput.addEventListener("input", validateForm);
        if (inquiryTypeRadios.length > 0) {
            inquiryTypeRadios.forEach(radio => radio.addEventListener("change", validateForm));
        }
        
    function validateForm() {
        const firstNameFilled = firstNameInput.value.trim() !== "";
        const emailFilled = emailInput.value.trim() !== "" && isValidEmail(emailInput.value.trim());
        const inquiryTypeSelected = inquiryTypeRadios.length > 0
            ? Array.from(inquiryTypeRadios).some(radio => radio.checked)
            : true;
        // Enable the button if all fields are valid
        if (firstNameFilled && emailFilled && inquiryTypeSelected) {
          submitButton.disabled = false;
        } else {
          submitButton.disabled = true;
        }
    }

    function disableButton() {
          document.getElementById("createSubscription").style.display = "none";
          document.getElementById("loading-spinner").classList.remove('hide');
      }
    
    clearFormBtn.addEventListener('click', (e) => {
        e.preventDefault()
        firstNameInput.value = ''
        submitButton.disabled = true

        lastNameInput.value = ''
        emailInput.value = ''
        inquiryTypeRadios.forEach(radio => {
            radio.checked = false;
        });
    })
});
};

if (window.location.href.includes('/subscription/')) {
    function openAddModalView() {
        const addView = document.getElementById('bundleModal')
        addView.classList.replace('hide', 'show')
        event.stopPropagation()
    }
    
    function closeBundleModal() {
        const modalContent = document.getElementById('bundleModalContent')
        const crossButton = document.getElementById('close-model-button')
    
        if (crossButton) {
            const modal = document.getElementById('bundleModal');
            modal.classList.replace('show', 'hide');
        }
    }
};