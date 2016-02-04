/*
 * ============================================================================
 * gpb.js
 *
 * This file contains code pertaining to the `Telemetry GPB` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

var reserved_types = [
    "double", "float", "int32", "int64", "uint32", "uint64", "sint32", "sint64",
    "fixed32", "fixed64", "sfixed32", "sfixed64", "bool", "string", "bytes"
];
var original_message_names = [];

$(function() { // on page load
    $('#gpb_path').blur(function () {
        M2M.path_blur_validate($(this).val()); // alert if potentially invalid path
    }).autocomplete({
        autoFocus: true,
        minLength: 0,
        source: M2M.path_autocomplete_source
    }).keydown(function(event) {
        if (event.keyCode === 13) {
            // Submit if enter is pressed
            $(this).blur();
            $('#gpb_path_button').click();
        }
    });

    $('#gpb_path_button').click(function() {
        if ($('#gpb_path').val() !== '') {
            $('#proto_editor_wrapper').hide();
            $('#gpb_result_wrapper').hide();
            M2M.utils.spinner_on('gpb');
            $(this).closest('.ajax_form').submit();
        }
    });

    $('#proto_editor_wrapper').hide();
    $('#gpb_result_wrapper').hide();
})

// Construct protobuf object given .proto form
function parse_proto_file(proto_file) {
    var protobuf, lines, i;

    if (proto_file.trim() === '') {
        // Happens if e.g. "RootOper" requested
        return {};
    }

    function parse_proto_message() {
        var message;

        function parse_proto_field(line) {
            var sections, field;
            sections = line.split(/\s\s*/); // split on whitespace
            if (sections.length < 7) {
                console.error("Field line not valid");
                return {};
            }
            field = {};
            field.modifier = sections[1];
            if (field.modifier !== "optional" &&
                field.modifier !== "required" &&
                field.modifier !== "repeated") {
                console.warn("Unexpected field modifier: " + field.modifier);
            }
            field.type = sections[2];
            field.name = sections[3];
            field.tag = sections[5];
            if (isNaN(field.tag)) {
                console.warn("Tag is not a number: " + field.tag);
            }
            field.cisco_field = sections[6].substring(0, sections[6].length-1); // exclude ';'
            field.deleted = false;
            return field;
        }

        message = {};

        // Parse name
        message.name = lines[i].split(/\s\s*/)[1];
        i++;

        // Parse header
        message.header = [];
        while (['optional', 'required', 'repeated', '}']
               .indexOf(lines[i].trim().split(/\s\s*/)[0]) === -1) {
            // If not start of field or end of message, add to header
            message.header.push(lines[i]);
            i++;
        }

        // Parse fields
        message.fields = [];
        while (lines[i].indexOf('}') !== 0) {
            // We assume that the message is ended by a line consisting of just a close brace
            if (lines[i].indexOf('}') !== -1) {
                console.warn('Found a closed curly brace in line: if this ' +
                             'was meant to end the message, the parser will fail')
            }
            // Parse field
            message.fields.push(parse_proto_field(lines[i]))
            i++;
        }
        i++; // point to line after end of message
        return message;
    }

    protobuf = {};
    lines = proto_file.split('\n').filter(function(line) {
        var tokens = line.trim().split(/\s\s*/);
        return (tokens.length > 1 || tokens[0] !== "") // line not empty
            && tokens[0].indexOf("//") !== 0; // line not comment
    });
    i = 0;

    // Parse header
    protobuf.header = [];
    while (lines[i].indexOf('message') !== 0) {
        protobuf.header.push(lines[i]);
        i++;
    }

    // Parse messages
    protobuf.messages = [];
    while (lines[i].indexOf('message') === 0) {
        protobuf.messages.push(parse_proto_message());
    }

    // Parse footer
    protobuf.footer = [];
    while (i < lines.length) {
        protobuf.footer.push(lines[i]);
        i++;
    }

    return protobuf
}

