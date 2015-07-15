var path = require('path')
    loadTasks = require('load-grunt-tasks')

module.exports = function(grunt) {
    loadTasks(grunt)

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            scripts: {
                files: ['script.imdbupdate/**'],
                tasks: ['sync']
            },
        },
        sync: {
            main: {
                files: [{
                    cwd: 'script.imdbupdate',
                    src: ['**'],
                    dest: path.join(process.env['HOME'], '/AppData/Roaming/Kodi/addons/<%= pkg.name %>')
                }],
                verbose: true
            }
        },
        compress: {
            build: {
                options: {
                    archive: 'build/<%= pkg.name %>-<%= pkg.version %>.zip'
                },
                files: [{
                    cwd: '',
                    src: ['script.imdbupdate/**'],
                    expand: true
                }]
            }
        },
        xmlpoke: {
            bump: {
                options: {
                    xpath: '/addon/@version',
                    value: '<%= pkg.version %>'
                },
                files: {
                    'script.imdbupdate/addon.xml': 'script.imdbupdate/addon.xml'
                },
            },
        },
        bump: {
            options: {
                files: ['package.json'],
                updateConfigs: ['pkg'],
                commit: false,
                createTag: false,
                push: false
            }
        }
    })

    grunt.registerTask('build', ['bump', 'xmlpoke', 'compress'])
}