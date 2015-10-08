var gulp = require('gulp'),
  zip = require('gulp-zip'),
  util = require('util'),
  runSequence = require('run-sequence'),
  bump = require('gulp-bump'),
  cheerio = require('gulp-cheerio'),
  release = require('gulp-github-release'),
  git = require('gulp-git');

gulp.task('compress', function () {
  var pkg = require('./package.json');
  var fileName = util.format('script.imdbupdate-%s.zip', pkg.version);

  return gulp.src('script.imdbupdate/**', { base: __dirname })
    .pipe(zip(fileName))
    .pipe(gulp.dest('build'));
});

gulp.task('bump', function () {
  return gulp.src('./package.json')
    .pipe(bump())
    .pipe(gulp.dest('./'));
});

gulp.task('xml', function () {
  var pkg = require('./package.json');

  return gulp
    .src(['script.imdbupdate/addon.xml'])
    .pipe(cheerio({
      run: function ($, file) {
        $('addon').attr('version', pkg.version);
      },
      parserOptions: {
        xmlMode: true
      }
    }))
    .pipe(gulp.dest('script.imdbupdate'));
});

gulp.task('build', function (callback) {
  runSequence('bump', 'xml', 'compress', callback);
});

gulp.task('github-release', function () {
  var pkg = require('./package.json');
  var fileName = util.format('script.imdbupdate-%s.zip', pkg.version);

  return gulp.src('build/' + fileName)
    .pipe(release({
      owner: 'Jandalf',
      repo: 'script.imdbupdate',
      manifest: pkg
    }));
});

gulp.task('release', function (callback) {
  runSequence('build', 'commit', 'push', 'github-release', callback);
});

gulp.task('commit', function () {
  var pkg = require('./package.json');

  return gulp.src(['./package.json', 'script.imdbupdate/addon.xml'])
    .pipe(git.commit('chore: release version ' + pkg.version));
});

gulp.task('push', function () {
  git.push('origin', 'master', function (err) {
    if (err) throw err;
  });
});