// Construct proto editor web form from object
function construct_proto_editor(protobuf) {
    /*
     * "protobuf" has a header, messages, and footer;
     * "header" and "footer" are arrays of lines of text;
     * "messages" is an array of messages;
     * a "message" has a name, header and an array of fields;
     * a "name" is a string and a "header" is an array of lines of text;
     * a "field" has a modifier, type, name, tag, deleted and cisco_field;
     * "modifier"s, "type"s, "name"s and "cisco_field"s are strings;
     * "deleted"s are booleans; and
     * "tags" are integers.
     */
    var $editor = $('#proto_editor'),
        $float_nav;

    if ($.isEmptyObject(protobuf)) {
        // Happens if e.g. "RootOper" requested
        // Message taken from running "telemetry generate gpb-encoding path 'RootOper'" on router
        $editor.html("Schema path has no data. Are you sure it's a leaf node?");
        return;
    }

    function construct_proto_message(message) {
        var $message, $fields;

        function construct_proto_field(field) {
            var $field, $tag;
            // Div for the row
            $field = $('<tr/>').attr({class: 'proto_field'});
            // Modifier
            $('<td/>').html(field.modifier)
                .attr({class: 'proto_modifier'})
                .appendTo($field);
            // Type
            $('<td/>').attr({class: 'proto_type ' + field.type}) // two classes
                .html(field.type)
                .appendTo($field);
            // Name
            $('<td/>').append(
                $('<input/>').attr({
                    type: "text",
                    class: "proto_name",
                    value: field.name
                }).keyup(function() {
                    check_errors_in_message($field.closest(".proto_message"));
                })
            ).appendTo($field);
            // Tag
            $tag = $('<td/>')
                .text('(tag number ')
                .attr({class: 'proto_tag'})
                .appendTo($field);
            // Tag input box
            $('<input/>').attr({
                type: "text",
                size:  2,
                value: field.tag,
                class: "proto_tag_input"
            }).keyup(function() {
                check_errors_in_message($field.closest(".proto_message"));
            }).appendTo($tag);
            $tag.append(')');
            $('<td/>').addClass('delete_button_col')
                      .append($('<input/>').attr({
                    type: 'button',
                    value: 'Delete',
                    class: "proto_delete"
                }).click(function() {
                    // Change css of everything in field
                    if ($(this).val() === "Delete") {
                        $field.addClass('deleted');
                        $(this).val("Undelete");
                    } else {
                        $field.removeClass('deleted');
                        $(this).val("Delete");
                    }
                    // Check if deleting this fields leaves any messages unreachable
                    // but only check if this type is a message name
                    if(original_message_names.indexOf(field.type) !== -1) {
                        delete_unreachable_messages();
                    }
                    check_errors_in_message($field.closest(".proto_message"));
                })
            ).appendTo($field);
            // Cisco field
            $('<td/>').attr({class: 'proto_cisco_field'})
                .hide()
                .html(field.cisco_field)
                .appendTo($field);
            return $field;
        }

        $message = $('<div/>').attr({class: 'proto_message'});
        var $message_name_wrapper = $('<div/>').appendTo($message);
        $('<span/>').attr({class: 'label'})
            .html('Message')
            .appendTo($message_name_wrapper);
        $('<input type="text" />').attr({
            size: '25',
            class: 'proto_message_name',
            id: 'proto_message_' + message.name,
            value: message.name
        }).keyup(function() {
            var msg_name = $(this).attr('value');
            // If a field has this type, update it to the new name
            $('.proto_type.' + msg_name).html($(this).val());
            // Also update the link in the nav bar
            $('.proto_link.' + msg_name).html($(this).val());
            check_errors_in_message($message);
        }).appendTo($message_name_wrapper);
        // Hidden div with message header
        $('<div/>')
            .attr({class: 'proto_message_header'})
            .hide()
            .html(message.header.join('\n'))
            .appendTo($message);
        $fields = $("<table/>").attr({class: 'proto_fields'})
            .appendTo($message);
        message.fields.forEach(function(field) {
            $fields.append(construct_proto_field(field));
        });
        $('<br>').appendTo($message);

        $('<a/>').attr({href: '#proto_message_' + message.name})
            .addClass('proto_link')
            .addClass(message.name)
            .html(message.name)
            .appendTo($gpb_nav_body);
        $('<br>').appendTo($gpb_nav_body);

        return $message;
    }

    $editor.html(''); // clear form

    $float_nav = $('<div>/').attr({id: 'floating_gpb_nav'})
        .appendTo($editor);
    $('<h4/>').html("Message Navigation")
              .click(function() {
                  $gpb_nav_body.toggle();
            }).appendTo($float_nav);
    var $gpb_nav_body = $('<div/>').attr({id: 'gpb_nav_body'})
        .appendTo($float_nav);

    $('<div/>')
        .attr({id: 'proto_header'})
        .hide()
        .html(protobuf.header.join('\n'))
        .appendTo($editor);

    protobuf.messages.forEach(function(message) {
        $editor.append(construct_proto_message(message));
    });
    build_original_messages();

    $('<div/>')
        .attr({id: 'proto_footer'})
        .hide()
        .html(protobuf.footer.join('\n'))
        .appendTo($editor);

    $('<input/>').attr({
        type: 'button',
        value: 'Generate file'
    }).click(function() {
        if($(".editor_err").length > 0) {
            var err_msg = get_err_msg_for_generate();
            alert(err_msg);
        }
        var proto_object = construct_proto_object();
        generate_proto_file(proto_object);
        $('#gpb_result_wrapper').show();
    }).appendTo($float_nav);
}


