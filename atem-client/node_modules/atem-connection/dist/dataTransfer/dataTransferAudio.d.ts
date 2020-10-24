/// <reference types="node" />
import { Commands } from '..';
import DataTransferFrame from './dataTransferFrame';
export default class DataTransferAudio extends DataTransferFrame {
    readonly name: string;
    constructor(transferId: number, storeId: number, data: Buffer, name: string);
    start(): Commands.ISerializableCommand[];
    sendDescription(): Commands.ISerializableCommand;
}
