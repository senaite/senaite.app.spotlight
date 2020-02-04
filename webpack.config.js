const path = require("path");
const webpack = require("webpack");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;


module.exports = {
  entry: {
    spotlight: path.resolve(__dirname, "./src/senaite/core/spotlight/static/src/spotlight.coffee")
  },
  output: {
    filename: "senaite.core.[name].js",
    path: path.resolve(__dirname, "./src/senaite/core/spotlight/static/js")
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
    // use underscore directly in code
    // new webpack.ProvidePlugin({
    //   underscore: "lodash"
    // }),
    new BundleAnalyzerPlugin()
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    // use jQuery from the outer scope
    jquery: "jQuery",
    bootstrap: "bootstrap",
    jsi18n: {
      root: "_"
    }
  }
};
