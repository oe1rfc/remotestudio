/// <reference types="node" />
import { Commands } from '..';
import { ISerializableCommand } from '../commands/CommandBase';
import DataTransfer from './dataTransfer';
export declare class DataTransferManager {
    private readonly commandQueue;
    private readonly stillsLock;
    private readonly clipLocks;
    private interval?;
    private exitUnsubscribe?;
    private transferIndex;
    startCommandSending(sendCommands: (cmds: ISerializableCommand[]) => Array<Promise<void>>): void;
    stopCommandSending(): void;
    handleCommand(command: Commands.IDeserializedCommand): void;
    uploadStill(index: number, data: Buffer, name: string, description: string): Promise<DataTransfer>;
    uploadClip(index: number, data: Array<Buffer>, name: string): Promise<DataTransfer>;
    uploadAudio(index: number, data: Buffer, name: string): Promise<DataTransfer>;
    private readonly nextTransferIndex;
    private getClipLock;
}
