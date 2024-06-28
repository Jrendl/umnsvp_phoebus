const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
module.exports = {
    entry: './src/app.js',
    mode: "development",
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: 'src/index.html',
            filename: 'index.html',
        })
    ],
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    externals: {
        openmct: "openmct",
    },
    devServer: {
        static: [{
            // eslint-disable-next-line no-undef
            directory: path.join(__dirname, '/node_modules/openmct/dist'),
            publicPath: '/node_modules/openmct/dist'
        }]
    },
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
    },
};