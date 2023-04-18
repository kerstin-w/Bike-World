$(document).ready(function () {
    // Select the buttons
    let collapseInfoBtn = $('#collapseInfoBtn');
    let collapseHistoryBtn = $('#collapseHistoryBtn');

    // Add a click event listener to the collapse info button
    collapseInfoBtn.on('click', function () {
        // Select the collapse history container
        let collapseHistory = $('#collapseHistory');
        // Check if the collapse history container has the 'show' class
        if (collapseHistory.hasClass('show')) {
            // If it does, remove the class to hide the container
            collapseHistory.removeClass('show');
        }
    });

    // Add a click event listener to the collapse history button
    collapseHistoryBtn.on('click', function () {
        // Select the collapse info container
        let collapseInfo = $('#collapseInfo');
        // Check if the collapse info container has the 'show' class
        if (collapseInfo.hasClass('show')) {
            // If it does, remove the class to hide the container
            collapseInfo.removeClass('show');
        }
    });
});