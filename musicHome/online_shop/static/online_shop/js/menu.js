document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("page_main").addEventListener('click', function() {
        document.location.href = "../home/";
    }, true)
    document.getElementById("enter").addEventListener('click', function() {
        document.location.href = "../log_in/";
    }, true)
    document.getElementById("reg").addEventListener('click', function() {
        document.location.href = "../registrate/";
    }, true)
    /*document.getElementById("page_help").addEventListener('click', function() {
        document.location.href = "../help/";
    }, true)*/
    /*document.getElementById("page_delivery").addEventListener('click', function() {
        document.location.href = "../delivery/";
    }, true)*/
    /*document.getElementById("search").addEventListener('click', function() {
        document.location.href = "../search/";
    }, true)*/
}, true)