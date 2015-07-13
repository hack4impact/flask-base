// Semantic UI breakpoints
var mobileBreakpoint = '768px';
var tabletBreakpoint = '992px';
var smallMonitorBreakpoint = '1200px';

$(document).ready(function () {

    // Enable dismissable flash messages
    $('.message .close').on('click', function () {
        $(this).closest('.message').transition('fade');
    });

    // Enable mobile navigation
    $('#open-nav').on('click', function () {
        $('.mobile.only .vertical.menu').transition('slide down');
    });

    // Enable sortable tables
    $('table.ui.sortable').tablesort();

    // Enable dropdowns
    $('.dropdown').dropdown();
    $('select').dropdown();
});


// Add a case-insensitive version of jQuery :contains pseduo
// Used in table filtering
(function ($) {
    function icontains(elem, text) {
        return (elem.textContent || elem.innerText || $(elem).text() || "")
                .toLowerCase().indexOf((text || "").toLowerCase()) > -1;
    }

    $.expr[':'].icontains = $.expr.createPseudo ?
        $.expr.createPseudo(function (text) {
            return function (elem) {
                return icontains(elem, text);
            };
        }) :
        function (elem, i, match) {
            return icontains(elem, match[3]);
        };
})(jQuery);