// Construct object from proto editor web form
function construct_proto_object() {
    // See construct_proto_editor for object description
    var $editor = $('#proto_editor');
    var proto_object = {};

    function construct_message_object($message) {
        var message = {};

        function construct_field_object($field) {
            var field = {};
            field.modifier = $field.find('.proto_modifier').html();
            field.type = $field.find('.proto_type').html();
            field.name = $field.find('.proto_name').val();
            field.tag = $field.find('.proto_tag_input').val();
            field.deleted = $field.find('.proto_delete').val() !== "Delete";
            field.cisco_field = $field.find('.proto_cisco_field').html();
            return field;
        }

        message.name = $message.find('.proto_message_name').val();
        message.fields = [];
        message.deleted = $message.hasClass('deleted');

        // Set header as [] unless there is something in the form
        var header = $message.find('.proto_message_header').text();
        message.header = header ? header.split("\n") : [];

        $message.find('.proto_field').each(function() {
            message.fields.push(construct_field_object($(this)));
        });
        return message;
    }

    proto_object.header = $editor.find('#proto_header').text().split("\n");

    proto_object.messages = [];
    $editor.find('.proto_message').each(function() {
        proto_object.messages.push(construct_message_object($(this)));
    });

    proto_object.footer = $editor.find('#proto_footer').text().split("\n");

    return proto_object;
}

// Given an object, construct proto file and print to gpb_result
function generate_proto_file(proto_object) {
    var header = proto_object.header,
        messages = proto_object.messages,
        footer = proto_object.footer,
        proto_lines = [],
        proto_file;

    function add_message_contents(message) {
        var indent = "    ";
        // Function to form the required string from a field dict
        function generate_field_line(field) {
            var field_parts = [field.modifier, field.type, field.name,
                               "=", field.tag, field.cisco_field];
            return indent + field_parts.join(" ") + ";";
        }

        proto_lines.push.apply(proto_lines, message.header);

        message.fields.forEach(function(field) {
            if(!field.deleted) {
                var field_line = generate_field_line(field);
                proto_lines.push(field_line);
            }
        });
    }

    proto_lines.push.apply(proto_lines, header);
    proto_lines.push("");

    messages.forEach(function(message) {
        if (!message.deleted) {
            var name_line = "message " + message.name + " {";
            proto_lines.push(name_line);
            add_message_contents(message);
            proto_lines.push("}");
            proto_lines.push("");
        }
    });

    proto_lines.push.apply(proto_lines, footer);

    proto_file = proto_lines.join("\n");
    $("#gpb_result").html(proto_file);

    // Add link to result in nav bar if necessary
    var $gen_file_link = $('.gen_file_link');
    if($('.gen_file_link').length === 0) {
        $('<br>').appendTo($("#floating_gpb_nav"));
        $gen_file_link = $('<a/>').attr({href: '#gpb_result_wrapper'})
            .addClass('gen_file_link')
            .html("View generated file")
            .appendTo($("#floating_gpb_nav"));
    }
    // Flash the link, to show the result has been updated
    $gen_file_link.hide().fadeIn();
}

