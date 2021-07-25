
//add active link for left panel ##############################################################################################################################
let current = location.pathname;

let arr_url = $('#left_panel a');

arr_url.each((t, el) => {
    if(el.getAttribute('href') == current){
        el.classList.toggle('active');
    }
});


//show note for the user #####################################################################################################################################
const noteForUser = (el, text, append) => {
    let $div = $(`<div class="row justify-content-center mt-3 ajax_check">
                    <div> 
                        <p class="alert alert-danger">${text}</p>
                    </div>
                </div>`);
    if(append == "append"){
        $(el).append($div)
    }else{
        $div.insertAfter(`#${el}`);
    }

}


// checking username availability #############################################################################################################################
const $chek_username = $('.chek_username')

const checkUsername = async (val) => {
        return await axios.get(`/api/available/username`,{
            params:{username: val}
        }).then( responce => {
            return responce
        }).catch(err => {
            console.log(err)
        });
    }

$chek_username.keyup( async () => {
    let $username = $chek_username.val()
    const $result = await checkUsername($username)
    if($result.data['response']){
        $('.ajax_check').remove()
            noteForUser($('.forms'), `Username: <b>${$username}</b> is already taken`, "append");
    }else{
        $('.ajax_check').remove()
    }
});

//update user's profile ########################################################################################################################################
const basicDataForm = async (form) => {

    // serializing data from form to the json obj
    const $json = $(form).serializeArray().reduce((obj, item) => { obj[item.name] = item.value; return obj; }, {})
    
    // formating images befor sending to the server
    let $data = readFile(document.querySelector('#image'))

    $data.append('json_data', JSON.stringify($json));

    // send data to the server
    return await axios.patch(`/api/update/profile`, $data, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then( responce => {
        return responce
    }).catch(err => {
        console.log(err)
    });
}

$("#update_user_profile").submit(async (e) =>{

    e.preventDefault();
        const $form = e.target
            const $result = await basicDataForm($form)

        // if data updated reload pages to show them
        if($result['data']['response']){
            location.reload();
        }else{
        // if erros happend on the server side handel them
            handelErrors($result['data'])
        }
});

//function to format image before sending to the server
const readFile = (fileField) => {
    let formData = new FormData();
        formData.append('image', fileField.files[0]);
            return formData
}

//function to handel server errors
const handelErrors = (errors) => {
    
    $('.ajax_check').remove()

    Object.keys(errors).map((key) =>{ 
        noteForUser(key, errors[key], 'insert');
    })
        
}


//functions help to confirm user email or phone number ############################################################################################################

//function that will trigger  request to send code to the user email or phone number for confirmation
const askCode = async (url, json) => {

    // send request to the server
    return await axios.post(url,{
        json
    }).then( responce => {
        return responce
    }).catch(err => {
        console.log(err)
    });
    
}

//if user will not receve the code
const releaseFormCodeRequest = (id_el) => {

        $(`#field_code_${id_el}`).toggleClass('fade_field').toggleClass('show_field');
            $(`#${id_el}`).attr('disabled', false);    
                $(`#code_${id_el}`).attr('required', false);
        $('.ajax_check').remove();
    
}


//proccess data to send to the server and receve from the server
const processData = async (el_id, url, json) => {

    // send request to the server, and display new fields
    let $result = await askCode(url, json)

    if($result['data'][el_id]){
        $(`#field_code_${el_id}`).toggleClass('fade_field').toggleClass('show_field')
            $(`#${el_id}`).attr('disabled', true)
                $(`#code_${el_id}`).attr('required', true)
    }

    //if pin or email or phonr number does not match in database notify user
    if($result['data']['code']){
        $(`#code_${el_id}`).val('')
            $(`#field_code_${el_id}`).toggleClass('fade_field').toggleClass('show_field')
                $(`#${el_id}`).attr('disabled', false)
                    $(`#code_${el_id}`).attr('required', false)
    }
        
    //this function will release form for a new PIN rquest in 10 min
    setTimeout(() => {releaseFormCodeRequest(el_id)}, 1000*60*10)
    
    //message for the user
    noteForUser($(`#confirm_user_${el_id}`), $result['data']['message'], "append")

}

//submit email form that will send request to getting the code or to checking the code on the server
$("#confirm_user_email").submit(async (e) =>{

    //privent defaul submitting of the form
    e.preventDefault();

    // get the values
    let $email = $('#email').val()
    let $code_email_val = $("#code_email").val()

    let $json = ''

    if(!$code_email_val.length){  
        $json = {'email': $email}
    }else{
        $json = {'code': $code_email_val, 'email': $email}
    }

    $('.ajax_check').remove();
    processData('email', '/api/request/confirm/email', $json)

});

//submit phone form that will send request to getting the code or to checking the code on the server
$("#confirm_user_phone").submit(async (e) =>{

    //privent defaul submitting of the form
    e.preventDefault();

    // get the button
    let $provider = $('#provider').val()
    let $phone = $('#phone').val()
    let $code_phone_val = $("#code_phone").val()

    let $json = ''

    //get data from the fileds
    if(!$code_phone_val.length){ 
        $json = {'provider': $provider, 'phone': $phone}
    }else{
        $json = {'code': $code_phone_val, 'phone': $phone} 
    }

    $('.ajax_check').remove();
    processData('phone', '/api/request/confirm/phone', $json)

});






