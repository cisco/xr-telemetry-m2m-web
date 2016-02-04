/*
 * ============================================================================
 * write_file.js
 *
 * This file contains code pertaining to the `Write File` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

// An object to hold the pre-written example files. These are keyed using a
// url hash.
var files = {}

//
// Load a pre-written file from src/assets/policies into the page.
//
function get_contents_from_preloaded_file(filename) {
    var file_path_box = document.getElementById('file_path_box'),
        contents_box = document.getElementById('file_contents');
    contents_box.value = files[filename];
    file_path_box.value = '/disk0/usr/' + filename;
}

// Bind event handlers for the file loaders on page load.
$(function () {
    // Load up the files
    $.get('policies', {}, function (s) {
        console.log('got files:' + JSON.stringify(Object.keys(s)));
        for (var filename in s) {
            files[filename] = s[filename];
        }
    });

    $('.file_loader ul').each(function () {
        $(this).on('click', 'a', function (e) {
            var filename = this.href.split('#')[1];
            console.log(filename);
            get_contents_from_preloaded_file(filename);
            e.preventDefault();
        });
    });
});

// Load the contents of any chosen text file into the page.
function get_contents_from_uploaded_file() {
    // Load file
    var input = document.getElementById('file_upload'),
        file = input.files[0],
        file_name = file.name,
        file_path_box,
        reader;
    console.log('Loading file: ' + file_name);

    // Load name and contents of file into the page
    file_path_box = document.getElementById('file_path_box');
    // Default destination is /disk0/usr/
    file_path_box.value = '/disk0/usr/' + file_name;
    reader = new FileReader();
    reader.onload = function(){
        var file_contents = reader.result,
            contents_box = document.getElementById('file_contents');
        contents_box.value = file_contents;
    };
    reader.readAsText(file);
}

M2M.get_contents_from_uploaded_file = get_contents_from_uploaded_file;

})(M2M, jQuery);