// Check the highlighting is correct, such that duplicates are
// highlighted so long as they are not in a deleted field or message
function highlight_duplicates(reason, $message) {
    // Dictionary to convert the reason given to an array of things to search
    var array_to_check = [[$("#proto_editor"), ".proto_message_name", "err_dup_msg"],
                          [$message, ".proto_tag_input", "err_dup_tag"],
                          [$message, ".proto_name", "err_dup_name"]];
    array_to_check.forEach(function(item) {
        var $search_area = item[0],
            search_class = item[1],
            error_type = item[2];
        highlight_type($search_area, search_class, error_type);
    });

    function colour_element($elem_changed, $search_list, error_type) {
    // Check for any matching elements in the $search_list
    // If none other than itself, ensure not highlighted
        var search_value = $elem_changed.val(),
            matched = 0;
        $search_list.each(function() {
            if ($(this).val() === search_value && !is_deleted($(this))) {
                matched++;
            }
        });
        if (matched < 2) {
            $elem_changed.removeClass('duplicate');
            remove_error_message($elem_changed, error_type);
        } else {
            $elem_changed.addClass('duplicate');
            add_error_message($elem_changed, error_type);
        }
    }

    function highlight_type($search_area, search_class, error_type) {
    // Within a given div, highlight any duplicates among elements
    // of a given class
        var search_list = $search_area.find(search_class);
        // For each deleted element, remove duplication colouring
        // then check for duplicates among non-deleted and colour as required
        search_list.each(function() {
            if( is_deleted($(this)) ) {
                $(this).removeClass('duplicate');
                remove_error_message($(this), error_type);
            } else {
                colour_element($(this), search_list, error_type);
            }
        });
    }

}

// Return true if the field or message the element is within is deleted
function is_deleted($element) {
    if(!$element.hasClass('proto_message_name')) {
        var $field = $element.closest(".proto_field");
        if($field.hasClass('deleted')) {
            return true;
        }
    }
    var $message = $element.closest(".proto_message");
    if($message.hasClass('deleted')) {
        return true;
    }
    return false;
}

// Build list of all original message names, stored globally
function build_original_messages() {
    original_message_names = [];
    $(".proto_message_name").each(function () {
        // The original name is stored in the id: proto_message_original_name
        var name = $(this).attr('value');
        original_message_names.push(name);
    });
}

// Build list of original message names which can be reached from root msg
function build_reachable_messages_set(root_name) {
    var reachable = [root_name],
        current_index = 0;

    // For each reference in the list, add the message it references to
    // the tree as long as the reference is 'live', and the message is not
    // already in the tree
    function add_references($proto_type_list) {
        $proto_type_list.each(function() {
            // If the field is deleted, don't add the reference
            if($(this).parent().hasClass('deleted')) {
                return;
            }
            // Get the type it is referencing
            var classes = $(this).attr("class").toString().split(' '),
                type = classes[1];
            // Only add if this type is possibly a message name, and
            // the message name hasn't already been added
            if(reserved_types.indexOf(type) == -1 && reachable.indexOf(type) == -1) {
                reachable.push(type);
            }
        });
    }
    // Breadth-first search through tree of reachable messages, adding
    // nodes as we go
    while(current_index < reachable.length){
        // Find the message div by searching for the id of name box
        var msg_name = reachable[current_index],
            $current_message = $("#proto_message_" + msg_name).closest(".proto_message");
        // Build a list of all references inside this message
        var references = $current_message.find(".proto_type");
        add_references(references);
       // Now move onto the next in the list
        current_index ++;
    }
    return reachable;
}

// Check which messages can be reached (through references) from root msg,
// delete any which aren't reachable
function delete_unreachable_messages() {
    // Build list of reachable messsages
    var root_name = original_message_names[0],
        reachable = build_reachable_messages_set(root_name);
    original_message_names.forEach(function(msg_name) {
        // Find the message div for this message name
        var $message = $("#proto_message_" + msg_name).closest(".proto_message");
        if(reachable.indexOf(msg_name) == -1) {
            // If it's not reachable then we can delete it
            $message.addClass('deleted');
            $("a." + msg_name).addClass('deleted_msg');
        } else {
            $message.removeClass('deleted');
            $("a." + msg_name).removeClass('deleted_msg');
        }
        // Check that the duplicate highlighting is correct
        check_errors_in_message($message);
    });
}

