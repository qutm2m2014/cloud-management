var gulp = require('gulp');
var usemin = require('gulp-usemin');
var minifyHtml = require('gulp-minify-html');
var minifyCss = require('gulp-minify-css');
var rev = require('gulp-rev');
var sass = require('gulp-ruby-sass');
var prefixer = require('gulp-autoprefixer');
var duration = require('gulp-duration');

gulp.task('usemin', function(){
    gulp.src('./index.html')
        .pipe(usemin({
            css: [minifyCss(), 'concat'],
            html: [minifyHtml({empty: true})],
            js: [rev()]
        }))
        .pipe(gulp.dest('dist/'))
});

gulp.task('sass', function(){
    gulp.src('scss/style.scss')
        .pipe(sass({
            loadPath:['./libs/','./libs/foundation/scss'],
            sourcemap:true})
        ).pipe(gulp.dest('css'))
});

gulp.task('watch', function(){
    gulp.watch('scss/**/*.scss', ['sass'])
});
