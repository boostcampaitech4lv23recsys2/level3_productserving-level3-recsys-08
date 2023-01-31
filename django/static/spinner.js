function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

loading = async () =>{
    
    $(".wrap").hide();
    $("#loading").show();
    $(".success-checkmark").hide()
    $.ajax({
        type:'POST',
        url:'/test_rec/result_page',
        success: function(response){
           
            setTimeout(() => {
                
                $("#loading").hide();
                $(".success-checkmark").show();
            }, 700)
            setTimeout(() => {
                $(".success-checkmark").hide();
                $('#data_box').show()
            }, 1600)
        },
        error: function(error){
            setTimeout(() => {
                spinnerBox.classList.add('not_visible')
                dataBox.innerHTML = `failed to load the data`
            }, 5000)
        }
    })
    await sleep(1600);
}

