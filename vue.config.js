// eslint-disable-next-line @typescript-eslint/no-var-requires
const SpeedMeasurePlugin = require("speed-measure-webpack-plugin");
const smp = new SpeedMeasurePlugin();

module.exports = {
  devServer: {
    proxy: {
      "^/api/": {
        target: "http://localhost:8888",
        ws: true,
        changeOrigin: true,
      },
    },
    watchOptions: {
      ignored: ["/node_modules/"],
      aggregateTimeout: 300,
      poll: 300,
    },
  },
  configureWebpack: smp.wrap({}),
};
