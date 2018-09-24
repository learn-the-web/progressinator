module.exports = {
  plugins: [
    require('postcss-import')(),
    require('postcss-assets')(),
    require('postcss-cssnext')({
      browsers: 'last 2 versions',
    }),
    require('cssnano')({
      safe: true,
    }),
  ],
}
