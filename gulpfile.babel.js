'use strict';

// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import gulp from 'gulp';
import del from 'del';
import browserSync from 'browser-sync';
import gulpLoadPlugins from 'gulp-load-plugins';

// this gonna load all our gulp plugins
const $ = gulpLoadPlugins();
const reload = browserSync.reload;

// Copy all root level files and folders from /app
gulp.task('copy', () => {
  const size = $.size({title: 'copy'});
  return gulp.src([
    'app/*',
    '!app/*.html'
  ])
  .pipe(gulp.dest('dist'))
  .pipe(size);
});

// Clean all output files
gulp.task('clean', () =>
  del(['.tmp', 'dist/*', '!dist/.git'], {dot: true})
);

// Optimize images
gulp.task('images', () =>
  gulp.src('app/images/**/*')
    .pipe($.cache($.imagemin({
      progressive: true,
      interlaced: true
    })))
    .pipe(gulp.dest('dist/images'))
    .pipe($.size({title: 'images'}))
);

// Copying fonts to dist
gulp.task('fonts', function() {
  return gulp.src('app/fonts/**/*')
  .pipe(gulp.dest('dist/fonts'))
})

// Lint Javascript
gulp.task('eslint', () =>
  gulp.src(['app/scripts/**/*.js', '!node_modules/**'])
  .pipe($.eslint({'useEslintrc':true}))
  .pipe($.eslint.format())
  .pipe($.eslint.failAfterError())
);

// Concatenate and minify JavaScript. Optionally transpiles ES2015 code to ES5.
// to enable ES2015 support remove the line `"only": "gulpfile.babel.js",` in the
// `.babelrc` file.
gulp.task('scripts', () =>
    gulp.src([
      // Note: Since we are not using useref in the scripts build pipeline,
      //       you need to explicitly list your scripts here in the right order
      //       to be correctly concatenated
      'app/scripts/main.js'
      // Other scripts
    ])
      .pipe($.newer('.tmp/scripts'))
      .pipe($.sourcemaps.init())
      .pipe($.babel())
      .pipe($.sourcemaps.write())
      .pipe(gulp.dest('.tmp/scripts'))
      .pipe($.concat('main.min.js'))
      .pipe($.uglify())
      // Output files
      .pipe($.size({title: 'scripts'}))
      .pipe($.sourcemaps.write('.'))
      .pipe(gulp.dest('dist/scripts'))
      .pipe(gulp.dest('.tmp/scripts'))
);

// Compile and automatically prefix stylesheets
gulp.task('styles', () => {
  const AUTOPREFIXER_BROWSERS = [
    'ie >= 10',
    'ie_mob >= 10',
    'ff >= 30',
    'chrome >= 34',
    'safari >= 7',
    'opera >= 23',
    'ios >= 7',
    'android >= 4.4',
    'bb >= 10'
  ];

  // For best performance, don't add Sass partials to `gulp.src`
  return gulp.src([
    'app/styles/**/*.sass',
    'app/styles/**/*.scss',
    'app/styles/**/*.css',
    // 'node_modules/bulma/bulma.sass',
  ])
  .pipe($.newer('.tmp/styles'))
  .pipe($.sourcemaps.init())
  .pipe($.sass({
    precision: 10
  }).on('error', $.sass.logError))
  .pipe($.autoprefixer(AUTOPREFIXER_BROWSERS))
  .pipe(gulp.dest('.tmp/styles'))
  // Concatenate and minify styles
  .pipe($.if('*.css', $.cssnano()))
  .pipe($.size({title: 'styles'}))
  .pipe(gulp.dest('dist/styles'))
  .pipe($.sourcemaps.write('./'))
  .pipe(gulp.dest('.tmp/styles'));
});


// Watch files for changes & reload
// Serve for testing frontend
gulp.task('serve', ['scripts', 'styles'], () => {
  browserSync({
    notify: false,
    // Customize the Browsersync console logging prefix
    logPrefix: 'WIKI',
    // Run as an https by uncommenting 'https: true'
    // Note: this uses an unsigned certificate which on first access
    //       will present a certificate warning in the browser.
    // https: true,
    server: ['.tmp', 'app'],
    port: 3000
  });

  gulp.watch(['app/**/*.html'], reload);
  gulp.watch(['app/styles/**/*.{sass,scss,css}'], ['styles', reload]);
  gulp.watch(['app/scripts/**/*.js'], ['lint', 'scripts', reload]);
  gulp.watch(['app/images/**/*'], reload);
});


// // Build and serve the output from the dist build
// gulp.task('serve:dist', ['default'], () =>
//   browserSync({
//     notify: false,
//     logPrefix: 'WSK',
//     // Allow scroll syncing across breakpoints
//     scrollElementMapping: ['main', '.mdl-layout'],
//     // Run as an https by uncommenting 'https: true'
//     // Note: this uses an unsigned certificate which on first access
//     //       will present a certificate warning in the browser.
//     // https: true,
//     server: 'dist',
//     port: 3001
//   })
// );

// // Build production files, the default task
// gulp.task('default', ['clean'], cb =>
//   runSequence(
//     'styles',
//     ['lint', 'html', 'scripts', 'images', 'copy'],
//     'generate-service-worker',
//     cb
//   )
// );
