var path = require('path');

module.exports = function(grunt) {
    require('load-grunt-tasks')(grunt);

    grunt.initConfig({
        watch: {
            scripts: {
                files: ['addon/**'],
                tasks: ['sync']
            },
        },
        sync: {
            main: {
                files: [{
                    cwd: 'addon',
                    src: ['**'],
                    dest: path.join(process.env['HOME'], '/AppData/Roaming/Kodi/addons/script.imdbupdate')
                }],
                verbose: true
            }
        }
    });
};