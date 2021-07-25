//disable button on the forms to privent multiple submission by the user ###########################################################################################
//all buttons will released in 1.5 sec
$('form').submit(()=>{
    $('button').attr('disabled', true);
        setTimeout(()=>{$('button').attr('disabled', false)}, 1500);
});



//send request to server to proccess coin for the user ##############################################################################################################
const userCoinsSetRequest = async (action, symbol) => {
    let $json = {'action': action, 'coin_symbol': symbol}
    return await axios.post(`/api/coin/userset`,{
        $json
    }).then( responce => {
        return responce
    }).catch(err => {
        console.log(err)
    });
}


//methods will update user settings for coins in the ui by removing coins from a tracking option #####################################################################

$("#user_coins_to_track").delegate("span.remove-coin", "click", (elm) =>{
    removeCoinFromUIAndProcessCoin(elm)
})

//proccess coin data remove and update ui 
const removeCoinFromUIAndProcessCoin = async (elm) =>{
    let symbol = $(elm.currentTarget).attr("data-symbol-remove")
        let result = await userCoinsSetRequest("DELETE", symbol)
            if(result['data']['response']){
                $(`#${symbol}`).remove()
                sendCoinToMoreCoins(symbol)
            }else{
                alert('Cannot remove coin from your set!')
            }
}


//method builds html elements and integrate coin data 
const sendCoinToMoreCoins = (symbol) => {

    //checking if image exists
    const img = new Image();

    img.src = `static/img/icons/${symbol.toLowerCase()}.png`;
    
    if (img.complete) {
        createMoreCoinsDiv(`static/img/icons/${symbol.toLowerCase()}.png`, symbol)
    } else {
      img.onerror = () => {
        createMoreCoinsDiv(`static/img/icons/default.png`, symbol)
      }
    }
    
}

const createMoreCoinsDiv = (img_path, symbol) => {
    let div = $(`<div class="text-center add_user_coin ${symbol}" style="margin-left:3px">
                    <div class="add-coin-to-user" data-symbol-add="${symbol}">
                        <img src="${img_path}" class="rounded" alt="${symbol}">
                        <p>${symbol}</p>
                    </div>
                </div>`);
    $("#more_coins_to_add").append(div)
}


//methods will add coins to the user set in db and to the ui for a tracking option ###############################################################################

$("#more_coins_to_add").delegate("div.add-coin-to-user", "click", (elm) =>{
    addCoinToUserSet(elm);
})


//proccess coin data add to the db and update ui with a new tracking form
const addCoinToUserSet = async (elm) => {

    // disable click for currant element
    $(elm.currentTarget).prop('disabled', true)
    //get symbol of coin
    let symbol = $(elm.currentTarget).attr("data-symbol-add")
    //send request to the server
    let result = await userCoinsSetRequest("ADD", symbol)

    if(result['data']['response']){
        $(`.${symbol}`).remove()
        $("#user_coins_to_track").append(result['data']['form'])
    }else{
        // enable click for currant element if response from server false
        $(elm.currentTarget).prop('disabled', false)
        alert('Cannot add coins to your set!')
    }
}

//alive methods update prices and percent changes for coins that in the user set #############################################################################

const sendRequestPricePrecent = async () =>{

    return await axios.get(`/api/coins/data/update`,{

    }).then( responce => {
        return responce
    }).catch(err => {
        console.log(err)
    });

}

//methods will update price and precent user's coins
const updatePricePrecent = async () => {
    let result = await sendRequestPricePrecent()

    if(result['data']){
        result['data'].map((el)=>{
            $(`#price_${el['coin_symbol']}`).text(el['coin_price']);
            $(`#coin_change_price_${el['coin_symbol']}`).text(el['coin_change_price']);

            $(`#coin_change_price_${el['coin_symbol']}`).removeClass("coin_change_price_red");
            $(`#coin_change_price_${el['coin_symbol']}`).removeClass("coin_change_price_green");

            (el['coin_change_price'].indexOf("-") > -1)? 
                $(`#coin_change_price_${el['coin_symbol']}`).addClass("coin_change_price_red"): 
                    $(`#coin_change_price_${el['coin_symbol']}`).addClass("coin_change_price_green");
        });
    }
}

// methods will run every 30 seconds to refresh price and percent data user's tracking coins
$().ready(()=>{ 
    setInterval(()=>{updatePricePrecent()}, 1 * 1000 * 30);
});



// send request tracking for the coin #########################################################################################################################

$("#user_coins_to_track").delegate("form.track_options", "submit", (elm) =>{ 
    elm.preventDefault();
        const form = elm.currentTarget
            processTrackingRequest(form) 
});



const processTrackingRequest = async (form) => {

        let btn = $(form).find("input[type=submit]:focus")

        if($(btn).hasClass("deactivated")){
            return false
        }

        const result = await requestTracking(form)

        if(result['data']['response'] && result['data']['tracking']){
            let stop_field = $('<input type="hidden" name="stop_tracking" value="on">')
                $(form).append(stop_field)
                    disableUnableFormElements(form, true)
            switchClassButtons(form)               
        }else if(result['data']['response'] && !result['data']['tracking']){
            let stop_field = $(form).find("input[name=stop_tracking]")
                stop_field.remove()
                    disableUnableFormElements(form, false)
            switchClassButtons(form)
        }
}

const disableUnableFormElements = (form, elm_bool) =>{
    let form_elems = $(form).find("input")
        form_elems.map(i => {

            if($(form_elems[i]).attr('type') != 'submit' && $(form_elems[i]).attr('type') != 'hidden'){
                $(form_elems[i]).attr('disabled', elm_bool);
            }

        });
}

const switchClassButtons = (form) =>{
    let btns = $(form).find("input[type=submit]")
    $(btns[0]).toggleClass("deactivated")
    $(btns[1]).toggleClass("deactivated")
}


const requestTracking = async (form) => {

    // serializing data from form to the json obj
    const json = $(form).serializeArray().reduce((obj, item) => { obj[item.name] = item.value; return obj; }, {})

    //stop processing if user did not choose to track by phone or and email
    if(!json['stop_tracking']){
        if(!json["by_phone"] && !json["by_email"]){
            alert("You have to choose at least one option to track!")
            return {'data':{'response':false}}
        }
        if(!json['goes']){
            alert("You have to choose which direction to track the rate of the coin")
            return {'data':{'response':false}}
        }
    }
    
    return await axios.post(`/api/track/user/coin`,{
        json
    }).then( responce => {
        return responce
    }).catch(err => {
        console.log(err)
    });
}