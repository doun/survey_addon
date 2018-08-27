(function ($) {
    var originalVal = $.fn.val;
    $.fn.val = function () {
        var result = originalVal.apply(this, arguments);
        if (arguments.length > 0)
            $(this).trigger('value-changed');
        return result;
    };
})(jQuery);

odoo.define("survey_addon.attach", function (require) {
    require('survey.survey');

    function set_fileinput(ele) {
        var required = $(ele).data('required');
        var image_only = $(ele).data('image_only');
        var tag = $(ele).data('tag');
        var ext = $(ele).data('file_ext')
        if (ext) {
            ext = ext.split(',');
            if (ext.length == 0) ext = null;
        }
        var value = $("input[name='" + tag + "']").val();
        $(ele).fileinput({
            showRemove: !required,
            showCaption: false,
            language: 'zh',
            dropZoneEnabled: false,
            allowedFileTypes: image_only ? ['image'] : null,
            allowedFileExtensions: ext,
            initialPreviewShowDelete: false,
            initialPreview: [
                value > 0 ? "<img class='kv-preview-data file-preview-image' alt='img' title='img' src='/web/image/"
                    + value + "'>" : '',
            ],
            showUpload: false,
        });
        $(ele).on('filebeforedelete', function(event, key, data) {
            event.cancel();
            console.log('Key = ' + key);
        });
    }

    function set_initial_img() {
        $('.o-attach-value').on('value-changed', function () {
            set_fileinput($("input[name='file_" + this.name + "']").fileinput('destroy'));
        });
    }

    function init_input() {
        $('.question-attach').each(function () {
            var required = $(this).data('required') === 'True';
            var image_only = $(this).data('image_only') === 'True';
            $(this).data('image_only', image_only);
            $(this).data('required', required);
            set_fileinput(this);
        });
    }
    init_input();
    set_initial_img();
});