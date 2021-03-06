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
    var last_event = null;
    function set_fileinput(ele) {
        var required = $(ele).data('required');
        var image_only = $(ele).data('image_only');
        var tag = $(ele).data('tag');
        var ext = $(ele).data('file_ext')
        if (ext) {
            ext = ext.split(',');
            if (ext.length == 0) ext = null;
        }
        var value = $("input[name='" + tag + "']").val() - 0;
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
            initialPreviewConfig: [
                { url: "/site/file-delete", key: 1 }
            ],
            showUpload: false,
        }).on('filebeforedelete', function (event) {
            if (last_event != event) {
                last_event = event;
                return false;
            }
            if (required) {
                window.alert('必填字段，不允许删除');
            }
            var confirmed = window.confirm('确认删除?');
            if (confirmed) {
                $("input[name='" + tag + "']").val('remove');
                return true;
            }
        }).on('filepredelete', function (event, key, jqXHR, data) {
            if(last_event != event){
                last_event = event;
                return false;
            }
            jqXHR.abort();
            
            arguments[4].success.apply(this);
            return false;
        });
    }

    function set_initial_img() {
        $('.o-attach-value').on('value-changed', function () {
            if ($(this).val() != 'remove') {
                var ele = $("input[name='file_" + this.name + "']");
                ele.fileinput('destroy');
                set_fileinput(ele);
            }
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