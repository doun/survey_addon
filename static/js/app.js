odoo.define("survey_addon.attach", function (require) {
    require('survey.survey');
    function set_initial_img() {
        $('.o-attach-value').each(function () {
            $(this).change(function(){
                
            });
        });
    }
    function init_input() {
        $('.question-attach').each(function () {
            var required = $(this).data('required');
            var image_only = $(this).data('iimage_only') === 'True';
            $(this).fileinput({
                //TODO: Preview窗口大小处理
                showRemove: !required,
                initialPreviewShowDelete: false,
                showCaption: false,
                language: 'zh',
                dropZoneEnabled: false,
                allowedFileTypes: image_only ? ['image'] : null,
                showUpload: false

            });
            $('.question-attach').on('filecleared', function (event) {
                $("input[name='" + event.target.name + "_removed']").val(true);
            });
            $('.question-attach').on('filechanged', function (event) {
                $("input[name='" + event.target.name + "_removed']").val(false);
            });
        });
    }
    init_input();
    set_initial_img();
});
