/// <reference types="node" />
import { Commands } from '..';
import DataTransferFrame from './dataTransferFrame';
export default class DataTransferStill extends DataTransferFrame {
    private readonly name;
    private readonly description;
    constructor(transferId: number, frameId: number, data: Buffer, name: string, description: string);
    sendDescription(): Commands.ISerializableCommand;
}
