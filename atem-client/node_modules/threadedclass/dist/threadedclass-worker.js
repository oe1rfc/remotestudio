"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const internalApi_1 = require("./internalApi");
const lib_1 = require("./lib");
const WorkerThreads = lib_1.getWorkerThreads();
/* This file is the one that is launched in the worker child process */
function send(message) {
    if (WorkerThreads) {
        if (WorkerThreads.parentPort) {
            WorkerThreads.parentPort.postMessage(message);
        }
        else {
            throw Error('WorkerThreads.parentPort not set!');
        }
    }
    else if (process.send) {
        process.send(message);
        // @ts-ignore global postMessage
    }
    else if (postMessage) {
        // @ts-ignore
        postMessage(message);
    }
    else
        throw Error('process.send and postMessage are undefined!');
}
class ThreadedWorker extends internalApi_1.Worker {
    constructor() {
        super(...arguments);
        this.instanceHandles = {};
    }
    sendMessageToParent(handle, msg, cb) {
        if (msg.cmd === internalApi_1.MessageType.LOG) {
            const message = Object.assign(Object.assign({}, msg), {
                cmdId: 0,
                instanceId: ''
            });
            send(message);
        }
        else {
            const message = Object.assign(Object.assign({}, msg), {
                cmdId: handle.cmdId++,
                instanceId: handle.id
            });
            if (cb)
                handle.queue[message.cmdId + ''] = cb;
            send(message);
        }
    }
    killInstance(handle) {
        delete this.instanceHandles[handle.id];
    }
}
// const _orgConsoleLog = console.log
if (lib_1.isBrowser()) {
    const worker = new ThreadedWorker();
    // console.log = worker.log
    // @ts-ignore global onmessage
    onmessage = (m) => {
        // Received message from parent
        if (m.type === 'message') {
            worker.onMessageFromParent(m.data);
        }
        else {
            console.log('child process: onMessage', m);
        }
    };
}
else if (lib_1.nodeSupportsWorkerThreads()) {
    if (WorkerThreads) {
        const worker = new ThreadedWorker();
        console.log = worker.log;
        console.error = worker.logError;
        if (WorkerThreads.parentPort) {
            WorkerThreads.parentPort.on('message', (m) => {
                // Received message from parent
                worker.onMessageFromParent(m);
            });
        }
        else {
            throw Error('WorkerThreads.parentPort not set!');
        }
    }
    else {
        throw Error('WorkerThreads not available!');
    }
}
else if (process.send) {
    const worker = new ThreadedWorker();
    console.log = worker.log;
    console.error = worker.logError;
    process.on('message', (m) => {
        // Received message from parent
        worker.onMessageFromParent(m);
    });
}
else {
    throw Error('process.send and onmessage are undefined!');
}
//# sourceMappingURL=threadedclass-worker.js.map