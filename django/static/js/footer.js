
$(window).scroll(function () {
  // console.log($('.wrap').outerHeight(true))
  // console.log(document.documentElement.scrollHeight)
  const docHeight = document.documentElement.scrollHeight;
  const winHeight = $(window).height();
  // const finalHeight = $('.wrap').outerHeight(true) - ($(window).height() * 0.9);
  const finalHeight = docHeight - winHeight
  // console.log(finalHeight)
  if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
    $('footer').css({ 'bottom': `-${finalHeight}px` });
    $('footer').css({ 'display': 'block' });

  } else {
    // $('footer').css({ 'bottom': `-${outerHeight}px` });
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