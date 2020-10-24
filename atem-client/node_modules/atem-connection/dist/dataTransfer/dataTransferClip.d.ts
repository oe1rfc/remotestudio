import { Commands } from '..';
import DataTransfer from './dataTransfer';
import DataTransferFrame from './dataTransferFrame';
export default class DataTransferClip extends DataTransfer {
    readonly clipIndex: number;
    readonly frames: Array<DataTransferFrame>;
    readonly name: string;
    curFrame: number;
    constructor(clipIndex: number, name: string, frames: Array<DataTransferFrame>);
    start(): Commands.ISerializableCommand[];
    handleCommand(command: Commands.IDeserializedCommand): Commands.ISerializableCommand[];
    readonly transferId: number;
    gotLock(): Commands.ISerializableCommand[];
}
