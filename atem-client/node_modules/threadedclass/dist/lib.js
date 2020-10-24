"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Returns true if running in th browser (if not, then we're in NodeJS)
 */
function isBrowser() {
    return !(process && process.hasOwnProperty('stdin'));
}
exports.isBrowser = isBrowser;
function browserSupportsWebWorkers() {
    // @ts-ignore
    return !!(isBrowser() && window.Worker);
}
exports.browserSupportsWebWorkers = browserSupportsWebWorkers;
function nodeSupportsWorkerThreads() {
    const workerThreads = getWorkerThreads();
    return !!workerThreads;
}
exports.nodeSupportsWorkerThreads = nodeSupportsWorkerThreads;
function getWorkerThreads() {
    try {
        const workerThreads = require('worker_threads');
        return workerThreads;
    }
    catch (e) {
        return null;
    }
}
exports.getWorkerThreads = getWorkerThreads;
//# sourceMappingURL=lib.js.map