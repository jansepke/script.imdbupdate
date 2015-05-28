var path = require('path')
loadTasks = require('load-grunt-tasks')

module.exports = function(grunt) {
    loadTasks(grunt)

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
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
                    cwd: 'addon',
                    src: ['**'],
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
                    'addon/addon.xml': 'addon/addon.xml'
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
        },
        changelog: {
            options: {
                from: 'db8de4f7c0788454a86dab8a1f335a9d20363118'
            }
        }
    })

    grunt.registerTask('build', ['bump', 'xmlpoke', 'compress']);
}