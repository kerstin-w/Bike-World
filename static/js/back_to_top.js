// Code Inspiration found here: https://mdbootstrap.com/docs/standard/extended/back-to-top/

// Get the button element
const mybutton = $('#btn-back-to-top');

// Show the button when the user scrolls down 20px from the top of the document
$(window).scroll(function () {
    if ($(this).scrollTop() > 20) {
        mybutton.show();
    } else {
        mybutton.hide();
    }
});

// Scroll to the top of the document when the user clicks the button
mybutton.click(function () {
    $("html, body").animate({
        scrollTop: 0
    }, 50);
});