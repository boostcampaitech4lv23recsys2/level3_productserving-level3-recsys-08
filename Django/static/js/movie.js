// 영화 선택 버튼 css 변경
window.onscroll = function () {
  let movie_length = $('.infinite-item').length;
  let isLoaded = false;

  if (movie_length == 100) {
    isLoaded = true;
  }

  let scrT = $(window).scrollTop();
  let targetHeight = $(document).height() - $(window).height()
  if ((scrT == targetHeight) && isLoaded) {
    $('.center_button').removeClass('fixed_button');

  } else {
    $('.center_button').addClass('fixed_button');

  }
};

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function submitForm(e) {
  document.documentElement.scrollTop = 0;
  e.preventDefault()
  $(".wrap").hide();
  $('.progress_container').hide();
  $('.progressbar_left').hide();
  $("#loading").show();
  $(".success-checkmark").hide()
  setTimeout(function () {
    $.ajax({
      type: 'GET',
      url: '/test_rec/result_page/',
      data: $('.movie_box').serialize(),
      async: false,
      success: function (response) {
        console.log('ajax 요청 보냄!')
        $("#loading").hide();
        $(".success-checkmark").show();
        $('.result_wrap').hide();
        setTimeout(() => {
          document.querySelector('.movie_box').submit()
        }, 1200)
      },
      error: function (error) {
        setTimeout(() => {
          $('.wrap').innerHTML = `failed to load the data`
        }, 5000)
      }
    })
  }, 2000)

}

// sweet alert
function check(e) {
  e.preventDefault();
  const checkedMovies = $('input[type=checkbox][name=movies]:checked').length
  if (checkedMovies < 3) {
    Swal.fire({ icon: 'info', title: '3개 이상 선택해주세요💧' })
  }
  else {
    submitForm(e)
  }
}
