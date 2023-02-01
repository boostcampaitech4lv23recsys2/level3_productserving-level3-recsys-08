// 영화 선택 버튼 css 변경
window.onscroll = function () {
  let movie_length = $('.infinite-item').length;
  let isLoaded = false;

  if (movie_length == 100) {
    isLoaded = true;
  }
  let scrT = $(window).scrollTop();
  if (scrT == $(document).height() - $(window).height() && isLoaded) {
    $('.center_button').removeClass('fixed_button');

  } else {
    $('.center_button').addClass('fixed_button');

  }
};

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}


const loading = async () => {
  console.log('Spinner')

  $(".wrap").hide();
  $("#loading").show();
  $(".success-checkmark").hide()
  $.ajax({
    type: 'POST',
    url: '/test_rec/result_page',
    success: function (response) {

      setTimeout(() => {

        $("#loading").hide();
        $(".success-checkmark").show();
      }, 2100)
      setTimeout(() => {
        $(".success-checkmark").hide();
        $('#data_box').show()
      }, 3000)
    },
    error: function (error) {
      setTimeout(() => {
        spinnerBox.classList.add('not_visible')
        dataBox.innerHTML = `failed to load the data`
      }, 5000)
    }
  })
  await sleep(3000);

}

async function submitForm(e) {
  e.preventDefault();
  await loading();
  document.querySelector('.movie_box').submit()
}

function check(e) {
  e.preventDefault();
  const checkedMovies = $('input[type=checkbox][name=movies]:checked').length
  if (checkedMovies < 5) {
    Swal.fire({ icon: 'info', title: '5개 이상 선택해주세요💧' })
  }
  else {
    submitForm(e)
  }
}



