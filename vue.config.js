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
};
