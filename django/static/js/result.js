function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// Spinner
// const loading = async () => {
//     console.log('Spinner')

//     // $(".wrap").hide();
//     // $("#loading").show();
//     // $(".success-checkmark").hide()
//     $.ajax({
//         type: 'POST',
//         url: '/test_rec/result_page',
//         beforeSend: function(request){
//             setTimeout(() => {
//                 $(".result_wrap").hide();
//             $("#loading").show();
//             $(".success-checkmark").hide()
//             }, 1500)
            
//             setTimeout(() => {

//                 $("#loading").hide();
//                 $(".success-checkmark").show();
//             }, 2100)

//             setTimeout(() => {
//                 $(".success-checkmark").hide();
//                 // $('#data_box').show()
//             }, 3000)
//         },
//         success: function (response) {

//             setTimeout(() => {

//                 $("#loading").hide();
//                 $(".success-checkmark").show();
//             }, 2100)
//             setTimeout(() => {
//                 $(".success-checkmark").hide();
//                 $('#data_box').show()
//             }, 3000)
//         },
//         error: function (error) {
//             setTimeout(() => {
//                 spinnerBox.classList.add('not_visible')
//                 dataBox.innerHTML = `failed to load the data`
//             }, 5000)
//         }
//     })
//     await sleep(3000);

// }


//   dataCharacters = $('#data1').attr('data-characters')
//   dataCharacters2 = $('#data2').attr('data-characters2')
//   // console.log('dataCharacters : ', dataCharacters)
//   // console.log('dataCharacters2 : ', dataCharacters2)

//   $(document).on('click', '.character_card', function(){
//     sessionStorage.setItem('data1', dataCharacters);
//     sessionStorage.setItem('data2', dataCharacters2)
//   })

//   window.onpageshow = function(event) {
		
//     $.ajax({
//       type:'POST',
//       url:'/test_rec/result_page',
//       data:{
//         'data1':sessionStorage.getItem('data1'), 
//         'data2':sessionStorage.getItem('data2')
//       },
//       success: function(){
//         console.log('성공1')
//       },
//       error:function(){
//         console.log('실패')
//       }
//     })

//   }
	

// $(document).on('click', '.retest_button', function(){
//     $.ajax({
//       type:'POST',
//       url:'/test_rec/result_page',
//       data:{
//         'data1':sessionStorage.getItem('data1'), 
//         'data2':sessionStorage.getItem('data2')
//       },
//       success: function(){
//         console.log('성공!!1')
//       },
//       error:function(){
//         console.log('실패')
//       }
//     })

//   })
//   $(document).on('click', '.result_button', function(){
//     $.ajax({
//       type:'POST',
//       url:'/test_rec/result_page',
//       data:{
//         'data1':sessionStorage.getItem('data1'), 
//         'data2':sessionStorage.getItem('data2')
//       },
//       success: function(){
//         console.log('성공!!1')
//       },
//       error:function(){
//         console.log('실패')
//       }
//     })
//   })