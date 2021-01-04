const path = require("path");
const webpack = require("webpack");

const TerserPlugin = require("terser-webpack-plugin");

const devMode = process.env.mode == "development";
const prodMode = process.env.mode == "production";
const mode = process.env.mode;
console.log(`RUNNING WEBPACK IN '${mode}' MODE`);

module.exports = {
  // https://webpack.js.org/configuration/mode/#usage
  mode: mode,
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
  optimization: {
    minimize: prodMode,
    minimizer: [
      // https://v4.webpack.js.org/plugins/terser-webpack-plugin/
      new TerserPlugin({
        exclude: /\/modules/,
        terserOptions: {
          // https://github.com/webpack-contrib/terser-webpack-plugin#terseroptions
          sourceMap: false, // Must be set to true if using source-maps in production
          format: {
            comments: false
          },
          compress: {
            drop_console: true,
            passes: 2,
          },
	      }
      }),
    ],
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
