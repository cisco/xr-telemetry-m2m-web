Every file in this subtree that doesn't start with a '!' in the
filename is flattened and served at the root of the web server
hierarchy. So individual filenames must be unique.

This is due to a half-baked idea to try to avoid slashes and be able
to fit into existing web server hierarchies in some super-portable
way. It's not clear yet if there's any win in reality, but this is
what's here right now.

Note that the screen.css file is built at runtime, not checked in.
