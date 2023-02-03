
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