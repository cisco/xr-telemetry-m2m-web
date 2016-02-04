/*
 * ============================================================================
 * telemetry.js
 *
 * This file contains code pertaining to the `Telemetry Policy` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

// An object to hold the pre-written example policies. These are keyed using a
// url hash.
var policies = {}

// Load a pre-written policy from src/assets/policies into the page.
function get_contents_from_preloaded_policy(policy) {
    // Get contents from the policies object filled on page load
    var contents = policies[policy];
    // Fill in the policy name and contents
    $('#telemetry_policy_name_box').val(policy);
    $('#telemetry_policy_contents').val(contents);
    clear_builder();
    fill_builder_from_contents_box();
}

// Load the contents of any chosen text file into the page.
function get_contents_from_uploaded_policy() {
    // load file
    var input = $('#telemetry_policy_upload')[0],
        file = input.files[0],
        policy_name = file.name,
        reader;
    console.log('Loading file: ' + policy_name);

    // Load name and contents of policy into the page
    $('#telemetry_policy_name_box').val(policy_name);
    reader = new FileReader();
    reader.onload = function(){
        var policy_contents = reader.result;
        $('#telemetry_policy_contents').val(policy_contents);
        clear_builder();
        fill_builder_from_contents_box();
    };
    reader.readAsText(file);
}

// Bind event handlers for the policy loaders on page load.
$(function () {
    // Load up the policies
    $.get('policies', {}, function (s) {
        console.log('got policies:' + JSON.stringify(Object.keys(s)));
        for (var policy in s) {
            policies[policy] = s[policy];
        }
    });

    $('.policy_loader ul').each(function () {
        $(this).on('click', 'a', function (e) {
            var policy = this.href.split('#')[1];
            console.log(policy);
            get_contents_from_preloaded_policy(policy);
            e.preventDefault();
        });
    });

    // Add initial group of paths
    add_new_group_input();
    
    // Set active path box to be the first one; expose it so the explorer can know which it is
    M2M.$active_path_box = $('#policy_builder').find('.path_input').first();
});

// Function to create a policy from the builder, and add to the contents box
function get_contents_from_builder() {
    var built_policy,
        name = $('#builder_name').val(),
        version = $('#builder_version').val(),
        description = $('#builder_description').val(),
        comment = $('#builder_comment').val(),
        identifier = $('#builder_identifier').val(),
        $groups_array,
        $paths_array,
        metadata_dict = {},
        collections_dict = {},
        groups_dict = {},
        full_dict = {};

    full_dict["Name"] = name;
    
    // Add metadata to metadata_dict if entered
    if(version) { metadata_dict["Version"] = version; }
    if(description) { metadata_dict["Description"] = description; }
    if(comment) { metadata_dict["Comment"] = comment; }
    if(identifier) { metadata_dict["Identifier"] = identifier; }
    
    // Add metadata dictionary to the overall dictionary
    full_dict["Metadata"] = metadata_dict;

    // Search for all groups, and add the appropriate dictionary for each
    $groups_array = $(".group");
    for(var i=0; i<$groups_array.length; i++) {
        var $group_div = $groups_array.eq(i),
            $paths_div = $group_div.find(".paths"),
            group_dict = {},
            path_name_array = [];
        // Find group_name and period by looking for elements with classes given
        var group_name = $group_div.find(".group_name")[0].value,
            period = $group_div.find(".period")[0].value;
        period = parseInt(period);

        group_dict["Period"] = period;
        // Look through all paths associated with this group
        // and add each non-zero value to the path_name_array
        $paths_array = $paths_div.find(".path_input");
        for(var j=0; j<$paths_array.length; j++) {
            var value = $paths_array[j].value;
            if(value) {
                path_name_array.push(value);
            }
        } 
        group_dict["Paths"] = path_name_array;
       
        // Only add the group if at least one path was entered
        if(Object.keys(path_name_array).length) {
            collections_dict[group_name] = group_dict;
        }
    }
    full_dict["CollectionGroups"] = collections_dict;

    built_policy = JSON.stringify(full_dict, null, 2);
    $('#telemetry_policy_contents').val(built_policy);
    $('#telemetry_policy_name_box').val(name + '.policy');
}

// Parse the contents of the box and populate the builder fields if possible
function fill_builder_from_contents_box() {
    var contents,
        policy_dict,
        builder_fields = [],
        num_groups_in_builder,
        groups_dict,
        group_names,
        paths_array,
        builder_boxes = [];
        
    contents = $("#telemetry_policy_contents").val();
    
    // Try to convert to JSON, if this fails then stop here
    try {
        policy_dict = JSON.parse(contents);
    }
    catch(err) {
        return
    }
    
    // Populate the array of fields we want to add to builder boxes
    builder_fields.push(policy_dict["Name"]);
    // Don't attempt to use the Metadata dictionary if it is null
    if(policy_dict["Metadata"]) {
        builder_fields.push(policy_dict["Metadata"]["Version"]);
        builder_fields.push(policy_dict["Metadata"]["Description"]);
        builder_fields.push(policy_dict["Metadata"]["Comment"]);
        builder_fields.push(policy_dict["Metadata"]["Identifier"]);
    }

    groups_dict = policy_dict["CollectionGroups"];
    // To avoid error, ensure that group_names is correct type
    if(typeof groups_dict !== 'object') {
        groups_dict = {};
    }
    num_groups_in_builder = $(".group").length;
    group_names = Object.keys(groups_dict);
    // For each group, add the fields to the array
    // and add an extra group div or path inputs if necessary
    for(var i=0; i<group_names.length; i++) {
        var this_group_name = group_names[i],
            this_group_dict = groups_dict[this_group_name],
            this_group_div,
            num_paths_in_div;

        paths_array = this_group_dict["Paths"];
        // Add the fields from this group to the array
        builder_fields.push(this_group_name);
        builder_fields.push(this_group_dict["Period"]);
        
        // Add an extra group section to builder if necessary
        if(i >= num_groups_in_builder) {
            add_new_group_input();
        }
        
        // for each path input box in the div, remove if empty
        // and else store value
        this_group_div = $(".group").eq(i);
        this_group_div.find('.path_input').each(function(index) {
            var trimmed_value = $.trim($(this).val());
            if (trimmed_value === "") {
                // Remove this path box
                $(this).siblings('.remove_path_button').click();
            } else if ($.inArray(trimmed_value, paths_array) === -1) {
                // If the value is not already in the paths_array, add
                paths_array.push(trimmed_value);
            }
        });
        // Now add all the paths to the array of fields
        for(var j=0; j<paths_array.length; j++) {
            builder_fields.push(paths_array[j]);
        }
        
        // count path inputs in the group div, and add more if needed
        num_paths_in_div = (this_group_div.find(".path_input")).length;
        while(paths_array.length > num_paths_in_div) {
            this_group_div.find(".new_path_button").click();
            num_paths_in_div += 1;
        }
    }

    // Populate the list of boxes to write to
    builder_boxes = $("#policy_builder :text");

    for(var i=0; i<builder_fields.length; i++) {
        var field = builder_fields[i],
            box = builder_boxes[i];
        // Only fill in the value if it is defined
        if(field) {
            box.value = field;
        }
    }
}

// function to add extra input for a new group
function add_new_group_input() {
    var policy_builder_div,
        new_group_div,
        paths_div;

    //Create a new group div, and append to policy_builder
    new_group_div = $("<div/>").attr({class: 'group'});
    new_group_div.appendTo($('#policy_builder'));

    $('<br>').appendTo(new_group_div);

    // Add Group name label and input box to new_group_div
    $("<span/>").attr({class:"right_top_aligned label"})
        .html("Group name:")
        .appendTo(new_group_div);
    $('<input type="text" />').attr({
        size: '30',
        class: 'group_name'
    }).appendTo(new_group_div);

    // Add period label and input box to new_group_div
    $("<span/>").attr({class:"label"})
        .html("Period:")
        .appendTo(new_group_div);
    $('<input type="text" />').attr({
        size: '10',
        class: 'period'
    }).appendTo(new_group_div);

    $('<button type="button" />')
        .html("Remove group")
        .click(function() {new_group_div.remove();})
        .appendTo(new_group_div);

    var paths_wrapper_div = $('<div/>')
        .attr({class: "paths_wrapper"})
        .appendTo(new_group_div);

    // Add label for div containing all the paths
    $("<span/>").attr({class:"right_top_aligned label"})
        .html("Paths:")
        .appendTo(paths_wrapper_div);

    // Create div to hold all paths, and append to new_group_div
    paths_div = $('<div />').attr({class: 'paths'}).appendTo(paths_wrapper_div);

    add_new_path_input(new_group_div);
}

// Add a new path input field and a button to remove it, to the specified group div
function add_new_path_input($group) {
    var $main_path_div = $group.find(".paths"),
        $path_div,
        $path_box,
        $remove_path,
        $add_path;

    $path_box = $('<input>')
        .attr({
            class: 'path_input',
            type: 'text',
            size: '60'})
        .click(function() {
            M2M.$active_path_box = $path_box; // Make this box the active one on click
        })
        .blur(function () {
            M2M.path_blur_validate($path_box.val()); // alert if potentially invalid path
        })
        .autocomplete({
            autoFocus: true,
            minLength: 0,
            source: M2M.path_autocomplete_source
        });

    function new_add_path_button() {
        return $('<button type="button" />')
                    .attr({class: 'new_path_button'})
                    .html("+")
                    .click(function() {
                        add_new_path_input($(this).closest('.group'));
                        $(this).remove();
                    });
    }

    $remove_path = $('<button type="button" />')
                    .attr({class: 'remove_path_button'})
                    .html("-")
                    .click(function() {
                        if ($remove_path.siblings('.new_path_button').size() > 0) {
                            // Need to transfer plus button to next box up
                            if ($remove_path.closest('.paths').children().size() === 1) {
                                // This is the last path box; add "+" button to paths div
                                $remove_path.closest('.paths').append(new_add_path_button());
                            } else {
                                // Transfer the "+" button to the previous path box
                                $path_div.prev().append(new_add_path_button());
                            }
                        }
                        $path_div.remove();
                    });

    $add_path = new_add_path_button();

    // Add input field and buttons inside a div
    $path_div = $('<div />').append($path_box, $remove_path, $add_path);

    $main_path_div.append($path_div); // Add the new path div to the path container
    M2M.$active_path_box = $path_box; // Make this box the active one now
}

// Function to use as jQuery autocomplete source for path autocomplete
function path_autocomplete(request, response) {
    var paths, num_term_sections, filtered_paths, parent;
    // Get cached paths
    paths = M2M.get_cached_paths();
    num_term_sections = request.term.split(".").length;
    // Get rid of unwanted ones (either because don't match or too long)
    filtered_paths = paths.filter(function(path) {
        // Sorry that this is one statement, but short circuit for efficiency
        return path.indexOf(request.term) === 0 // only include results that actually match!
                && (path.split(".").length === num_term_sections // either same num sections as term
                    || (path.indexOf(request.term + ".") === 0 // or path is {term}.something
                        && path.split(".").length === num_term_sections + 1)); // (not {term}.something.somethingelse)
    });
    // Ask for the children to be brought into the cache
    parent = request.term.substring(0, request.term.lastIndexOf('.'));
    if (parent.length > 0) {
        M2M.add_children_to_cache(parent);
    }
    // Give back list of suggestions, sorted
    response(filtered_paths.sort(M2M.order_paths));
}

// Function to use for validation on blur of path boxes
function path_blur_validate(path) { // Warns if invalid - may give false negatives
    if (path !== "" && M2M.get_cached_paths().indexOf(path) === -1) {
        M2M.add_children_to_cache(path); // if path not in cache, ask to bring it in
        window.setTimeout(function() { // if after 2s it still isn't in cache, alert user
            if (path !== "" && M2M.get_cached_paths().indexOf(path) === -1) {
                alert("The path \"" + path + "\" is probably not valid - please double check");
            }
        }, 2000); // it's hacky but better than nothing
    }
}

// Clear all builder input boxes, and delete all group divs
function clear_builder() {
    // Set all input textboxes to have value ""
    $('#policy_builder').find(':text').val("");
    // Remove extra paths and groups
    cleanup_policy_form(); 
}

// Remove all empty path boxes, then all empty groups from policy web form
function cleanup_policy_form () {
    // For each group in the policy form
    $('#policy_builder').children('.group').each(function(index) {
        // For each path box in that group
        $(this).find('.path_input').each(function(jndex) {
            if ($.trim($(this).val()) === "") {
                // Remove the div containing this box if empty
                $(this).siblings('.remove_path_button').click();
            }
        })
        // If the group now contains no path boxes, then remove it
        if (($(this).find('.path_input')).length === 0) {
            $(this).remove();
        }
    });
}

M2M.get_contents_from_builder = get_contents_from_builder;
M2M.add_new_group_input = add_new_group_input;
M2M.add_new_path_input = add_new_path_input;
M2M.get_contents_from_uploaded_policy = get_contents_from_uploaded_policy;
M2M.fill_builder = fill_builder_from_contents_box;
M2M.path_autocomplete_source = path_autocomplete;
M2M.path_blur_validate = path_blur_validate;

})(M2M, jQuery);
