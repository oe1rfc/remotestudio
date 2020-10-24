/// <reference types="node" />
import { Commands } from '..';
import DataTransfer from './dataTransfer';
export default class DataTransferFrame extends DataTransfer {
    readonly frameId: number;
    readonly hash: string;
    readonly data: Buffer;
    private _sent;
    constructor(transferId: number, storeId: number, frameId: number, data: Buffer);
    start(): Commands.ISerializableCommand[];
    sendDescription(): Commands.ISerializableCommand;
    handleCommand(command: Commands.IDeserializedCommand): Commands.ISerializableCommand[];
    gotLock(): Commands.ISerializableCommand[];
    private queueCommand;
}
