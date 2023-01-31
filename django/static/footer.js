
$(window).scroll(function () {
  // console.log('scrollTop : ', $(window).scrollTop())
  // console.log('window height : ',$(window).height())
  // console.log('document height : ', $(document).height())

  if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
    console.log('끝')
    $('footer').css({ 'bottom': '-3000px' });
    $('footer').css({ 'display': 'flex' });

  } else {
    console.log('스크롤')
    $('footer').css({ 'bottom': '-3000px' });
    $('footer').css({ 'display': 'none' });

  }
});

// window.addEventListener("scroll", function () {
//   var footer = document.querySelector("footer");
//   var windowHeight = window.innerHeight;
//   var body = document.body;
//   var html = document.documentElement;
//   var docHeight = Math.max(body.scrollHeight, body.offsetHeight,
//     html.clientHeight, html.scrollHeight, html.offsetHeight);
//   console.log(window.pageYOffset + windowHeight)
//   console.log(docHeight - footer.offsetHeight)
//   console.log('------------------------------------')
//   if (window.pageYOffset + windowHeight >= docHeight - footer.offsetHeight) {
//     footer.style.bottom = 0 + "px";
//   } else {
//     footer.style.bottom = -footer.offsetHeight + "px";
//   }
// });