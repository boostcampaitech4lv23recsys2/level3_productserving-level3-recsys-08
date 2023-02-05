
$(window).scroll(function () {
  const docHeight = document.documentElement.scrollHeight;
  const winHeight = $(window).height();
  const finalHeight = docHeight - winHeight;
  // console.log('here', $(window).scrollTop() + $(window).height())
  // console.log('here2:', $(document).height())
  if ($(window).scrollTop() + $(window).height() >= $(document).height()-100) {
    $('footer').css({ 'bottom': `-${finalHeight}px` });
    $('footer').css({ 'display': 'flex' });

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