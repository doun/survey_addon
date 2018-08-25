$(function(){
    $('.question-attach').each(function () {
        var required = $(this).data('required');
        $(this).fileinput({
            showRemove: !required,
            initialPreviewShowDelete: !required
        });
     });
    $('.question-attach').on('filecleared', function (event) { 
        $("input[name='" + event.target.name + "_removed']").val(true);
    });
    $('.question-attach').on('filechanged', function (event) { 
        $();
    });
});