// Append a span containing an error messsage - the message for each error
// is preset in css
function add_error_message($element, error_class) {
    var $location;
    // If this is a proto message name, then we just take the parent
    // we need to find the field div we are in
    if($element.hasClass("proto_message_name")) {
        $location = $element.parent();
    } else {
        $location = $element.closest(".proto_field");
    }
    var $existing_errors = $location.find("." + error_class);
    console.log($element.val() + " " + $existing_errors.length);
    if($existing_errors.length == 0) {
        $('<span/>').addClass(error_class + " editor_err")
                    .html("")
                    .appendTo($location);
    }
}

// Remove any error messages of a certain class from the field or message
function remove_error_message($element, error_class) {
    var $location;
    // If this is a proto message name, then we just take the parent
    // we need to find the field div we are in
    if($element.hasClass("proto_message_name")) {
        $location = $element.parent();
    } else {
        $location = $element.closest(".proto_field");
    }
    var $existing_errors = $location.find("." + error_class);
    $existing_errors.remove();
}

function check_errors_in_message($message) {
    // Checks that only valid characters are used
    function check_valid_characters($this) {
        if (!is_deleted($this) && !/^(\w+)$/.test($this.val())) {
            $this.addClass('invalid_identifier');
            add_error_message($this, "err_invalid");
        } else {
            $this.removeClass('invalid_identifier');
            remove_error_message($this, "err_invalid");
        }
    }

    // Checks that name is not one of the reserved types
    function check_not_forbbiden($this) {
        if (!is_deleted($this) && reserved_types.indexOf($this.val()) !== -1) {
            $this.addClass('forbidden_name');
            add_error_message($this, "err_forbidden");
        } else {
            $this.removeClass('forbidden_name');
            remove_error_message($this, "err_forbidden");
        }
    }

    // Checks that tag is a number
    function check_valid_tag($this) {
        if (!is_deleted($this) && /\D/.test($this.val())) {
            $this.addClass('tag_not_number');
            add_error_message($this, "err_tag");
        } else {
            $this.removeClass('tag_not_number');
            remove_error_message($this, "err_tag");
        }
    }
    var $msg_name = $message.find(".proto_message_name");
    check_not_forbbiden($msg_name);
    check_valid_characters($msg_name);

    $message.find(".proto_field").each(function() {
        var $name = $(this).find(".proto_name"),
            $tag = $(this).find(".proto_tag_input");
        check_valid_characters($name);
        check_valid_tag($tag);
    });
    highlight_duplicates("msg_state_change", $message);
    highlight_errors_in_nav();
}

function get_err_msg_for_generate() {
    var err_msg = "There may be errors in this .proto file\n\n";

    var err_msg_dict = {
        '.err_dup_msg' : "Message names must be unique",
        '.err_dup_tag' : "Tags must be unique within messages",
        '.err_dup_name' : "Names must be unique within messages",
        '.err_tag' : "Tags must be positive integers",
        '.err_invalid' : "Names must contain only letters, numbers and underscores",
        '.err_forbidden' : "Message names are not reserved, e.g. 'string'"
    };
    var err_classes = ['.err_dup_msg', '.err_dup_tag', '.err_dup_name',
                       '.err_tag', '.err_invalid', '.err_forbidden'];
    err_classes.forEach(function(err_class) {
        if($(err_class).length > 0) {
            err_msg += "- " + err_msg_dict[err_class] + "\n";
        }
    });
    return err_msg;
}

// Check all messages, and highlight link in nav red if errors in message
function highlight_errors_in_nav() {
    var $msg_divs = $("#proto_editor").find(".proto_message");
    // For each div, check for any errors, and change classes of link
    $msg_divs.each(function() {
        var num_err_msgs = $(this).find(".editor_err").length,
            msg_name = $(this).find(".proto_message_name").attr("value"),
            $link = $("a." + msg_name);
        if(num_err_msgs == 0) {
            $link.removeClass('msg_with_err');
        } else {
            $link.addClass('msg_with_err');
        }
    });
}

M2M.build_proto_editor = function(proto_file) {
    construct_proto_editor(parse_proto_file(proto_file));
};

}) (M2M, jQuery);
