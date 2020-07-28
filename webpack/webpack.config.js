const path = require("path");
const webpack = require("webpack");
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  context: path.resolve(__dirname, "app"),
  entry: {
    spotlight: "./spotlight.coffee"
  },
  output: {
    filename: "senaite.app.spotlight.js",
    path: path.resolve(__dirname, "../src/senaite/app/spotlight/static/js")
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: ["babel-loader", "coffee-loader"]
      }, {
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: ["babel-loader"]
      }, {
        test: /\.(css|scss|sass)$/,
        exclude: [/node_modules/],
        use: ["style-loader", "css-loader", "sass-loader"]
      }
    ]
  },
  plugins: [
    // e.g. https://webpack.js.org/plugins/provide-plugin/
    // new BundleAnalyzerPlugin()
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    // use jQuery from the outer scope
    jquery: "jQuery",
    bootstrap: "bootstrap"
  }
};
