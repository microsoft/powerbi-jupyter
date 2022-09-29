// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
let path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        index: path.resolve('tests/src/index.spec.ts'),
        utilsTest: path.resolve('tests/src/utils.spec.ts'),
    },
    output: {
        path: path.resolve('compiledTests'),
        filename: '[name].spec.js'
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.ts(x)?$/,
                loader: 'ts-loader',
                options: {
                    configFile: path.resolve('tests/tsconfig.json')
                },
                exclude: /node_modules/
            },
        ]
    },
    resolve: {
        extensions: [
            '.ts',
            '.js'
        ]
    },
};