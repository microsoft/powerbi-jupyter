module.exports = function (config) {
  config.set({
    basePath: '..',
    frameworks: ['mocha', 'karma-typescript'],
    reporters: ['mocha', 'karma-typescript'],
    client: {
      mocha: {
        timeout : 10000, // 10 seconds - upped from 2 seconds
        retries: 3 // Allow for slow server on CI.
      }
    },
    files: [
      { pattern: "tests/src/**/*.ts" },
      { pattern: "src/**/*.ts" },
    ],
    exclude: [
      "src/extension.ts",
    ],
    preprocessors: {
      '**/*.ts': ['karma-typescript']
    },
    browserNoActivityTimeout: 31000, // 31 seconds - upped from 10 seconds
    port: 9876,
    colors: true,
    singleRun: true,
    logLevel: config.LOG_INFO,


    karmaTypescriptConfig: {
      tsconfig: 'tests/tsconfig.json',
      reports: {
        "text-summary": "",
        "html": "coverage",
        "lcovonly": {
          "directory": "coverage",
          "filename": "coverage.lcov"
        }
      },
      bundlerOptions: {
        transforms: [
            require("karma-typescript-es6-transform")()
        ]
      }
    }
  });
};
